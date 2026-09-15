---
name: minipay-conventions
description: >-
  MiniPay platform conventions for FastAPI, PostgreSQL, config, logging, and
  HTTP behaviour. Use when adding or changing API routes, UI pages, database
  access, Docker/env config, health probes, error responses, or idempotent
  payments. Do not use for git commits, pull requests, or tags.
---

# MiniPay conventions

Apply these invariants. Do not invent a second stack or a second error format.

## Stack
- Python 3.12, FastAPI, psycopg 3, parameterised SQL (no ORM for payment queries).
- Server-rendered Jinja2 UI from the same app. No separate frontend build.
- PostgreSQL 16. Config via environment / pydantic-settings only.

## HTTP and errors
- `POST` create → 201; idempotent replay of the same payment payload → 200 plus `Idempotent-Replay: true`; same reference, different payload → 409.
- Auth: `X-API-Key` on `/api/*`. `/health` and `/ready` stay unauthenticated.
- Envelope: `{"error":{"code":"...","message":"...","request_id":"..."}}`.
- Echo `X-Request-ID` (incoming or generated) on every response and log line.

## Health
- `/health` = process alive (liveness probe).
- `/ready` = database ping with a short timeout (readiness probe) → 503 if DB is down.
- Never point liveness at `/ready`.

## Data and SQL
- Parameterised queries only (`%s`). No f-strings or string concatenation of user input.
- Do not `UPDATE`/`DELETE` seed data to make reports easier.
- Duplicate `transaction_ref` values exist in seed data; do not assume uniqueness in the schema.

## Secrets
- Never hard-code credentials. Never commit `.env`. Use `.env.example` placeholders only.
- Kubernetes: non-secrets in ConfigMaps; credentials in Secrets via `secretKeyRef` / `envFrom`.

## After generating code
- Point at files changed. Suggest how to verify (`curl`, `pytest`) but do not run git commit.
