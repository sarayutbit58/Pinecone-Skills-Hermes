import tempfile
import unittest
from pathlib import Path

from src.config import load_config
from src.indexer import SkillIndexer


class DummyClient:
    def __init__(self):
        self.records = []

    def upsert(self, records):
        self.records.extend(records)


class SkillIndexerTests(unittest.TestCase):
    def test_sync_indexes_all_configured_skill_paths_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first" / "alpha"
            second = root / "second" / "beta"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "SKILL.md").write_text(
                "---\nname: alpha\n---\nAlpha overview\n## When To Use\nUse alpha.\n",
                encoding="utf-8",
            )
            (second / "SKILL.md").write_text(
                "---\nname: beta\n---\nBeta overview\n## Examples\nUse beta.\n",
                encoding="utf-8",
            )

            config = load_config({"skills": {"paths": [str(root / "first"), str(root / "second"), str(root / "first")]}})
            indexer = object.__new__(SkillIndexer)
            indexer.config = config
            indexer.client = DummyClient()
            indexer.embed_batch = lambda texts: [[float(i)] for i, _ in enumerate(texts, start=1)]

            result = indexer.sync()

            self.assertEqual(result, {"indexed": 4})
            vector_ids = [record[0] for record in indexer.client.records]
            self.assertEqual(vector_ids.count("alpha:overview"), 1)
            self.assertEqual(vector_ids.count("alpha:when_to_use"), 1)
            self.assertEqual(vector_ids.count("beta:overview"), 1)
            self.assertEqual(vector_ids.count("beta:examples"), 1)


if __name__ == "__main__":
    unittest.main()
