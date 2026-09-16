"""Authentication / access-control on /api/* vs open /health."""
import jsonschema

from schemas import ERROR_ENVELOPE


def test_missing_api_key_401(anon):
    """authentication or access-control — no X-API-Key."""
    r = anon.request("GET", "/api/payments/TXN00000001")
    assert r.status_code == 401
    jsonschema.validate(r.json(), ERROR_ENVELOPE)
    assert r.json()["error"]["code"] == "MISSING_API_KEY"


def test_wrong_api_key_403(anon):
    """authentication or access-control — wrong X-API-Key."""
    r = anon.request(
        "GET",
        "/api/payments/TXN00000001",
        headers={"X-API-Key": "not-the-key"},
    )
    assert r.status_code == 403
    jsonschema.validate(r.json(), ERROR_ENVELOPE)
    assert r.json()["error"]["code"] == "INVALID_API_KEY"


def test_health_needs_no_key(anon):
    """authentication or access-control — /health stays open."""
    r = anon.request("GET", "/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
