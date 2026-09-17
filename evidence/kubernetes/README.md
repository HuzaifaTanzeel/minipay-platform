# Evidence from kubectl

Live captures for INCIDENT-002. Working stack is namespace `minipay`. The v0 manifest was applied only in throwaway `minipay-legacy` (now deleted).

| File | Namespace | Contents |
|---|---|---|
| [working-get-pods.txt](working-get-pods.txt) | minipay | `get pods,endpoints` — API 1/1, endpoints have pod IPs |
| [v0-get-pods.txt](v0-get-pods.txt) | minipay-legacy | `get pods -o wide` — 0/1 Error |
| [v0-describe-pod.txt](v0-describe-pod.txt) | minipay-legacy | probes :8080 / :8081, env `DB_HOST` only |
| [v0-endpoints.txt](v0-endpoints.txt) | minipay-legacy | `<none>`; selector `minipay-backend` |
| [v0-logs.txt](v0-logs.txt) | minipay-legacy | Settings missing `DATABASE_URL` / `API_KEY` |
| [incident-002-legacy-pods-fixed.png](incident-002-legacy-pods-fixed.png) | minipay-legacy | After YAML fix: 1/1 Running, endpoints on :8000 |

Commands: [kubernetes/RUNBOOK.md](../../kubernetes/RUNBOOK.md). RCA: [investigation/INCIDENT-002-RCA.md](../../investigation/INCIDENT-002-RCA.md).
