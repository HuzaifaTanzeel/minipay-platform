"""Payments: create/get, validation, idempotency, pagination, latency, ambiguous refs."""
from __future__ import annotations

import os
import statistics
import subprocess
import time

import jsonschema
import pytest

from schemas import ERROR_ENVELOPE, PAYMENT

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_create_payment_201_schema(api, customer, uniq):
    """response schema/content assertions — POST /api/payments 201."""
    r = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": customer["customer_ref"],
            "amount": "12.50",
            "transaction_ref": uniq,
        },
    )
    assert r.status_code == 201, r.text
    jsonschema.validate(r.json(), PAYMENT)


def test_create_payment_negative_amount_422(api, customer, uniq):
    """invalid/missing fields — amount must be > 0."""
    r = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": customer["customer_ref"],
            "amount": -1,
            "transaction_ref": uniq,
        },
    )
    assert r.status_code == 422


def test_create_payment_three_dp_422(api, customer, uniq):
    """invalid/missing fields — amount at most 2 decimal places."""
    r = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": customer["customer_ref"],
            "amount": "1.234",
            "transaction_ref": uniq,
        },
    )
    assert r.status_code == 422


def test_create_payment_unknown_customer_404(api, uniq):
    """unknown resources — POST payment for a missing customer."""
    r = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": "CUSTNOPE01",
            "amount": "10.00",
            "transaction_ref": uniq,
        },
    )
    assert r.status_code == 404
    jsonschema.validate(r.json(), ERROR_ENVELOPE)
    assert r.json()["error"]["code"] == "CUSTOMER_NOT_FOUND"


def test_get_payment_ok(api, customer, uniq):
    """successful requests — GET /api/payments/{ref}."""
    created = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": customer["customer_ref"],
            "amount": "8.00",
            "transaction_ref": uniq,
        },
    )
    assert created.status_code == 201
    got = api.request("GET", f"/api/payments/{uniq}")
    assert got.status_code == 200
    assert got.json()["id"] == created.json()["id"]
    jsonschema.validate(got.json(), PAYMENT)


def test_get_payment_by_id_ok(api, customer, uniq):
    """successful requests — GET /api/payments/by-id/{id}."""
    created = api.request(
        "POST",
        "/api/payments",
        json={
            "customer_ref": customer["customer_ref"],
            "amount": "9.00",
            "transaction_ref": uniq,
        },
    )
    assert created.status_code == 201
    txn_id = created.json()["id"]
    got = api.request("GET", f"/api/payments/by-id/{txn_id}")
    assert got.status_code == 200
    assert got.json()["transaction_ref"] == uniq


def test_get_payment_unknown_404_envelope(api):
    """unknown resources — error envelope + X-Request-ID."""
    r = api.request("GET", "/api/payments/TXN_NOPE_01")
    assert r.status_code == 404
    body = r.json()
    jsonschema.validate(body, ERROR_ENVELOPE)
    assert body["error"]["code"] == "PAYMENT_NOT_FOUND"
    assert body["error"]["request_id"]
    assert r.headers.get("X-Request-ID") == body["error"]["request_id"]


def test_idempotent_replay_same_payload_200(api, customer, uniq):
    """duplicate/idempotent payment submission — same payload replays."""
    payload = {
        "customer_ref": customer["customer_ref"],
        "amount": "15.00",
        "transaction_ref": uniq,
    }
    first = api.request("POST", "/api/payments", json=payload)
    assert first.status_code == 201
    second = api.request("POST", "/api/payments", json=payload)
    assert second.status_code == 200
    assert second.headers.get("Idempotent-Replay") == "true"
    assert second.json()["id"] == first.json()["id"]


def test_same_ref_different_amount_409(api, customer, uniq):
    """duplicate/idempotent payment submission — different payload conflicts."""
    payload = {
        "customer_ref": customer["customer_ref"],
        "amount": "15.00",
        "transaction_ref": uniq,
    }
    first = api.request("POST", "/api/payments", json=payload)
    assert first.status_code == 201
    conflict = api.request(
        "POST",
        "/api/payments",
        json={**payload, "amount": "16.00"},
    )
    assert conflict.status_code == 409
    jsonschema.validate(conflict.json(), ERROR_ENVELOPE)
    assert conflict.json()["error"]["code"] == "REFERENCE_CONFLICT"


def test_customer_payments_pagination(api, customer, uniq):
    """successful requests — GET /api/customers/{id}/payments pagination."""
    for i in range(2):
        r = api.request(
            "POST",
            "/api/payments",
            json={
                "customer_ref": customer["customer_ref"],
                "amount": "1.00",
                "transaction_ref": f"{uniq}{i}",
            },
        )
        assert r.status_code == 201
    cid = customer["id"]
    page0 = api.request("GET", f"/api/customers/{cid}/payments", params={"limit": 1, "offset": 0})
    page1 = api.request("GET", f"/api/customers/{cid}/payments", params={"limit": 1, "offset": 1})
    assert page0.status_code == 200
    assert page1.status_code == 200
    b0, b1 = page0.json(), page1.json()
    assert b0["limit"] == 1 and b0["offset"] == 0
    assert "items" in b0 and len(b0["items"]) == 1
    assert b1["items"][0]["id"] != b0["items"][0]["id"]


def test_customer_payments_limit_bounds_422(api, customer):
    """invalid/missing fields — limit Query ge=1, le=200."""
    cid = customer["id"]
    low = api.request("GET", f"/api/customers/{cid}/payments", params={"limit": 0})
    high = api.request("GET", f"/api/customers/{cid}/payments", params={"limit": 201})
    assert low.status_code == 422
    assert high.status_code == 422


def test_malformed_json_400_or_422(api):
    """invalid/missing fields — malformed JSON body."""
    r = api.request(
        "POST",
        "/api/customers",
        data="{",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code in (400, 422)


def test_lookup_latency_p50_under_300ms(api):
    """one basic response-time assertion — p50 of 10 GETs, not p99 (laptop noise)."""
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        r = api.request("GET", "/api/payments/TXN00000001")
        times.append((time.perf_counter() - t0) * 1000)
        assert r.status_code == 200
    p50 = statistics.median(times)
    assert p50 < 300, f"p50 {p50:.1f} ms (p99 on a laptop is too noisy for a gate)"


def test_duplicate_reference_lookup(api):
    """duplicate seed ref is 409 REFERENCE_AMBIGUOUS with both row ids."""
    r = api.request("GET", "/api/payments/TXN00004999")
    assert r.status_code == 409
    body = r.json()
    jsonschema.validate(body, ERROR_ENVELOPE)
    assert body["error"]["code"] == "REFERENCE_AMBIGUOUS"
    assert body["error"]["request_id"]
    ids = body["error"]["ids"]
    assert isinstance(ids, list) and len(ids) == 2
    assert all(isinstance(i, int) for i in ids)


@pytest.mark.skipif(
    not os.getenv("MINIPAY_ALLOW_DESTRUCTIVE"),
    reason="set MINIPAY_ALLOW_DESTRUCTIVE=1 to stop Compose db",
)
def test_ready_503_when_db_down(anon):
    """server/API error behavior — /ready is 503 when Postgres is down."""
    try:
        subprocess.run(
            ["docker", "compose", "stop", "db"],
            cwd=_REPO,
            check=True,
            capture_output=True,
            text=True,
        )
        last = None
        for _ in range(20):
            last = anon.request("GET", "/ready")
            if last.status_code == 503:
                break
            time.sleep(0.5)
        assert last is not None and last.status_code == 503
        assert last.json()["status"] == "not_ready"
    finally:
        subprocess.run(
            ["docker", "compose", "start", "db"],
            cwd=_REPO,
            check=True,
            capture_output=True,
            text=True,
        )
        for _ in range(40):
            r = anon.request("GET", "/ready")
            if r.status_code == 200:
                return
            time.sleep(0.5)
        pytest.fail("/ready did not recover after starting db")
