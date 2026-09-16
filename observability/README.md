# Observability (optional)

Prometheus + Grafana + postgres-exporter, started with Compose profile `observability`. Default `docker compose up` does not start these services.

They scrape Docker DNS names (`api`, `db`, `postgres-exporter`). When Kubernetes lands, reuse the same scrape file, alert file, and dashboard JSON as ConfigMaps and point discovery at Services (`minipay-api`, `minipay-db`, `minipay-postgres-exporter`). Do not install kube-prometheus-stack until the cluster path works.

## Start

Core stack healthy and seeded first. Optional: set `GRAFANA_ADMIN_PASSWORD` in `.env` (see `.env.example`). If unset, Grafana logs in as `admin` / `CHANGE_ME`.

```powershell
docker compose --profile observability up -d --build
```

| URL | What |
|---|---|
| http://localhost:3000 | Grafana (`admin` / `GRAFANA_ADMIN_PASSWORD`) |
| http://localhost:9090 | Prometheus (graph, targets, alerts) |
| http://localhost:9187/metrics | postgres-exporter |
| http://localhost:8000/metrics | API histograms (no API key) |

The starter dashboard is **MiniPay overview** (folder MiniPay). It is provisioned with `allowUiUpdates: true`. Delete panels, change PromQL or SQL, and Save. Edits live in the `grafana-data` volume and survive container recreate. They reset only on `docker compose down -v`. To keep git in sync after UI edits: Grafana Share → Export → overwrite `grafana/dashboards/minipay.json`.

Prometheus UI (`/graph`) is a PromQL scratchpad that does not depend on Grafana. Alert rules are [prometheus/alerts.yml](prometheus/alerts.yml); edit the file and restart Prometheus (or POST `/-/reload`).

## Why p95, not only average

Average is pulled around by the easy majority. Ninety-nine payment lookups at 2 ms and one at 2 s still “look like” ~22 ms. Operators and SLOs care about the **slow tail**: the search that timed out, the seq-scan before indexes, the callback that retried.

- **p95** means 95% of samples finished faster than this value. p99 is stricter.
- MiniPay already answers this in SQL for **payment processing** time (`sql/07_processing_time_avg_p95.sql`): `AVG(...)` next to `percentile_cont(0.95) WITHIN GROUP (ORDER BY completed_at - created_at)`.
- The API histogram answers the same question for **request** time:

```text
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

versus

```text
sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))
```

Alert on **5xx ratio** (and p95 if you add a rule), not on average latency. Average can recover while p95 is still bad.

API tests use a p50 gate because a laptop p99 is too noisy; that is a test threshold, not an SLO.

`pg_stat_statements.mean_exec_time` is a per-statement average. Use it to find expensive SQL, not as a substitute for request p95.

## Datasources

Grafana OSS ships a PostgreSQL plugin; nothing extra to install. Provisioning wires:

- **Prometheus** — API request rate, latency percentiles, status classes, exporter stats (connections, xact, cache hit, rows).
- **Postgres** — live `sql/07` avg vs p95, stuck PROCESSING (> 15 minutes), top `pg_stat_statements`.

409 `REFERENCE_AMBIGUOUS` is a 4xx. The status panel groups codes as 2xx / 4xx / 5xx.

## Kubernetes later

| Compose | Cluster |
|---|---|
| scrape `api:8000` | Service `minipay-api` + `kubernetes_sd_configs` or a static overlay |
| scrape `postgres-exporter:9187` | Service `minipay-postgres-exporter` |
| Grafana → `db:5432` | Service `minipay-db` |
| `.env` passwords | Secret `secretKeyRef` / `envFrom` |

Same dashboard JSON. Same alert expression. Only service discovery changes.
