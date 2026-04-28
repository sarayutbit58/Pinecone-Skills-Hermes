"""Hermes plugin entrypoint for Pinecone Skills Hermes."""

from __future__ import annotations

from typing import Any, Dict

from .config import load_config
from .indexer import SkillIndexer
from .router import SkillRouter


_indexer: SkillIndexer | None = None
_router: SkillRouter | None = None


def register(ctx: Any) -> None:
    """Register plugin tools with Hermes.

    This is the Hermes plugin entrypoint referenced by plugin.yaml.
    It registers two tools:

    - semantic_skill_index: scan local Hermes skills and index them to Pinecone
    - semantic_skill_search: find relevant skills from user intent
    """
    global _indexer, _router

    raw_config: Dict[str, Any] = {}
    if hasattr(ctx, "config") and ctx.config is not None:
        raw_config = ctx.config.get("pinecone_skill_router", {}) or {}

    config = load_config(raw_config)
    _indexer = SkillIndexer(config)
    _router = SkillRouter(config)

    if config.enabled and config.auto_index_on_start:
        try:
            _indexer.sync()
        except Exception as exc:
            if hasattr(ctx, "logger"):
                ctx.logger.error(f"Pinecone skill index startup sync failed: {exc}")

    def semantic_skill_index(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return _indexer.sync()

    def semantic_skill_search(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        params = params or {}
        query = params.get("query", "")
        if not query:
            return {"mode": "none", "skills": [], "error": "query is required"}
        return _router.search(query)

    ctx.register_tool(
        name="semantic_skill_index",
        description="Index Hermes SKILL.md files into Pinecone for semantic skill routing.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        function=semantic_skill_index,
    )

    ctx.register_tool(
        name="semantic_skill_search",
        description="Search relevant Hermes skills using semantic similarity over Pinecone.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User request or task intent to match against indexed Hermes skills.",
                }
            },
            "required": ["query"],
        },
        function=semantic_skill_search,
    )
