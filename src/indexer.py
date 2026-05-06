from __future__ import annotations

import os
from typing import Any, Iterable

from .pinecone_client import build_pinecone_client
from .util import parse_skill_file


INDEXED_SECTIONS = {"overview", "when_to_use", "examples", "procedure"}


class SkillIndexer:
    def __init__(self, config: Any) -> None:
        self.config = config
        self.client = build_pinecone_client(config)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.Embedding.create(input=texts, model=self.config.embeddings.model)
        return [d["embedding"] for d in res["data"]]

    def configured_skill_paths(self) -> Iterable[str]:
        seen: set[str] = set()
        for raw_path in getattr(self.config.skills, "paths", ["~/.hermes/skills"]):
            path = os.path.abspath(os.path.expanduser(raw_path))
            if path not in seen:
                seen.add(path)
                yield path

    def scan(self, base_path: str) -> Iterable[str]:
        for root, _, files in os.walk(base_path):
            for f in files:
                if f.lower() == "skill.md":
                    yield os.path.join(root, f)

    def sync(self) -> dict[str, int]:
        records = []

        for base_path in self.configured_skill_paths():
            for path in self.scan(base_path):
                parsed = parse_skill_file(path)
                meta = parsed["metadata"]
                sections = parsed["sections"]

                skill_name = meta.get("name", os.path.basename(os.path.dirname(path)))

                texts = []
                metas = []

                for section, text in sections.items():
                    if section in INDEXED_SECTIONS and text.strip():
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
