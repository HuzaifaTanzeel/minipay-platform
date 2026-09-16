# MiniPay L2 support CLI

Diagnose a payment from Postgres when the API is down or returning 500. The
CLI does not call `GET /api/payments/{ref}` — it loads **every** row for a
`transaction_ref` (seed data contains a few duplicates) and scores anomaly rules.

```text
python/support_tool.py          entrypoint
python/support_tool/
  cli.py                        argparse + wiring
  commands.py                   use cases
  analysis.py                   rule registry (no I/O)
  db.py / api.py                Postgres and HTTP adapters
  ports.py                      TransactionStore, HealthChecker, Clock
```

## Install

Use the repo venv (same install as API and UI tests). From the repository root:

```powershell
.\scripts\setup-venv.ps1
.\.venv\Scripts\Activate.ps1
```

CLI-only deps are [requirements.txt](requirements.txt); the bootstrap installs them via the root [requirements-dev.txt](../requirements-dev.txt). Do not pip-install into the system interpreter.

## Configuration

Never put credentials in code. Precedence: `--config` INI, then environment,
then `%USERPROFILE%\.minipay\support.ini` (Linux: `~/.minipay/support.ini`),
then defaults.

| Variable | INI key | Required | Default |
|---|---|---|---|
| `MINIPAY_DB_DSN` | `db_dsn` | yes (any DB command) | — |
| `MINIPAY_API_URL` | `api_url` | no | `http://localhost:8000` |
| `MINIPAY_API_KEY` | `api_key` | no | unset (`/health` and `/ready` do not need it) |
| `MINIPAY_TIMEOUT` | `timeout` | no | `3` (seconds) |
| `MINIPAY_STUCK_MINUTES` | `stuck_minutes` | no | `15` |

INI file:

```ini
[minipay]
db_dsn = postgresql://minipay:CHANGE_ME@localhost:5432/minipay
api_url = http://localhost:8000
timeout = 3
stuck_minutes = 15
```

PowerShell (Compose Postgres on localhost:5432):

```powershell
$env:MINIPAY_DB_DSN = "postgresql://minipay:<password>@localhost:5432/minipay"
$env:MINIPAY_API_URL = "http://localhost:8000"
```

## Commands

```powershell
python python/support_tool.py --transaction TXN00000001
python python/support_tool.py --transaction TXN00004999 --json
python python/support_tool.py --stuck-summary
python python/support_tool.py --failed-summary
python python/support_tool.py --health
python python/support_tool.py --help
```

`--json` writes only the report to stdout (pipe to `jq`). Logs go to stderr.
`-v` turns on DEBUG.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | found / healthy, no anomalies |
| 1 | transaction reference not found |
| 2 | found, but one or more anomalies |
| 3 | missing config, or database/API probe failed |
| 130 | interrupted (`Ctrl+C`) |

`--transaction TXN00004999` is expected to exit **2** (`DUPLICATE_REFERENCE`)
while `GET /api/payments/TXN00004999` still returns 500.

## Sample text (`--transaction TXN00000001`)

Live seeded database:

```text
TRANSACTION
  id:              1
  transaction_ref: TXN00000001
  amount:          11221.97
  status:          SUCCESS
  failure_code:    -

CUSTOMER
  customer_ref:    CUST000655
  name:            Customer 655
  customer_id:     655

TIMELINE
  created_at:      2026-09-09 23:59:32
  completed_at:    2026-09-10 00:00:01
  duration:        0:00:29

CALLBACKS
  attempt 1: HTTP 200 SUCCESS at 2026-09-10 00:00:06

ANOMALIES
  (none)

RECOMMENDATION
  No anomalies detected. No action required.
```

## Sample (`--transaction TXN00004999`)

Same database. The API still returns 500 for this ref; the CLI loads both rows (exit 2):

```text
TRANSACTION
  id:              4999
  transaction_ref: TXN00004999
  amount:          79632.16
  status:          FAILED
  failure_code:    UPSTREAM_ERROR
  ...
ANOMALIES
  [HIGH] DUPLICATE_REFERENCE: reference shared by transaction ids [4999, 5000]
  [INFO] FAILED_UPSTREAM: UPSTREAM_ERROR
  duplicate ids: [4999, 5000]

RECOMMENDATION
  Escalate to L3: identify canonical transaction, void the other, enforce uniqueness at ingestion.
```

`--json` uses the same fields (`transaction`, `callbacks`, `anomalies`, `recommendation`, `duplicate_ids`). Amounts and timestamps are strings so the document stays `jq`-friendly.

## Tests

No live Postgres required (in-memory fakes implement the same ports):

```powershell
python -m pytest python/tests -q
# 29 passed
```

## Anomaly rules

| Code | Severity | When |
|---|---|---|
| `DUPLICATE_REFERENCE` | HIGH | more than one row shares the ref |
| `STUCK_PROCESSING` | HIGH | PROCESSING, no `completed_at`, older than N minutes |
| `COMPLETED_BEFORE_CREATED` | HIGH | `completed_at` before `created_at` |
| `SUCCESS_WITHOUT_CALLBACK` | MEDIUM | SUCCESS with no SUCCESS callback |
| `CALLBACK_RETRIES_EXHAUSTED` | MEDIUM | at least three callbacks, all FAILED |
| `FAILED_UPSTREAM` / `FAILED` | INFO | FAILED with a `failure_code` |
