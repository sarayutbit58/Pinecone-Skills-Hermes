import pinecone
import os
from .policies import is_allowed


class SkillRouter:
    def __init__(self, config):
        self.config = config
        pinecone.init(api_key=config.pinecone.api_key, environment=config.pinecone.environment)
        self.index = pinecone.Index(config.pinecone.index_name)

    def embed(self, text):
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.Embedding.create(input=[text], model=self.config.embeddings.model)
        return res["data"][0]["embedding"]

    def search(self, query):
        vec = self.embed(query)
        res = self.index.query(vector=vec, top_k=self.config.routing.top_k, include_metadata=True)

        candidates = {}

        for m in res["matches"]:
            meta = m["metadata"]
            name = meta.get("skill_name")
            score = m["score"]

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
