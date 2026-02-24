from fastapi.testclient import TestClient

from coldwing.api.app import app


client = TestClient(app)


def test_api_basic_auth_required():
    res = client.post("/v1/scans", json={"profile": "snapshot", "scope": {"target": "example.com", "allow_active_scan": True}})
    assert res.status_code == 422


def test_api_basic_auth_ok(monkeypatch, tmp_path):
    monkeypatch.setenv("COLDWING_INMEM_QUEUE", "1")
    from coldwing.api.app import InMemoryQueueAdapter

    import coldwing.api.app as appmod

    appmod.queue = InMemoryQueueAdapter()
    res = client.post(
        "/v1/scans",
        headers={"Authorization": "Bearer token-acme"},
        json={"profile": "snapshot", "scope": {"target": "example.com", "allow_active_scan": True}},
    )
    assert res.status_code == 200
    assert "id" in res.json()
