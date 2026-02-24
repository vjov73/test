import pytest

from coldwing.service import run_scan


def test_redteam_gating_blocks_without_approval(tmp_path, monkeypatch):
    monkeypatch.setattr("coldwing.service.DATA_ROOT", tmp_path)
    spec = {
        "tenant_id": "tenant_acme",
        "profile": "redteam",
        "scope": {
            "tenant_id": "tenant_acme",
            "target": "example.com",
            "allow_active_scan": True,
            "redteam_approved": False,
            "redteam_reference": "",
        },
    }
    with pytest.raises(PermissionError):
        run_scan(spec)
