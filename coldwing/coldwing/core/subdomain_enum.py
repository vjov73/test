from __future__ import annotations


def run(target: str, limit: int = 10) -> dict:
    subs = [f"sub{i}.{target}" for i in range(1, limit + 1)]
    return {"target": target, "subdomains": subs}
