# MiniPay

Small payment-processing platform: a REST API and web UI in front of PostgreSQL, with Kubernetes deployment, automated tests, SQL investigation, and L2 support tooling. Built to practise reproducible local/K8s setups, safe config and secrets, and operational documentation.

**Status:** local PostgreSQL, FastAPI, and React UI via Docker Compose, schema, seed, SQL reports, L2 support CLI, optional pgAdmin. Cluster manifests are not in the default path yet.

## Quick start

```powershell
copy .env.example .env
# set DB_PASSWORD, API_KEY (and matching URLs) in .env — do not commit .env
docker compose up -d --build
python database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

UI: http://localhost:8080. API: http://localhost:8000.

Full steps: [SETUP.md](SETUP.md). Database notes: [database/README.md](database/README.md).

## Repository layout

| Path | Purpose |
|---|---|
| [SETUP.md](SETUP.md) | Run what exists today |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components and data flow (current + planned) |
| [AI_USAGE.md](AI_USAGE.md) | How AI tools were used and validated |
| `database/` | Schema, seed generator, Compose init extras |
| `backend/` | FastAPI service |
| `frontend/` | React UI (served by nginx in Compose) |
| `sql/` | Reporting queries and performance notes |
| `kubernetes/` | Cluster manifests (planned) |
| [python/](python/README.md) | L2 support CLI (`python python/support_tool.py --transaction REF`) |
| `tests/api/`, `tests/ui/` | Automated tests (planned) |
| `investigation/` | Incident post-mortems (planned) |
| `evidence/` | Command output and redacted screenshots (planned) |

## Conventions

Humans own git (commits, PRs, tags). Cursor project skills live under `.cursor/skills/` (platform conventions, RCA shape, repo hygiene scan). Configuration is environment-based; no secrets in YAML or git.

## License

MIT. See [LICENSE](LICENSE).
