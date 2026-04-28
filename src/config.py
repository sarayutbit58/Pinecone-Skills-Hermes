from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any

_ENV_PATTERN = re.compile(r"^\$\{([^}]+)\}$")


def resolve_env(value: Any) -> Any:
    if isinstance(value, str):
        match = _ENV_PATTERN.match(value.strip())
        if match:
            return os.getenv(match.group(1), "")
    return value


@dataclass
class PineconeConfig:
    api_key: str = ""
    environment: str = "us-east-1-aws"
    index_name: str = "hermes-skills"
    namespace: str = "default"


@dataclass
class EmbeddingConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    dimension: int = 1536


@dataclass
class SkillsConfig:
    paths: list[str] = field(default_factory=lambda: ["~/.hermes/skills"])
    include_external_dirs: bool = True
    reindex_if_hash_changed: bool = True


@dataclass
class RoutingConfig:
    top_k: int = 8
    auto_load_threshold: float = 0.84
    suggest_threshold: float = 0.74
    max_auto_loaded_skills: int = 3


@dataclass
class SafetyConfig:
    allow_community_skills: bool = False
    require_platform_match: bool = True
    require_toolset_match: bool = True
    blocked_capabilities: list[str] = field(default_factory=lambda: [
        "credential_access",
        "filesystem_write",
        "network_egress",
    ])


@dataclass
class PluginConfig:
    enabled: bool = True
    auto_index_on_start: bool = True
    auto_route_on_user_message: bool = False
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    embeddings: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    skills: SkillsConfig = field(default_factory=SkillsConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)


def load_config(raw: dict[str, Any] | None) -> PluginConfig:
    raw = raw or {}
    pc = raw.get("pinecone", {}) or {}
    emb = raw.get("embeddings", {}) or {}
    skills = raw.get("skills", {}) or {}
    routing = raw.get("routing", {}) or {}
    safety = raw.get("safety", {}) or {}

    paths = skills.get("paths", ["~/.hermes/skills"])
    if isinstance(paths, str):
        paths = [paths]

    blocked = safety.get("blocked_capabilities", ["credential_access", "filesystem_write", "network_egress"])
    if isinstance(blocked, str):
        blocked = [blocked]

    return PluginConfig(
        enabled=bool(raw.get("enabled", True)),
        auto_index_on_start=bool(raw.get("auto_index_on_start", True)),
        auto_route_on_user_message=bool(raw.get("auto_route_on_user_message", False)),
        pinecone=PineconeConfig(
            api_key=resolve_env(pc.get("api_key", os.getenv("PINECONE_API_KEY", ""))),
            environment=pc.get("environment", "us-east-1-aws"),
            index_name=pc.get("index_name", "hermes-skills"),
            namespace=pc.get("namespace", "default"),
        ),
        embeddings=EmbeddingConfig(
            provider=emb.get("provider", "openai"),
            model=emb.get("model", "text-embedding-3-small"),
            dimension=int(emb.get("dimension", 1536)),
        ),
        skills=SkillsConfig(
            paths=paths,
            include_external_dirs=bool(skills.get("include_external_dirs", True)),
            reindex_if_hash_changed=bool(skills.get("reindex_if_hash_changed", True)),
        ),
        routing=RoutingConfig(
            top_k=int(routing.get("top_k", 8)),
            auto_load_threshold=float(routing.get("auto_load_threshold", 0.84)),
            suggest_threshold=float(routing.get("suggest_threshold", 0.74)),
            max_auto_loaded_skills=int(routing.get("max_auto_loaded_skills", 3)),
        ),
        safety=SafetyConfig(
            allow_community_skills=bool(safety.get("allow_community_skills", False)),
            require_platform_match=bool(safety.get("require_platform_match", True)),
            require_toolset_match=bool(safety.get("require_toolset_match", True)),
            blocked_capabilities=blocked,
        ),
    )
