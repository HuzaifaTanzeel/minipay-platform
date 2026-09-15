# 02 – SQL & Data Investigation

Use the supplied schema/data generator or an equivalent relational implementation.

Create SQL scripts that answer:
1. Transaction count and total value by status and day.
2. Top 10 customers by successful transaction value.
3. Transactions that have remained in `PROCESSING` for more than 15 minutes.
4. Duplicate transaction references.
5. Daily success rate as a percentage.
6. Reconciliation: successful transaction count/value versus callback-success count/value.
7. Average and p95 processing time where timestamps permit calculation.

Then identify and improve one deliberately inefficient query or access pattern. Provide `sql/PERFORMANCE.md` containing the before/after query plan or other evidence and explain the change (for example, indexing or query restructuring).

Use safe, readable SQL. Do not modify source data merely to make answers easier.
