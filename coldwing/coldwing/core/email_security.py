from __future__ import annotations


def run(target: str) -> dict:
    return {"target": target, "spf": "pass", "dmarc": "monitor", "dkim": "unknown"}
