# AI usage

I used Cursor while building this. I still ran everything locally, edited what it generated, and made the git commits / PRs myself.

## Tools

- Cursor

## What I used it for

- First drafts of README / SETUP / database notes
- Backend + UI scaffolding
- SQL queries and “what should EXPLAIN look like” questions
- The L2 CLI under `python/`
- Commit message / PR wording
- Created API and UI Tests using Cursor, also created a negative Scneario to verify that the test fails by removing greater than 0 check on Payment page.
- Created Grafana Dashbaord

## Some actual asks

- How do I record `EXPLAIN (ANALYZE, BUFFERS)` so before/after is comparable, not just “it got faster”
- Build a support CLI that still works if the API is down or lookup fails
- SETUP commands that work in PowerShell, not only bash



## How I checked it

I don’t merge AI output blindly. For the CLI I ran `python -m pytest python/tests -q` (29 passed) and then against my local db:

- `TXN00000001` — normal SUCCESS, no anomalies
- `TXN00004999` — duplicate, ids 4999 and 5000
- `--health` and `--stuck-summary` as well

Same for SQL: I ran the statements in psql, not just from the chat.

## Something I changed

First version of the CLI called `GET /api/payments/{ref}`. That is useless for `TXN00004999` because the API 500s. I made it query Postgres and return every matching row instead, so you still get the duplicate warning and a next step.