from __future__ import annotations

import os
from typing import Any

from .cache import JsonCache, stable_hash
from .feedback import SkillFeedbackStore
from .pinecone_client import build_pinecone_client
from .policies import is_allowed


class SkillRouter:
    def __init__(self, config: Any) -> None:
        self.config = config
        self.client = build_pinecone_client(config)
        self.cache = JsonCache("~/.hermes/cache/router.json", ttl_seconds=3600)
        self.feedback = SkillFeedbackStore()

    def embed(self, text: str) -> list[float]:
        key = f"emb:{stable_hash(text)}"
        cached = self.cache.get(key)
        if cached:
            return cached

        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.Embedding.create(input=[text], model=self.config.embeddings.model)
        vec = res["data"][0]["embedding"]
        self.cache.set(key, vec)
        return vec

    def record_feedback(self, skill_name: str, success: bool, query: str | None = None, note: str | None = None):
        # Feedback changes ranking. Clear cached search results so learning applies next time.
        stats = self.feedback.record(skill_name=skill_name, success=success, query=query, note=note)
        self.cache.delete_prefix("search:")
        return stats

    def search(self, query: str):
        cache_key = f"search:{stable_hash(query)}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        vec = self.embed(query)
        res = self.client.query(vector=vec, top_k=self.config.routing.top_k, include_metadata=True)

        candidates = {}

        for m in res.get("matches", []):
            meta = m.get("metadata", {})
            name = meta.get("skill_name")
            score = m.get("score", 0.0)

            if not name:
                continue

            adjusted_score = self.feedback.adjust_score(name, score)

            if name not in candidates or candidates[name]["score"] < adjusted_score:
                candidates[name] = {
                    "name": name,
                    "score": adjusted_score,
                    "base_score": score,
                    "meta": meta,
                }

        filtered = [c for c in candidates.values() if is_allowed(c["meta"], self.config)]
        filtered.sort(key=lambda x: x["score"], reverse=True)

        if not filtered:
            result = {"mode": "none", "skills": []}
            self.cache.set(cache_key, result)
            return result

        top = filtered[0]["score"]

        if top >= self.config.routing.auto_load_threshold:
            result = {"mode": "auto_load", "skills": filtered[:2]}
        elif top >= self.config.routing.suggest_threshold:
            result = {"mode": "suggest", "skills": filtered[:3]}
        else:
            result = {"mode": "none", "skills": []}

        self.cache.set(cache_key, result)
        return result
