from __future__ import annotations


def run(target: str) -> dict:
    return {"target": target, "paths": ["/admin", "/backup", "/.git"]}
