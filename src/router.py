from __future__ import annotations

import os
from typing import Any

from .pinecone_client import build_pinecone_client
from .policies import is_allowed


class SkillRouter:
    def __init__(self, config: Any) -> None:
        self.config = config
        self.client = build_pinecone_client(config)

    def embed(self, text: str) -> list[float]:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.Embedding.create(input=[text], model=self.config.embeddings.model)
        return res["data"][0]["embedding"]

    def search(self, query: str):
        vec = self.embed(query)
        res = self.client.query(vector=vec, top_k=self.config.routing.top_k, include_metadata=True)

        candidates = {}

        for m in res.get("matches", []):
            meta = m.get("metadata", {})
            name = meta.get("skill_name")
            score = m.get("score", 0.0)

            if not name:
                continue

            if name not in candidates or candidates[name]["score"] < score:
                candidates[name] = {
                    "name": name,
                    "score": score,
                    "meta": meta,
                }

        filtered = [c for c in candidates.values() if is_allowed(c["meta"], self.config)]
        filtered.sort(key=lambda x: x["score"], reverse=True)

        if not filtered:
            return {"mode": "none", "skills": []}

        top = filtered[0]["score"]

        if top >= self.config.routing.auto_load_threshold:
            return {"mode": "auto_load", "skills": filtered[:2]}
        elif top >= self.config.routing.suggest_threshold:
            return {"mode": "suggest", "skills": filtered[:3]}

        return {"mode": "none", "skills": []}
