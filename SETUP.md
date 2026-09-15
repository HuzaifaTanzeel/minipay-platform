# Setup

How to run what this repository currently ships. Credentials live in `.env` (copy from `.env.example`). Never commit `.env`, tokens, or private keys.

**Current scope:** PostgreSQL 16 via Docker Compose, schema, synthetic seed, optional pgAdmin. The HTTP API, UI, Kubernetes manifests, automated tests, and support CLI are not in this tree yet.

## Prerequisites

- Docker Desktop (or compatible Compose v2)
- Python 3 on the PATH (`python` or `py` on Windows)

## 1. Environment file

```powershell
copy .env.example .env
```

Set at least:

- `DB_PASSWORD` — used by Compose for Postgres
- `DATABASE_URL` and `MINIPAY_DB_DSN` — same password as `DB_PASSWORD`
- `PGADMIN_PASSWORD` — if you start the `tools` profile
- `PGADMIN_EMAIL` — must be a normal address (for example `admin@example.com`). Values like `user@minipay.local` are rejected by pgAdmin 8.

Keep `DB_NAME=minipay` and `DB_USER=minipay`.

## 2. Start the database

```powershell
docker compose up -d db
docker compose ps
```

`db` must show **healthy**. If `docker compose config` errors with `Set DB_PASSWORD in .env`, `.env` is missing or `DB_PASSWORD` is empty.

## 3. Seed

```powershell
python database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

Checks and expected counts: [database/README.md](database/README.md).

## 4. Optional pgAdmin

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

API, UI, `sql/` reporting scripts, Kubernetes, Rancher, pytest, and the Python support tool. Those will be documented here as they land. Full submission layout (architecture, AI usage, investigation, tests, evidence) is listed in the repository root README.
