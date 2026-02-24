from __future__ import annotations


def run(target: str) -> dict:
    return {"target": target, "risk": "medium", "findings": ["missing security headers"]}
