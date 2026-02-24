from __future__ import annotations

from fastapi import Header, HTTPException

from coldwing.api.tenants import Tenant, get_tenant_by_token


def require_tenant_token(authorization: str = Header(...)) -> Tenant:
    token = authorization.replace("Bearer", "").strip()
    tenant = get_tenant_by_token(token)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid tenant token")
    return tenant
