from __future__ import annotations


def run(target: str, deep: bool = False) -> dict:
    tech = ["nginx", "python"]
    if deep:
        tech.extend(["fastapi", "postgresql"]) 
    return {"target": target, "stack": tech, "mode": "deep" if deep else "light"}
