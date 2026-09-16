# Setup

How to run what this repository currently ships. Credentials live in `.env` (copy from `.env.example`). Never commit `.env`, tokens, or private keys.

**Current scope:** PostgreSQL 16, FastAPI, and the React UI via Docker Compose, plus schema, synthetic seed, SQL reports, optional pgAdmin, optional Prometheus/Grafana, the L2 support CLI, API pytest, and Playwright UI tests. Kubernetes manifests are not in this tree yet.

Python tooling (API tests, UI tests, CLI tests, ruff) is installed into **`.venv`**. Do not `pip install` into the system interpreter.

## Prerequisites

- Docker Desktop (or compatible Compose v2)
- Python 3.12 on the PATH (`python` or `py` on Windows)
- Ability to create a virtualenv (`python -m venv`)

## 1. Environment file

```powershell
copy .env.example .env
```

Set at least:

- `DB_PASSWORD` — used by Compose for Postgres
- `API_KEY` — injected by the `web` nginx proxy into `/api` requests (never shipped in the browser bundle)
- `DATABASE_URL` and `MINIPAY_DB_DSN` — same password as `DB_PASSWORD`
- `PGADMIN_PASSWORD` — if you start the `tools` profile
- `PGADMIN_EMAIL` — must be a normal address (for example `admin@example.com`). Values like `user@minipay.local` are rejected by pgAdmin 8.
- `GRAFANA_ADMIN_PASSWORD` — Grafana admin password when you start the `observability` profile (defaults to `CHANGE_ME` if unset)

Keep `DB_NAME=minipay` and `DB_USER=minipay`. `MINIPAY_BASE_URL` defaults to the API (`http://localhost:8000`); `MINIPAY_UI_URL` defaults to the Compose UI (`http://localhost:8080`).

## 2. Start the stack

```powershell
docker compose up -d --build
docker compose ps
```

`db`, `api`, and `web` must show **healthy**. The UI is at http://localhost:8080; the API is at http://localhost:8000.

If `docker compose config` errors with `Set DB_PASSWORD in .env` or `Set API_KEY in .env`, `.env` is missing or those values are empty.

## 3. Seed

```powershell
python database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

Checks and expected counts: [database/README.md](database/README.md).

## 4. Python virtualenv (once)

One file, one venv, all pytest suites:

```powershell
.\scripts\setup-venv.ps1
.\.venv\Scripts\Activate.ps1
```

Linux / WSL:

```bash
chmod +x scripts/setup-venv.sh
./scripts/setup-venv.sh
source .venv/bin/activate
```

The script creates `.venv` if needed, installs [requirements-dev.txt](requirements-dev.txt) (API + UI + CLI + ruff), and downloads Playwright’s Chromium. Playwright browsers are not on PyPI; that last step cannot live in the requirements file.

Already have a venv and only need to refresh deps:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

If `Activate.ps1` is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 5. L2 support CLI

With the venv activated, point the CLI at the same database as Compose:

```powershell
$env:MINIPAY_DB_DSN = "postgresql://minipay:<password>@localhost:5432/minipay"
python python/support_tool.py --transaction TXN00000001
python python/support_tool.py --transaction TXN00004999 --json
python -m pytest python/tests -q
```

Use the same password as `DB_PASSWORD` in `.env`. Config, exit codes, and sample output: [python/README.md](python/README.md).

## 6. API tests

Compose `api` must be healthy and the database seeded. Venv activated:

```powershell
python -m pytest tests/api -v
```

`API_KEY` is taken from `.env` if you do not export it. Timeouts, retries, and 4xx vs 5xx: [tests/api/NOTES.md](tests/api/NOTES.md).

Stopping Postgres for `/ready` 503 is skipped unless you set `MINIPAY_ALLOW_DESTRUCTIVE=1` (the suite restarts `db` afterwards).

## 7. UI tests

Run every command below from the **repository root**, with the venv activated (step 4). Compose **`web`** must be healthy on http://localhost:8080 (API-only on 8000 is not enough).

**Headless** (default — no browser window; same as CI). Writes [evidence/ui/report.html](evidence/ui/report.html):

```powershell
python -m pytest -c tests/ui/pytest.ini tests/ui -v
```

**Headed** (Chromium window opens so you can watch the five journeys):

```powershell
python -m pytest -c tests/ui/pytest.ini tests/ui -v --headed
```

**Headed, slowed down** (easier to see clicks and navigation):

```powershell
python -m pytest -c tests/ui/pytest.ini tests/ui -v --headed --slowmo 400
```

One journey only (negative amount):

```powershell
python -m pytest -c tests/ui/pytest.ini tests/ui/test_journeys.py::test_create_payment_invalid_amount_shows_validation -v --headed --slowmo 400
```

Linux / WSL (headless): `make test-ui` after `make setup-venv`. Headed on WSL needs a display (WSLg or an X server); on Windows run the PowerShell commands above instead.

Expect **5 passed**. Saved HTML reports (open in a browser, no extra server): [report-before.html](evidence/ui/report-before.html) (1 failed, before the amount check) vs [report-after.html](evidence/ui/report-after.html) (5 passed). Page objects and env vars: [tests/ui/README.md](tests/ui/README.md).

## 8. Optional pgAdmin

```powershell
docker compose --profile tools up -d
```

Open http://localhost:5050. Register a server with host **`db`**, port `5432`. Details: [database/README.md](database/README.md).

## 9. Optional Prometheus and Grafana

Not part of the default `docker compose up`. After the core stack is healthy:

```powershell
docker compose --profile observability up -d --build
```

Set `GRAFANA_ADMIN_PASSWORD` in `.env` (see `.env.example`); if unset, Grafana uses `CHANGE_ME`.

| URL | Login |
|---|---|
| http://localhost:3000 | Grafana — `admin` / `GRAFANA_ADMIN_PASSWORD` |
| http://localhost:9090 | Prometheus (no login) |
| http://localhost:8000/metrics | API scrape target (no API key) |

The MiniPay overview dashboard is editable (delete panels, change PromQL, Save). UI edits survive restart; `docker compose down -v` wipes them. Percentiles vs averages, datasources, and the later Kubernetes mapping: [observability/README.md](observability/README.md).

## Teardown

```powershell
docker compose --profile tools --profile observability down
```

Data remains in the `pgdata` volume (Grafana UI edits stay in `grafana-data`). To delete schema, seed, and Grafana’s saved dashboards:

```powershell
docker compose down -v
```

## Troubleshooting

| Symptom | What to check |
|---|---|
| `Activate.ps1` cannot be loaded | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again |
| `playwright` / browser missing | Re-run `python -m playwright install chromium` inside `.venv`. On Linux/WSL use `python -m playwright install --with-deps chromium` |
| UI tests: connection refused on 8080 | `docker compose ps` — `web` must be **healthy**. API on 8000 is a different process |
| UI tests: `TXN00000001` not found | Seed has not been loaded (step 3) |
| API tests: missing `API_KEY` | Copy `.env.example` to `.env` and set `API_KEY` |
| Mix-up of 8000 vs 8080 | `MINIPAY_BASE_URL` = API (8000). `MINIPAY_UI_URL` = console (8080) |
| `docker compose config` asks for `DB_PASSWORD` / `API_KEY` | `.env` missing or those values empty |
| `--headed` but no Chromium window | Run the PowerShell commands on Windows. WSL headed mode needs WSLg or an X server |

## What is not set up yet

Kubernetes and Rancher. Those will be documented here as they land. Full layout (architecture, AI usage, investigation, tests, evidence) is listed in the repository root README.
