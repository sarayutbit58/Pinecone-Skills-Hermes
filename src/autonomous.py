from __future__ import annotations

from typing import Any, Dict


class AutonomousSkillAgent:
    """Lightweight autonomous layer.

    This is NOT a full planner. It injects a pre-routing step so Hermes always
    attempts semantic skill selection before solving a task.
    """

    def __init__(self, router) -> None:
        self.router = router

    def route(self, user_input: str) -> Dict[str, Any]:
        return self.router.search(user_input)

    def enrich_prompt(self, user_input: str) -> str:
        routing = self.route(user_input)

        if routing.get("mode") == "none":
            return user_input

        skills = routing.get("skills", [])
        skill_names = [s.get("name") for s in skills if s.get("name")]

        if not skill_names:
            return user_input

        return "\n".join([
            "[Auto-selected skills]",
            ", ".join(skill_names),
            "",
            "Use these skills if relevant to solve the task.",
            "",
            "User task:",
            user_input,
        ])
