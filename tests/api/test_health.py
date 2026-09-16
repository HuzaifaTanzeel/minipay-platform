"""Health and readiness (successful probes; /health needs no API key)."""


def test_health_ok(anon):
    """successful requests — GET /health."""
    r = anon.request("GET", "/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_ok(anon):
    """successful requests — GET /ready (schema: status, checks.database)."""
    r = anon.request("GET", "/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["checks"]["database"] == "ok"
