# Query performance

Measured on local Postgres with **500,000** transactions. The default seed for a quick demo is 50,000; this run is larger so a full-table scan is easy to see.

We did not change payment rows. We added indexes in `00_indexes_v1.sql`, then ran the **same** three searches again.

Raw plans (no commentary): `evidence/sql/*_before.txt` and `*_after.txt`.

## What a user or operator does

| Action | Before | After |
|---|---|---|
| Search one payment by reference (`TXN00012345`) | **129 ms**, read the whole table | **0.6 ms**, index on `transaction_ref` |
| Open a customer’s latest 50 payments (`customer_id = 42`) | **63 ms**, read the whole table, then keep 50 | **13 ms**, index on customer + time |
| List payments stuck in PROCESSING (> 15 minutes) | **167 ms**, read the whole table | **172 ms**, index used but ~25,000 rows still loaded |

Search and the customer list are clearly faster. The stuck list is **not**, because it still returns tens of thousands of rows (almost every PROCESSING payment at this scale). An index does not help much when you still read that many heap pages.

## Indexes added

| Index | Why |
|---|---|
| `ix_transactions_ref` | Payment search and API lookup by reference |
| `ix_transactions_customer_created` | Customer payment list, newest first |
| `ix_transactions_processing` | Partial index: PROCESSING rows only (helps when few are stuck) |
| `ix_callbacks_transaction` | Load callbacks for one payment |

Postgres uses a heap table plus B-tree indexes (not a SQL Server clustered primary key).

## Trade-off

Indexes use disk and make inserts a bit heavier. Lookups stay cheap as the table grows. Default 50k seed for evaluators is still fine; 500k was for this measurement.
