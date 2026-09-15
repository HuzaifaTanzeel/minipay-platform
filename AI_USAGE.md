# AI usage

Cursor helped draft code, docs, and commands. I ran Compose, curl, and the UI myself, reviewed every file, and I make every git commit and pull request.

## Tools

- Cursor (agent chat in the MiniPay workspace)

## Where I used it

| Workstream | What the model drafted | What I kept / changed |
|---|---|---|
| Docs | README / SETUP wording, Compose commands | Edited to match what actually runs locally |
| Database | Compose + seed commands | Ran seed and `psql` checks myself; did not commit `.env` or generated SQL |
| API | FastAPI layout (config, pool, routers, services, repositories) | Kept parameterised SQL, env-only config, `/health` vs `/ready`, JSON error envelope |
| UI | React + Vite + shadcn pages (dashboard, payments, customers, create payment) | Chose a separate SPA after first trying a server-rendered UI; kept `data-testid`s for later Playwright |
| Docker | API image, nginx image, Compose `web` service | Made `web` start with default `docker compose up` (not a profile). API key is injected by nginx, not the browser bundle |

## Representative interactions

1. **Task:** Bootstrap the HTTP API on the existing Postgres seed.
   **Prompt (abridged):** “Build FastAPI with health/ready, API-key auth, payments and customers, structured logs, and a request-id error envelope.”
   **Used:** yes, as the starting layout.
   **Validation:** `docker compose up --build`; curl `/health`, `/ready`, create/lookup payments.

2. **Task:** Replace a co-hosted UI with a React SPA.
   **Prompt (abridged):** “Split backend and frontend folders; shadcn + Tailwind; list/filter APIs; proxy so the API key never ships to the browser.”
   **Used:** yes.
   **Validation:** UI at http://localhost:8080; `/api/stats` through nginx without sending a key from curl; list/filter pages load against the 50k-row seed.

3. **Task:** Run the frontend from Compose, not `npm run dev`.
   **Prompt (abridged):** “Frontend should also run from docker compose.”
   **Used:** yes (nginx multi-stage image + Compose `web` service).
   **Validation:** `docker compose ps` shows `web` healthy; GET `/` → 200 on port 8080.

4. **Task:** Explain the request path.
   **Prompt (abridged):** “Are we using a reverse proxy, and what is the flow?”
   **Used:** as an explanation I checked against `nginx.conf.template` and `docker-compose.yml`.

## How I validated generated output

- Read every new Python/TS/YAML file before keeping it.
- `docker compose up -d --build` for `db`, `api`, and `web`.
- curl: `/health`, `/ready`, missing/wrong API key, create customer/payment, idempotent replay, conflict, `GET /api/payments/TXN00004999`.
- Browser: dashboard, payments filters, customer list/detail, new payment form.
- Confirmed `.env` and seed dumps are not tracked.

## Where I corrected or rejected AI output

1. **pgAdmin email.** Suggested `admin@minipay.local`; pgAdmin 8 rejected it. I set `PGADMIN_EMAIL=admin@example.com` and recreated the container.

2. **API key in the frontend bundle.** A simple approach is `VITE_API_KEY` sent from the browser. I rejected that. Vite (dev) and nginx (Compose) inject `X-API-Key` on proxied `/api` requests so the key stays server-side.

3. **Compose profile for the UI.** The first Compose snippet hid `web` behind a profile, so `docker compose up` did not start the UI. I dropped the profile and wait for `api` to be healthy before starting nginx.

4. **Unique constraint on `transaction_ref`.** An obvious schema “fix” is `UNIQUE(transaction_ref)`. That fails on the seed (duplicate refs such as `TXN00004999`). Lookup currently returns 500 for those refs; I left that behaviour in place so it can be investigated properly rather than papered over.

5. **PowerShell JSON bodies.** Suggested inline `curl -d "{...}"` broke under PowerShell quoting. I sent JSON via temp files (`--data "@pay.json"`) instead.

## What I did without the model

- Decided the SPA talks only to `/api` on the same origin (nginx), not directly to `:8000`.
- Confirmed duplicate-reference lookups still 500 (`TXN00004999`) after the split.
- Chose not to rewrite seed data to make reports or the UI easier.
