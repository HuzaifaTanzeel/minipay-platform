# INCIDENT-001 – Duplicate reference lookup returned 500

| | |
|---|---|
| Severity | P2 |
| Status | Resolved |
| Components | api / db |
| Author | Huzaifa Tanzeel |

## What happened

Operators searching by payment reference sometimes got HTTP 500 `INTERNAL_ERROR` while neighbouring refs still returned 200. The UI showed a generic crash. The same seed refs (for example `TXN00004999`) appear twice in `transactions`. Lookup now returns 409 `REFERENCE_AMBIGUOUS` with both ids.

## How we reproduced it

Compose stack up, 500k-row seed. Unique ref still worked; health was up.

```text
GET /api/payments/TXN00000001   → 200  (id=1, SUCCESS)
GET /health                     → 200
GET /api/payments/TXN00004999   → 500  INTERNAL_ERROR  request_id=54a82d7d3bfd
```

`GET /api/payments/by-id/{id}` was already available for a known numeric id.

## Evidence

| File | What it shows |
|---|---|
| [evidence/api/incident-001-curl-500.txt](../evidence/api/incident-001-curl-500.txt) | Duplicate-ref GET: 500 envelope, `request_id` `54a82d7d3bfd` |
| [evidence/api/incident-001-curl-200.txt](../evidence/api/incident-001-curl-200.txt) | Unique ref `TXN00000001` still 200 |
| [evidence/api/incident-001-api-logs.txt](../evidence/api/incident-001-api-logs.txt) | Same `request_id`: `MultipleRowsError` from `fetch_one_strict` |
| [evidence/api/incident-001-duplicate-refs.txt](../evidence/api/incident-001-duplicate-refs.txt) | `sql/04_duplicate_refs.sql`: 100 refs appear twice |
| [evidence/api/incident-001-unique-constraint-fails.txt](../evidence/api/incident-001-unique-constraint-fails.txt) | `ALTER TABLE … UNIQUE (transaction_ref)` rejected (`TXN00354999` duplicated) |
| [evidence/api/incident-001-curl-409.txt](../evidence/api/incident-001-curl-409.txt) | After the lookup change: 409 `REFERENCE_AMBIGUOUS` with `ids` |

## Hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| API process is down | `/health` 200; `TXN00000001` 200 in the same second | **Rejected** |
| Auth / nginx misroute | Same path and key as the 200 lookup | **Rejected** |
| `fetch_one_strict` raises when two rows share the ref; unhandled → 500 | Logs: `MultipleRowsError` for `('TXN00004999',)` | **Confirmed** |
| Schema already unique on `transaction_ref` | `ALTER TABLE … UNIQUE` failed on existing duplicates | **Rejected** |

## Cause

**Trigger:** seed generator reuses a `transaction_ref` every 5,000 rows (`TXN00004999` is ids 4999 and 5000). **Underlying:** `GET /api/payments/{ref}` assumed one row per ref (`get_by_ref` → `fetch_one_strict`) while the table has no uniqueness on `transaction_ref`. `MultipleRowsError` was not mapped to an API error, so the unhandled handler returned 500. POST create already treated an ambiguous ref as 409; GET did not.

## Fix

**Immediate:** catch `MultipleRowsError` in `get_payment` (not in `fetch_one_strict`). Look up both rows, log a warning, return 409 `REFERENCE_AMBIGUOUS` with `ids` and a pointer to `GET /api/payments/by-id/{id}`. Seed rows are unchanged. POST idempotency is unchanged.

**Lasting:** do not add `UNIQUE(transaction_ref)` until duplicates are cleaned up (the ALTER already failed). After a cleanup runbook, `CREATE UNIQUE INDEX CONCURRENTLY`. New ambiguous creates are already blocked on POST.

## Check

- `GET /api/payments/TXN00004999` → 409, `REFERENCE_AMBIGUOUS`, ids `[4999, 5000]` (`evidence/api/incident-001-curl-409.txt`).
- `GET /api/payments/TXN00000001` still 200.
- `python -m pytest tests/api -v` — 22 passed, 1 skipped (`test_duplicate_reference_lookup` included).
- Playwright `test_search_duplicate_reference_shows_clear_message` — 6 passed after rebuilding Compose `web`.

## Prevent

Detection: `test_duplicate_reference_lookup` and the UI journey on `TXN00004999`. Prevention: keep POST’s ambiguous-ref 409; apply uniqueness only after cleanup, concurrently.
