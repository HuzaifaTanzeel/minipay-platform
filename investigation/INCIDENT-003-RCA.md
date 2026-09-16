# INCIDENT-003 – Slow payment search as volume grows

| | |
|---|---|
| Severity | P2 |
| Status | Resolved |
| Components | db |
| Author | Huzaifa Tanzeel |

## What happened

Operators searching by payment reference (and opening a customer’s latest payments) got slower as `transactions` grew to **500,000** rows. Answers were still correct. We added indexes in `sql/00_indexes_v1.sql`. Search and the customer list got faster; a huge “stuck PROCESSING” list did not.

## How we reproduced it

```text
EXPLAIN (ANALYZE, BUFFERS)
  SELECT * FROM transactions WHERE transaction_ref = 'TXN00012345';
  SELECT * FROM transactions WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 50;
  SELECT * FROM transactions WHERE status = 'PROCESSING' AND created_at < NOW() - INTERVAL '15 minutes';
```

Lookup still returned one row. `LIMIT 50` did not skip the full table scan.

## Evidence

`evidence/sql/lookup_by_ref_before.txt` / `_after.txt` (same for `customer_list_*`, `stuck_*`). Summary: `sql/PERFORMANCE.md`.

| Query | Before | After |
|---|---|---|
| Search by reference | 129 ms, seq scan | 0.6 ms, index |
| Customer list, 50 rows | 63 ms, seq scan | 13 ms, index |
| Stuck PROCESSING (~25k rows) | 167 ms | 172 ms (index used, still a large heap read) |

## Hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| API/UI bug | `EXPLAIN` in `psql` only | **Rejected** |
| Host overloaded | Idle machine; plans show ~500k-row filter | **Rejected** |
| Missing indexes for how we search | Before seq scan, after index scan | **Confirmed** |
| Stuck report will speed up the same way | Time stayed ~170 ms | **Rejected** as a win |

## Cause

**Trigger:** search/list on a large heap. **Underlying:** no indexes on `transaction_ref`, `(customer_id, created_at)`, or PROCESSING+time. FK on `callbacks` does not index `transaction_id`. Stuck filter matched ~25k rows, so an index could not skip much heap.

## Fix

No data change. Applied `sql/00_indexes_v1.sql` + `ANALYZE`. No `CLUSTER` (Postgres heap + B-trees).

## Check

Same three `EXPLAIN` commands after indexes (`*_after.txt`). Lookup ~129 ms → ~0.6 ms; customer list ~63 ms → ~13 ms.

## Prevent

Review indexes when adding a search path; keep plans in `evidence/sql/`. Optional: watch p95 of lookup via `pg_stat_statements`.
