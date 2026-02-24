from __future__ import annotations

from typing import Any


def build_json_report(results: dict[str, Any]) -> dict[str, Any]:
    return {"meta": {"job_id": results["job_id"], "profile": results["profile"]}, "results": results}
