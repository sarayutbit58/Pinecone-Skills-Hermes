from __future__ import annotations

from typing import Any, Dict

from .autonomous import AutonomousSkillAgent
from .config import load_config
from .indexer import SkillIndexer
from .router import SkillRouter

_indexer = None
_router = None
_agent = None


def register(ctx: Any) -> None:
    global _indexer, _router, _agent

    raw_config: Dict[str, Any] = {}
    if hasattr(ctx, "config") and ctx.config is not None:
        raw_config = ctx.config.get("pinecone_skill_router", {}) or {}

    config = load_config(raw_config)

    _indexer = SkillIndexer(config)
    _router = SkillRouter(config)
    _agent = AutonomousSkillAgent(_router)

    if config.enabled and config.auto_index_on_start:
        try:
            _indexer.sync()
        except Exception:
            pass

    def semantic_skill_search(params=None):
        query = (params or {}).get("query", "")
        return _router.search(query)

    def autonomous_route(params=None):
        query = (params or {}).get("query", "")
        return _agent.route(query)

    def skill_feedback(params=None):
        params = params or {}
        skill_name = params.get("skill_name", "")
        success = bool(params.get("success", False))
        query = params.get("query")
        note = params.get("note")
        if not skill_name:
            return {"error": "skill_name is required"}
        return _router.record_feedback(skill_name=skill_name, success=success, query=query, note=note)

    def skill_feedback_snapshot(params=None):
        return _router.feedback.snapshot()

    ctx.register_tool(
        name="semantic_skill_search",
        description="Semantic skill routing",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        function=semantic_skill_search,
    )

    ctx.register_tool(
        name="autonomous_skill_route",
        description="Auto skill selection before execution",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        function=autonomous_route,
    )

    ctx.register_tool(
        name="skill_feedback",
        description="Record success or failure feedback for a selected skill so future routing can improve.",
        parameters={
            "type": "object",
            "properties": {
                "skill_name": {"type": "string"},
                "success": {"type": "boolean"},
                "query": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["skill_name", "success"],
        },
        function=skill_feedback,
    )

    ctx.register_tool(
        name="skill_feedback_snapshot",
        description="Show local skill feedback statistics used for self-learning ranking.",
        parameters={"type": "object", "properties": {}, "required": []},
        function=skill_feedback_snapshot,
    )
