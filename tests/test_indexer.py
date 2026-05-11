from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.indexer import SkillIndexer


class FakeClient:
    def __init__(self) -> None:
        self.records = []

    def upsert(self, records):
        self.records.extend(records)


class ConfiguredPathsIndexer(SkillIndexer):
    def __init__(self, paths):
        self.config = SimpleNamespace(
            skills=SimpleNamespace(paths=paths),
            embeddings=SimpleNamespace(model="test-model"),
        )
        self.client = FakeClient()

    def embed_batch(self, texts):
        return [[float(index)] for index, _ in enumerate(texts)]


class SkillIndexerTests(unittest.TestCase):
    def test_sync_uses_each_configured_skill_path(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_skill = Path(first) / "alpha" / "SKILL.md"
            second_skill = Path(second) / "beta" / "SKILL.md"
            first_skill.parent.mkdir()
            second_skill.parent.mkdir()
            first_skill.write_text("---\nname: alpha\n---\nAlpha overview\n", encoding="utf-8")
            second_skill.write_text("---\nname: beta\n---\nBeta overview\n", encoding="utf-8")

            indexer = ConfiguredPathsIndexer([first, second, first])
            result = indexer.sync()

        skill_names = {record[2]["skill_name"] for record in indexer.client.records}
        self.assertEqual(result, {"indexed": 2})
        self.assertEqual(skill_names, {"alpha", "beta"})

    def test_configured_skill_paths_skips_missing_directories(self):
        with tempfile.TemporaryDirectory() as existing:
            indexer = ConfiguredPathsIndexer([existing, str(Path(existing) / "missing")])
            self.assertEqual(list(indexer.configured_skill_paths()), [str(Path(existing).resolve())])


if __name__ == "__main__":
    unittest.main()
