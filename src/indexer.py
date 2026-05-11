from __future__ import annotations

import os
from typing import Any, Iterable

from .pinecone_client import build_pinecone_client
from .util import parse_skill_file


class SkillIndexer:
    def __init__(self, config: Any) -> None:
        self.config = config
        self.client = build_pinecone_client(config)

    def embed_batch(self, texts):
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.Embedding.create(input=texts, model=self.config.embeddings.model)
        return [d["embedding"] for d in res["data"]]

    def scan(self, base_path):
        for root, _, files in os.walk(base_path):
            for f in files:
                if f.lower() == "skill.md":
                    yield os.path.join(root, f)

    def configured_skill_paths(self) -> Iterable[str]:
        seen = set()
        for path in getattr(self.config.skills, "paths", ["~/.hermes/skills"]):
            expanded = os.path.abspath(os.path.expanduser(path))
            if expanded in seen or not os.path.isdir(expanded):
                continue
            seen.add(expanded)
            yield expanded

    def sync(self):
        records = []

        for skill_root in self.configured_skill_paths():
            for path in self.scan(skill_root):
                parsed = parse_skill_file(path)
                meta = parsed["metadata"]
                sections = parsed["sections"]

                skill_name = meta.get("name", os.path.basename(os.path.dirname(path)))

                texts = []
                metas = []

                for section, text in sections.items():
                    if section in ["overview", "when_to_use", "examples", "procedure"]:
                        texts.append(text)
                        metas.append({
                            "skill_name": skill_name,
                            "section": section,
                            "path": path,
                        })

                if not texts:
                    continue

                embeddings = self.embed_batch(texts)

                for emb, m in zip(embeddings, metas):
                    records.append((f"{skill_name}:{m['section']}", emb, m))

        if records:
            self.client.upsert(records)

        return {"indexed": len(records)}
