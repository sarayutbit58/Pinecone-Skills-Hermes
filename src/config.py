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
    index_name: str = "hermes-skills"
    namespace: str = "default"
    transport: str = "sdk"  # sdk | mcp
    cloud: str = "aws"
    region: str = "us-east-1"
    integrated_embedding: bool = False
    mcp_command: str = "npx"
    mcp_args: list[str] = field(default_factory=lambda: ["-y", "@pinecone-database/mcp"])


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
    top_k: int = 5
    auto_load_threshold: float = 0.86
    suggest_threshold: float = 0.76
    max_auto_loaded_skills: int = 2
    auto_route_instruction: bool = True


@dataclass
class SafetyConfig:
    allow_community_skills: bool = False
    require_platform_match: bool = True
    require_toolset_match: bool = True
    supported_platforms: list[str] = field(default_factory=lambda: ["linux"])
    required_runtime_tools: list[str] = field(default_factory=lambda: ["node", "npm", "npx"])
    blocked_capabilities: list[str] = field(default_factory=lambda: [
        "credential_access",
        "filesystem_write",
        "network_egress",
    ])
    redact_paths: bool = True


@dataclass
class RuntimeConfig:
    retries: int = 3
    timeout_seconds: int = 30
    fail_closed: bool = False
    debug: bool = False
    enforce_linux: bool = True
    require_npm: bool = True


@dataclass
class PluginConfig:
    enabled: bool = True
    auto_index_on_start: bool = False
    auto_route_on_user_message: bool = True
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    embeddings: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    skills: SkillsConfig = field(default_factory=SkillsConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)


def _as_list(value: Any, default: list[str]) -> list[str]:
    if value is None:
        return default
    if isinstance(value, str):
        return [value]
    return list(value)


def load_config(raw: dict[str, Any] | None) -> PluginConfig:
    raw = raw or {}
    pc = raw.get("pinecone", {}) or {}
    emb = raw.get("embeddings", {}) or {}
    skills = raw.get("skills", {}) or {}
    routing = raw.get("routing", {}) or {}
    safety = raw.get("safety", {}) or {}
    runtime = raw.get("runtime", {}) or {}

    return PluginConfig(
        enabled=bool(raw.get("enabled", True)),
        auto_index_on_start=bool(raw.get("auto_index_on_start", False)),
        auto_route_on_user_message=bool(raw.get("auto_route_on_user_message", True)),
        pinecone=PineconeConfig(
            api_key=resolve_env(pc.get("api_key", os.getenv("PINECONE_API_KEY", ""))),
            index_name=pc.get("index_name", "hermes-skills"),
            namespace=pc.get("namespace", "default"),
            transport=pc.get("transport", "sdk"),
            cloud=pc.get("cloud", "aws"),
            region=pc.get("region", "us-east-1"),
            integrated_embedding=bool(pc.get("integrated_embedding", False)),
            mcp_command=pc.get("mcp_command", "npx"),
            mcp_args=_as_list(pc.get("mcp_args"), ["-y", "@pinecone-database/mcp"]),
        ),
        embeddings=EmbeddingConfig(
            provider=emb.get("provider", "openai"),
            model=emb.get("model", "text-embedding-3-small"),
            dimension=int(emb.get("dimension", 1536)),
        ),
        skills=SkillsConfig(
            paths=_as_list(skills.get("paths"), ["~/.hermes/skills"]),
            include_external_dirs=bool(skills.get("include_external_dirs", True)),
            reindex_if_hash_changed=bool(skills.get("reindex_if_hash_changed", True)),
        ),
        routing=RoutingConfig(
            top_k=int(routing.get("top_k", 5)),
            auto_load_threshold=float(routing.get("auto_load_threshold", 0.86)),
            suggest_threshold=float(routing.get("suggest_threshold", 0.76)),
            max_auto_loaded_skills=int(routing.get("max_auto_loaded_skills", 2)),
            auto_route_instruction=bool(routing.get("auto_route_instruction", True)),
        ),
        safety=SafetyConfig(
            allow_community_skills=bool(safety.get("allow_community_skills", False)),
            require_platform_match=bool(safety.get("require_platform_match", True)),
            require_toolset_match=bool(safety.get("require_toolset_match", True)),
            supported_platforms=_as_list(safety.get("supported_platforms"), ["linux"]),
            required_runtime_tools=_as_list(safety.get("required_runtime_tools"), ["node", "npm", "npx"]),
            blocked_capabilities=_as_list(safety.get("blocked_capabilities"), ["credential_access", "filesystem_write", "network_egress"]),
            redact_paths=bool(safety.get("redact_paths", True)),
        ),
        runtime=RuntimeConfig(
            retries=int(runtime.get("retries", 3)),
            timeout_seconds=int(runtime.get("timeout_seconds", 30)),
            fail_closed=bool(runtime.get("fail_closed", False)),
            debug=bool(runtime.get("debug", False)),
            enforce_linux=bool(runtime.get("enforce_linux", True)),
            require_npm=bool(runtime.get("require_npm", True)),
        ),
    )
