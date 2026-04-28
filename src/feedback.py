from __future__ import annotations

from typing import Any

from .cache import JsonCache, stable_hash


class SkillFeedbackStore:
    """Local feedback store for self-learning skill ranking.

    This intentionally uses a local JSON cache first so Free Tier usage stays low.
    The system learns from success/failure signals without writing telemetry to
    Pinecone on every request.
    """

    def __init__(self, path: str = "~/.hermes/cache/skill_feedback.json") -> None:
        self.cache = JsonCache(path, ttl_seconds=0)

    def _key(self, skill_name: str) -> str:
        return f"skill:{skill_name}"

    def get_stats(self, skill_name: str) -> dict[str, Any]:
        return self.cache.get(self._key(skill_name)) or {
            "success": 0,
            "failure": 0,
            "uses": 0,
            "score_adjustment": 0.0,
        }

    def record(self, skill_name: str, success: bool, query: str | None = None, note: str | None = None) -> dict[str, Any]:
        stats = self.get_stats(skill_name)
        stats["uses"] = int(stats.get("uses", 0)) + 1
        if success:
            stats["success"] = int(stats.get("success", 0)) + 1
        else:
            stats["failure"] = int(stats.get("failure", 0)) + 1

        success_count = int(stats.get("success", 0))
        failure_count = int(stats.get("failure", 0))
        total = max(success_count + failure_count, 1)
        success_rate = success_count / total

        # Conservative adjustment for routing. Keeps semantic score dominant.
        stats["score_adjustment"] = round((success_rate - 0.5) * 0.08, 4)
        stats["last_query_hash"] = stable_hash(query or "") if query else None
        stats["last_note"] = note

        self.cache.set(self._key(skill_name), stats)
        return stats

    def adjust_score(self, skill_name: str, base_score: float) -> float:
        stats = self.get_stats(skill_name)
        adjusted = base_score + float(stats.get("score_adjustment", 0.0))
        return max(0.0, min(1.0, adjusted))

    def snapshot(self) -> dict[str, Any]:
        return self.cache._data
