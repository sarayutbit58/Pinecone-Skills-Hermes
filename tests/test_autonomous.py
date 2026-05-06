import unittest

from src.autonomous import AutonomousSkillAgent


class DummyRouter:
    def search(self, user_input):
        return {"mode": "auto_load", "skills": [{"name": "pdf"}, {"name": "excel"}]}


class AutonomousSkillAgentTests(unittest.TestCase):
    def test_enrich_prompt_has_no_leading_blank_line(self):
        prompt = AutonomousSkillAgent(DummyRouter()).enrich_prompt("Summarize the report")

        self.assertTrue(prompt.startswith("[Auto-selected skills]"))
        self.assertIn("pdf, excel", prompt)
        self.assertTrue(prompt.endswith("Summarize the report"))


if __name__ == "__main__":
    unittest.main()
