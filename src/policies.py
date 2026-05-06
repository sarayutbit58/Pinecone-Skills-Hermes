from __future__ import annotations

import platform
from typing import Any


def _as_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    return {str(item) for item in value}


def current_platform() -> str:
    p = platform.system().lower()
    if "darwin" in p:
        return "macos"
    if "windows" in p:
        return "windows"
    if "linux" in p:
        return "linux"
    return p


def is_allowed(meta: dict[str, Any], config: Any) -> bool:
    trust = meta.get("trust_level")
    if trust == "community" and not config.safety.allow_community_skills:
        return False

    if config.safety.require_platform_match:
        platforms = _as_set(meta.get("platforms"))
        if platforms and current_platform() not in platforms:
            return False

    if config.safety.require_toolset_match:
        required_toolsets = _as_set(getattr(config.safety, "required_toolsets", []))
        skill_toolsets = _as_set(meta.get("toolsets"))
        if required_toolsets and not (skill_toolsets & required_toolsets):
            return False

    caps = _as_set(meta.get("capabilities"))
    blocked = _as_set(config.safety.blocked_capabilities)
    if caps & blocked:
        return False

    return True
