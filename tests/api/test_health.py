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


def test_metrics_ok_without_key(anon):
    """Prometheus scrape target is unauthenticated and exposes histograms."""
    # 401 is still an instrumented response; buckets appear after at least one.
    anon.request("GET", "/api/payments/TXN00000001")
    r = anon.request("GET", "/metrics")
    assert r.status_code == 200
    body = r.text
    assert "http_request_duration_seconds_bucket" in body
    assert "http_requests_total" in body
