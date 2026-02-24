from __future__ import annotations

from typing import Any


def run(target: str) -> dict[str, Any]:
    return {"target": target, "records": {"A": ["203.0.113.10"], "MX": ["mail.example.net"]}}
