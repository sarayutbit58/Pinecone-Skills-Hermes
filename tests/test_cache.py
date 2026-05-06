import tempfile
import unittest
from pathlib import Path

from src.cache import JsonCache


class JsonCacheTests(unittest.TestCase):
    def test_delete_prefix_removes_matching_keys_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cache.json"
            cache = JsonCache(str(path))
            cache.set("search:one", 1)
            cache.set("emb:one", 2)

            cache.delete_prefix("search:")

            reloaded = JsonCache(str(path))
            self.assertIsNone(reloaded.get("search:one"))
            self.assertEqual(reloaded.get("emb:one"), 2)


if __name__ == "__main__":
    unittest.main()
