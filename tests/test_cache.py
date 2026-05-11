from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.cache import JsonCache


class JsonCacheTests(unittest.TestCase):
    def test_delete_prefix_removes_matching_keys_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "cache.json"
            cache = JsonCache(str(cache_path))
            cache.set("search:a", {"mode": "none"})
            cache.set("search:b", {"mode": "suggest"})
            cache.set("emb:a", [1.0])

            deleted = cache.delete_prefix("search:")
            reloaded = JsonCache(str(cache_path))

        self.assertEqual(deleted, 2)
        self.assertIsNone(reloaded.get("search:a"))
        self.assertIsNone(reloaded.get("search:b"))
        self.assertEqual(reloaded.get("emb:a"), [1.0])


if __name__ == "__main__":
    unittest.main()
