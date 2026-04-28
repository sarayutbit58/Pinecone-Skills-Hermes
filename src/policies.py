import platform


def current_platform():
    p = platform.system().lower()
    if "darwin" in p:
        return "macos"
    if "windows" in p:
        return "windows"
    if "linux" in p:
        return "linux"
    return p


def is_allowed(meta, config):
    trust = meta.get("trust_level")
    if trust == "community" and not config.safety.allow_community_skills:
        return False

    if config.safety.require_platform_match:
        platforms = meta.get("platforms", [])
        if platforms and current_platform() not in platforms:
            return False

    caps = meta.get("capabilities", [])
    for cap in caps:
        if cap in config.safety.blocked_capabilities:
            return False

    return True
