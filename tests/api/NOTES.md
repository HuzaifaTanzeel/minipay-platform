# API test notes

Run the suite against a live Compose API (not an in-process client):

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m pytest tests/api -v
```

`MINIPAY_BASE_URL` defaults to `http://localhost:8000`. `API_KEY` (or `MINIPAY_API_KEY`) is read from the environment or from repo-root `.env`. Stopping Postgres is skipped unless `MINIPAY_ALLOW_DESTRUCTIVE=1`.

## Brief coverage

| Brief | Test |
|---|---|
| Successful requests | `test_health_ok`, `test_ready_ok`, `test_create_customer_201`, `test_create_payment_201_schema`, `test_get_payment_ok`, `test_get_payment_by_id_ok`, `test_customer_payments_pagination` |
| Invalid / missing fields | `test_create_customer_missing_name_422`, `test_create_payment_negative_amount_422`, `test_create_payment_three_dp_422`, `test_customer_payments_limit_bounds_422`, `test_malformed_json_400_or_422` |
| Unknown resources | `test_create_payment_unknown_customer_404`, `test_get_payment_unknown_404_envelope` |
| Auth | `test_missing_api_key_401`, `test_wrong_api_key_403`, `test_health_needs_no_key` |
| Idempotent / duplicate submit | `test_idempotent_replay_same_payload_200`, `test_same_ref_different_amount_409`, `test_create_customer_duplicate_409` |
| Server error where practical | `test_duplicate_reference_lookup` (500 today), `test_ready_503_when_db_down` |
| Schema | `test_create_payment_201_schema` (`jsonschema`) |
| Response time | `test_lookup_latency_p50_under_300ms` |

`GET /api/payments/{ref}` is by reference. Numeric id is `GET /api/payments/by-id/{id}`.

## Timeouts

- Client: connect about 2 s, read about 5 s. These tests use a 5 s request timeout.
- Server: Postgres `statement_timeout` is 2000 ms (`db_statement_timeout_ms`). `/ready` uses a 1 s pool timeout.

## Retries (payment client, not this suite)

Retry only network errors, HTTP 5xx, and 429, and only on **idempotent** calls (GET, or POST with the same `transaction_ref`). Exponential backoff with jitter, max 3 attempts. Never retry 4xx — that is a bad request; if the 4xx rate climbs, alert. 429: honour `Retry-After` if present, else the same backoff.

## Idempotency

The client generates `transaction_ref`. The server must store the **result**. Same ref + same payload → 200 and `Idempotent-Replay: true`. Same ref + different amount → 409 `REFERENCE_CONFLICT`. If the client retried a POST without a ref, it could create two payments.

## 4xx vs 5xx

- 4xx: caller bug (validation, missing key, unknown customer). Fix the request; do not retry.
- 5xx: our bug or an outage. Retry with backoff, then page. Quote `error.request_id` / `X-Request-ID` in logs.
- Duplicate seed refs such as `TXN00004999` currently 500 `INTERNAL_ERROR` (Incident 1). After the lookup fix this should be 409 `REFERENCE_AMBIGUOUS`.

## Callbacks

If a merchant never sees a SUCCESS callback, reconciliation (`sql/06_reconciliation_callbacks.sql`) is the safety net — not another blind POST of the payment.
