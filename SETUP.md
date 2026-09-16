# Setup

How to run what this repository currently ships. Credentials live in `.env` (copy from `.env.example`). Never commit `.env`, tokens, or private keys.

**Current scope:** PostgreSQL 16, FastAPI, and the React UI via Docker Compose, plus schema, synthetic seed, SQL reports, optional pgAdmin, and the L2 support CLI. Kubernetes manifests and API/UI automated tests are not in this tree yet.

## Prerequisites

- Docker Desktop (or compatible Compose v2)
- Python 3 on the PATH (`python` or `py` on Windows)

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

Keep `DB_NAME=minipay` and `DB_USER=minipay`.

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

## 4. L2 support CLI

Install CLI deps (once), then point it at the same database as Compose:

```powershell
python -m pip install -r python/requirements.txt
$env:MINIPAY_DB_DSN = "postgresql://minipay:<password>@localhost:5432/minipay"
python python/support_tool.py --transaction TXN00000001
python python/support_tool.py --transaction TXN00004999 --json
python -m pytest python/tests -q
```

Use the same password as `DB_PASSWORD` in `.env`. Config, exit codes, and sample output: [python/README.md](python/README.md).

## 5. Optional pgAdmin

```powershell
docker compose --profile tools up -d
```

Open http://localhost:5050. Register a server with host **`db`**, port `5432`. Details: [database/README.md](database/README.md).

## Teardown

```powershell
docker compose --profile tools down
```

Data remains in the `pgdata` volume. To delete schema and seed:

```powershell
docker compose down -v
```

## What is not set up yet

Kubernetes, Rancher, and API/UI pytest suites. Those will be documented here as they land. Full layout (architecture, AI usage, investigation, tests, evidence) is listed in the repository root README.
