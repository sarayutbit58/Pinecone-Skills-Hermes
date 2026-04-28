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
