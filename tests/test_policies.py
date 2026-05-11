from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.policies import is_allowed


def config(**overrides):
    safety = SimpleNamespace(
        allow_community_skills=False,
        require_platform_match=False,
        require_toolset_match=True,
        required_toolsets=[],
        blocked_capabilities=["credential_access"],
    )
    for key, value in overrides.items():
        setattr(safety, key, value)
    return SimpleNamespace(safety=safety)


class PolicyTests(unittest.TestCase):
    def test_require_toolset_match_allows_skill_with_required_toolsets(self):
        meta = {"toolsets": ["pinecone", "openai"]}
        self.assertTrue(is_allowed(meta, config(required_toolsets=["pinecone"])))

    def test_require_toolset_match_blocks_skill_without_required_toolsets(self):
        meta = {"toolsets": ["openai"]}
        self.assertFalse(is_allowed(meta, config(required_toolsets=["pinecone"])))

    def test_require_toolset_match_is_noop_without_required_toolsets(self):
        meta = {"toolsets": []}
        self.assertTrue(is_allowed(meta, config(required_toolsets=[])))


if __name__ == "__main__":
    unittest.main()
