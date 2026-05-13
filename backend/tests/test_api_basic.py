import json

def test_root_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("status") == "ok"
    assert "backend" in data.get("message", "").lower()


def test_auth_session_no_session_returns_401(client):
    resp = client.post("/auth/session")
    assert resp.status_code == 401
    data = resp.get_json()
    assert data is not None
    assert data.get("code") == "unauthorized"
    assert isinstance(data.get("message"), str)


def test_simulator_all_public(client):
    resp = client.get("/simulator/all")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_visor_all_public(client):
    resp = client.get("/visor/all")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_simulator_access_requires_auth(client):
    resp = client.get("/simulator/access/1")
    assert resp.status_code in (401, 403)


def test_visor_access_requires_auth(client):
    resp = client.get("/visor/access/1")
    assert resp.status_code in (401, 403)
