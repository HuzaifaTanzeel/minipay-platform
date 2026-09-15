# Agent notes (MiniPay)

This repo is a small payment-processing platform (API, UI, PostgreSQL, Kubernetes, tests, L2 tooling).

## Ownership
- Humans own Git: branches, commits, pull requests, tags, and merges.
- Agents may draft code, tests, and docs. They must not commit, push, or open PRs unless the human explicitly asks in that turn.

## Skills
Project skills live in `.cursor/skills/`. Read the matching skill before generating API/SQL/Kubernetes/incident text. Run `repo-hygiene` before claiming a change is ready to push.

## Invariants
- Configuration and credentials come from environment variables or Kubernetes Secrets, never hard-coded values.
- SQL is parameterised. Do not interpolate user input into queries.
- `/health` is liveness (process). `/ready` is readiness (dependencies).
- JSON error envelope: `{"error":{"code","message","request_id"}}`.
- Do not rewrite seed data to make reports easier.
