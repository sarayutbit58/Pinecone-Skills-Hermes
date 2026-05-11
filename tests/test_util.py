from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.util import parse_skill_file


class UtilTests(unittest.TestCase):
    def test_parse_skill_file_splits_markdown_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_file = Path(tmp) / "SKILL.md"
            skill_file.write_text(
                "---\nname: sample\n---\nOverview text\n## When To Use\nUse it here\n### Examples\nExample text\n",
                encoding="utf-8",
            )

            parsed = parse_skill_file(str(skill_file))

        self.assertEqual(parsed["metadata"], {"name": "sample"})
        self.assertIn("Overview text", parsed["sections"]["overview"])
        self.assertIn("Use it here", parsed["sections"]["when_to_use"])
        self.assertIn("Example text", parsed["sections"]["examples"])


if __name__ == "__main__":
    unittest.main()
