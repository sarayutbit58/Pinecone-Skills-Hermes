import tempfile
import unittest
from pathlib import Path

from src.cache import JsonCache
from src.config import load_config
from src.feedback import SkillFeedbackStore
from src.router import SkillRouter


class DummyClient:
    def __init__(self, score):
        self.score = score

    def query(self, vector, top_k, include_metadata=True):
        return {
            "matches": [
                {
                    "score": self.score,
                    "metadata": {"skill_name": "pdf", "section": "overview"},
                }
            ]
        }


class SkillRouterTests(unittest.TestCase):
    def build_router(self, score, cache_path, feedback_path):
        config = load_config({"routing": {"auto_load_threshold": 0.84, "suggest_threshold": 0.74}})
        router = object.__new__(SkillRouter)
        router.config = config
        router.client = DummyClient(score)
        router.cache = JsonCache(str(cache_path), ttl_seconds=3600)
        router.feedback = SkillFeedbackStore(str(feedback_path))
        router.embed = lambda query: [0.1, 0.2, 0.3]
        return router

    def test_search_returns_mode_from_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            auto = self.build_router(0.90, root / "auto.json", root / "feedback-auto.json").search("summarize pdf")
            suggest = self.build_router(0.78, root / "suggest.json", root / "feedback-suggest.json").search("summarize pdf")
            none = self.build_router(0.50, root / "none.json", root / "feedback-none.json").search("summarize pdf")

            self.assertEqual(auto["mode"], "auto_load")
            self.assertEqual(suggest["mode"], "suggest")
            self.assertEqual(none, {"mode": "none", "skills": []})


if __name__ == "__main__":
    unittest.main()
