import unittest
from unittest.mock import patch

from src.config import load_config
from src.policies import is_allowed


class PolicyTests(unittest.TestCase):
    def test_blocks_when_required_toolset_does_not_match(self):
        config = load_config({"safety": {"required_toolsets": ["python"]}})

        self.assertFalse(is_allowed({"toolsets": ["node"]}, config))

    def test_allows_when_required_toolset_matches(self):
        config = load_config({"safety": {"required_toolsets": ["python"]}})

        self.assertTrue(is_allowed({"toolsets": ["python", "shell"]}, config))

    @patch("src.policies.current_platform", return_value="linux")
    def test_platform_metadata_accepts_string_or_list(self, _):
        config = load_config({})

        self.assertTrue(is_allowed({"platforms": "linux"}, config))
        self.assertFalse(is_allowed({"platforms": ["windows"]}, config))


if __name__ == "__main__":
    unittest.main()
