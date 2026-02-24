from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Tenant:
    tenant_id: str
    organization_name: str
    api_token: str


TENANTS = {
    "token-acme": Tenant("tenant_acme", "Acme Corp", "token-acme"),
    "token-coldwing": Tenant("tenant_coldwing", "Coldwing Labs", "token-coldwing"),
}


def get_tenant_by_token(token: str) -> Tenant | None:
    return TENANTS.get(token)


def tenant_storage_root(tenant_id: str) -> Path:
    root = Path("/data") / "tenants" / tenant_id
    root.mkdir(parents=True, exist_ok=True)
    return root
