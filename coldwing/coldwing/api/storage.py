from __future__ import annotations

import json
from pathlib import Path

from coldwing.api.tenants import tenant_storage_root


def scan_dir(tenant_id: str, scan_id: str) -> Path:
    d = tenant_storage_root(tenant_id) / "scans" / scan_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
