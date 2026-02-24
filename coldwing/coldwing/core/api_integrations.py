from __future__ import annotations


def run_shodan(target: str, enabled: bool) -> dict:
    if not enabled:
        return {"enabled": False}
    return {"enabled": True, "target": target, "services": ["http", "https"]}
