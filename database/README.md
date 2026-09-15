# Database

MiniPay uses PostgreSQL 16. The product model is three tables in `database/schema.sql`: `customers`, `transactions`, and `callbacks`. Indexing in that schema is intentionally light so lookup and reporting patterns can be measured against loaded volume before indexes are added (`sql/PERFORMANCE.md` when that work lands). Do not rewrite or delete seed rows to make reports easier.

`database/02_extensions.sql` enables `pg_stat_statements` on first cluster init. Compose also sets `shared_preload_libraries=pg_stat_statements` and `log_min_duration_statement=100`. That is platform observability (statement stats and slow-query log), not part of the payment domain model.

Init files mounted into `docker-entrypoint-initdb.d` run **once**, when the data volume is empty. Changing them later requires recreating the volume (`docker compose down -v`), which deletes data.

## Prerequisites

- Docker Compose
- Python 3 (to run `generate_data.py`)
- `.env` copied from `.env.example` with `DB_PASSWORD` set (never commit `.env`)

Keep `DB_NAME` and `DB_USER` as `minipay` unless you also change the Compose healthcheck.

## Start Postgres

From the repository root:

```powershell
docker compose up -d db
docker compose ps
```

Wait until `db` is **healthy**. Postgres listens on `127.0.0.1:5432`.

Optional pgAdmin (Compose profile `tools` — not part of the payment runtime):

```powershell
docker compose --profile tools up -d
```

- URL: http://localhost:5050
- Login: `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` from `.env`
- Register server: host **`db`**, port `5432`, database and user from `.env`
- Do not use `localhost` as the host while pgAdmin runs as a Compose service

## Seed

Synthetic load is generated at runtime and is **not** stored in git (`seed.sql` is gitignored).

```powershell
python database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

Defaults (RNG seed 42): 1,000 customers and 50,000 transactions. Created timestamps fall in September 2026. Status mix is `SUCCESS`, `FAILED` (often `failure_code = UPSTREAM_ERROR`), and `PROCESSING`.

A small number of `transaction_ref` values appear twice (the generator reuses a reference every 5,000 rows, for example `TXN00004999`). That is intentional. The schema does not enforce uniqueness on `transaction_ref`.

Re-running the generator against a database that already has this seed will fail on unique `customer_ref` / primary keys. Reset the volume first.

## Checks

```powershell
docker compose exec db psql -U minipay -d minipay -c "SELECT count(*) FROM customers;"
docker compose exec db psql -U minipay -d minipay -c "SELECT status, count(*) FROM transactions GROUP BY 1 ORDER BY 1;"
docker compose exec db psql -U minipay -d minipay -c "SELECT transaction_ref, count(*) FROM transactions GROUP BY 1 HAVING count(*) > 1 ORDER BY 1;"
docker compose exec db psql -U minipay -d minipay -c "SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements';"
```

Expect 1,000 customers, 50,000 transactions (on the order of ~41k SUCCESS / ~6.5k FAILED / ~2.5k PROCESSING with the default generator), about ten duplicate references, and `pg_stat_statements` installed.

At 50k rows, simple aggregations often complete in tens of milliseconds on a laptop. Statement stats still show which query shapes ran; `EXPLAIN (ANALYZE, BUFFERS)` is the evidence for access patterns when reporting and indexes are added.

### Statement stats (optional)

```sql
SELECT left(query, 80) AS query_preview, calls, round(mean_exec_time::numeric, 2) AS mean_ms
FROM pg_stat_statements
WHERE query ILIKE '%transactions%'
  AND query NOT ILIKE '%pg_catalog%'
  AND query NOT ILIKE '%pga4dash%'
ORDER BY mean_exec_time DESC;
```

Slow-query log (statements ≥ 100 ms): `docker compose logs db --tail 100`.

## Reset

```powershell
docker compose down -v
```

This removes the named volume. Schema and extension scripts run again on the next `up`.

## Generator

`database/generate_data.py` writes PostgreSQL `INSERT` statements to stdout. Pipe into `psql` as above. Defaults: 1,000 customers, 50,000 transactions.
