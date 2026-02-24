from __future__ import annotations

from typing import Any


REQUIRED_SCOPE_FIELDS = {"target", "allow_active_scan", "tenant_id"}


def validate_scope(scope: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_SCOPE_FIELDS - set(scope)
    if missing:
        raise ValueError(f"Missing scope fields: {sorted(missing)}")
    if not isinstance(scope.get("target"), str) or not scope["target"].strip():
        raise ValueError("target must be a non-empty string")
    allowed_ports = scope.get("allowed_ports", [])
    if allowed_ports and not all(isinstance(p, int) and 1 <= p <= 65535 for p in allowed_ports):
        raise ValueError("allowed_ports must contain valid integer ports")
    return scope


def enforce_redteam(scope: dict[str, Any], redteam: bool) -> None:
    if not redteam:
        return
    if scope.get("redteam_approved") is not True:
        raise PermissionError("Red Team profile requires redteam_approved=true in scope")
    if not isinstance(scope.get("redteam_reference"), str) or not scope["redteam_reference"].strip():
        raise PermissionError("Red Team profile requires redteam_reference")
