import pinecone
import os
from .util import parse_skill_file, compute_sha256


class SkillIndexer:
    def __init__(self, config):
        self.config = config
        pinecone.init(api_key=config.pinecone.api_key, environment=config.pinecone.environment)
        self.index = pinecone.Index(config.pinecone.index_name)

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

    def sync(self):
        records = []

        for path in self.scan(os.path.expanduser("~/.hermes/skills")):
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
            self.index.upsert(records)

        return {"indexed": len(records)}
