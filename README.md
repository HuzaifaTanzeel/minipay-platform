# MiniPay

Payments console + REST API + PostgreSQL. Same UI at http://localhost:8080 via Docker Compose **or** Kubernetes (k3d). Do not run both on 8080 at once.

Start Docker Desktop. Copy `.env.example` to `.env` and replace every `CHANGE_ME`. Never commit `.env`.

```powershell
copy .env.example .env
```

How the pieces connect: [ARCHITECTURE.md](ARCHITECTURE.md). Extra commands: [SETUP.md](SETUP.md). AI tools: [AI_USAGE.md](AI_USAGE.md).

The rest of this file is a **walkthrough in task order**. Each section has: what to run, then where the work and evidence are.

---

## 0. Bring the app up

**Compose** (simplest — use this for SQL, CLI, API tests, and UI tests):

```powershell
docker compose up -d --build
docker compose ps
python database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

Wait until `db`, `api`, and `web` are **healthy**. Open http://localhost:8080 and search **`TXN00000001`**. API: http://localhost:8000.

Python tools (API tests, UI tests, CLI) share one venv: [SETUP.md](SETUP.md) §4.

```powershell
.\scripts\setup-venv.ps1
.\.venv\Scripts\Activate.ps1
```

---

## 1. Linux and Git

Repo hygiene: [`.gitignore`](.gitignore) (`.env` is ignored). Commits are incremental; humans own git.

WSL2 host diagnostics (OS, CPU, memory, disk, ports, DNS, in-cluster service): [evidence/linux.md](evidence/linux.md). Command cheat sheet for logs and probes: [kubernetes/RUNBOOK.md](kubernetes/RUNBOOK.md) and [SETUP.md](SETUP.md).

---

## 2. Database and SQL

Schema and seed: [database/schema.sql](database/schema.sql), [database/generate_data.py](database/generate_data.py), [database/README.md](database/README.md). Seed data is not rewritten to make reports easier.

Reports (run against Compose `db` after seed): [sql/README.md](sql/README.md).

| Question | Script |
|---|---|
| Count / value by status and day | [sql/01_count_value_by_status_day.sql](sql/01_count_value_by_status_day.sql) |
| Top 10 customers by SUCCESS value | [sql/02_top10_customers_success.sql](sql/02_top10_customers_success.sql) |
| PROCESSING older than 15 minutes | [sql/03_stuck_processing_15m.sql](sql/03_stuck_processing_15m.sql) |
| Duplicate `transaction_ref` | [sql/04_duplicate_refs.sql](sql/04_duplicate_refs.sql) |
| Daily success rate | [sql/05_daily_success_rate.sql](sql/05_daily_success_rate.sql) |
| SUCCESS vs callback SUCCESS | [sql/06_reconciliation_callbacks.sql](sql/06_reconciliation_callbacks.sql) |
| Average and p95 duration | [sql/07_processing_time_avg_p95.sql](sql/07_processing_time_avg_p95.sql) |

Index change and before/after: [sql/00_indexes_v1.sql](sql/00_indexes_v1.sql), [sql/PERFORMANCE.md](sql/PERFORMANCE.md). Raw timings: [evidence/sql/](evidence/sql/).

Example:

```powershell
Get-Content sql\01_count_value_by_status_day.sql | docker compose exec -T db psql -U minipay -d minipay
```

---

## 3. Kubernetes

On Windows use **Ubuntu (WSL)**, not PowerShell. Docker Desktop → Settings → Resources → WSL integration → enable Ubuntu.

```bash
chmod +x scripts/k8s-*.sh
./scripts/k8s-up.sh
./scripts/k8s-smoke.sh
```

The script installs `kubectl`/`k3d` if missing, may ask for `sudo` once (Docker socket), creates namespace `minipay`, builds a Secret from `.env` (not from committed YAML), applies [kubernetes/overlays/local](kubernetes/overlays/local), and seeds. Lookup **`TXN00000001`** at http://localhost:8080. Pods: `kubectl -n minipay get pods`.

| What | Where |
|---|---|
| Working manifests (Deployments, StatefulSet, Services, ConfigMap, probes, resources, PVC, Ingress) | [kubernetes/base/](kubernetes/base/) |
| Secret shape only (`CHANGE_ME`) | [kubernetes/base/secret.example.yaml](kubernetes/base/secret.example.yaml) |
| Bring-up / tear-down | [scripts/k8s-up.sh](scripts/k8s-up.sh), [scripts/k8s-down.sh](scripts/k8s-down.sh), [scripts/k8s-smoke.sh](scripts/k8s-smoke.sh) |
| Rollout, logs, `get endpoints` | [kubernetes/RUNBOOK.md](kubernetes/RUNBOOK.md) |
| Defects in the original Deployment/Service | [kubernetes/legacy/api-deployment-v0.yaml](kubernetes/legacy/api-deployment-v0.yaml), [investigation/kubernetes-findings.md](investigation/kubernetes-findings.md) |
| Live `kubectl` captures | [evidence/kubernetes/](evidence/kubernetes/) |
| Rancher import and workload ops | [evidence/rancher.md](evidence/rancher.md), [evidence/rancher/](evidence/rancher/) |

**Rancher** (local Docker, optional): import k3d cluster `minipay` as **`minipay-local`**. UI: **`https://localhost:8443`** (MiniPay UI stays on **8080**). On WSL + Docker Desktop, set Global Settings **`server-url`** to **`https://host.docker.internal:8443`** so the cluster agent can reach Rancher. Procedure and screenshots: [evidence/rancher.md](evidence/rancher.md).

---

## 4. Support CLI (L2)

```powershell
python python/support_tool.py --transaction TXN00000001
python python/support_tool.py --transaction TXN00004999 --json
python -m pytest python/tests -q
```

Uses `MINIPAY_DB_DSN` from `.env` (no credentials in code). Design, exit codes, stuck/health extras: [python/README.md](python/README.md).

---

## 5. API and API tests

Compose `api` must be healthy and the database seeded.

```powershell
python -m pytest tests/api -v
```

Service: [backend/](backend/). Coverage, timeouts, 4xx vs 5xx, idempotency: [tests/api/NOTES.md](tests/api/NOTES.md). Saved run: [evidence/api/pytest-api.txt](evidence/api/pytest-api.txt). Duplicate-ref incident curls: [evidence/api/](evidence/api/).

---

## 6. UI tests

Compose **`web`** must be healthy on 8080 (API-only on 8000 is not enough). Database seeded.

```powershell
python -m pytest -c tests/ui/pytest.ini tests/ui -v
```

Watch the browser: add `--headed`. Journeys and CI notes: [tests/ui/README.md](tests/ui/README.md). HTML reports: [evidence/ui/report-before.html](evidence/ui/report-before.html), [evidence/ui/report-after.html](evidence/ui/report-after.html).

---

## 7. Incidents

| Write-up | Topic | Evidence |
|---|---|---|
| [investigation/INCIDENT-001-RCA.md](investigation/INCIDENT-001-RCA.md) | Duplicate `transaction_ref` lookup | [evidence/api/](evidence/api/) |
| [investigation/kubernetes-findings.md](investigation/kubernetes-findings.md) | Broken v0 manifest | [evidence/kubernetes/](evidence/kubernetes/) |
| [investigation/INCIDENT-002-RCA.md](investigation/INCIDENT-002-RCA.md) | v0 deploy: READY 0/1, empty endpoints | [evidence/kubernetes/](evidence/kubernetes/) |
| [investigation/INCIDENT-003-RCA.md](investigation/INCIDENT-003-RCA.md) | Slow search at volume | [evidence/sql/](evidence/sql/) |

Index of post-mortems: [investigation/README.md](investigation/README.md).

---

## Optional

Prometheus + Grafana: [observability/README.md](observability/README.md) (`docker compose --profile observability up -d`).

---

## License

MIT. See [LICENSE](LICENSE).
