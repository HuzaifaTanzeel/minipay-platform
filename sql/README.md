# SQL reports

Read-only scripts for MiniPay operational questions. They do not `UPDATE` or `DELETE` seed data.

From the repository root, with Compose `db` healthy and seeded (~50k transactions):

```powershell
Get-Content sql\01_count_value_by_status_day.sql | docker compose exec -T db psql -U minipay -d minipay
```

| File | Question |
|---|---|
| `01_count_value_by_status_day.sql` | Count and value by status and day |
| `02_top10_customers_success.sql` | Top 10 customers by SUCCESS value |
| `03_stuck_processing_15m.sql` | PROCESSING older than 15 minutes |
| `04_duplicate_refs.sql` | Duplicate `transaction_ref` |
| `05_daily_success_rate.sql` | Daily success rate % |
| `06_reconciliation_callbacks.sql` | SUCCESS vs callback SUCCESS |
| `07_processing_time_avg_p95.sql` | Average and p95 duration |
| `00_indexes_v1.sql` | Indexes for lookup / customer list / PROCESSING |
| [PERFORMANCE.md](PERFORMANCE.md) | Before/after times (500k-row measurement) |
