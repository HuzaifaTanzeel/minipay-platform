# Kubernetes findings (v0 manifest)

Source: [kubernetes/legacy/api-deployment-v0.yaml](../kubernetes/legacy/api-deployment-v0.yaml). That file is the first-release attempt. Do not apply it to namespace `minipay`. Working manifests are under `kubernetes/base/` (named port `http` on **8000**, matching the API process).

Detection commands assume the v0 objects were applied in a throwaway namespace (for example `minipay-legacy`) with only the image name substituted.

| # | Line | Defect | Symptom | How to detect | Severity | Fix |
|---|---|---|---|---|---|---|
| 1 | 22 | Placeholder image `YOUR_IMAGE_HERE` | ImagePullBackOff; pod never starts | `kubectl -n minipay-legacy get pods`; `describe pod` Events | P1 | Pin a real tag (`minipay-api:1.0.0`) and `imagePullPolicy: IfNotPresent` for k3d import |
| 2 | 24, 37 | `containerPort` / liveness use **8080**; process listens on **8000** | Probe connection refused even if the app is up | `kubectl describe pod` Liveness; app Dockerfile `EXPOSE 8000` | P1 | Named port `http: 8000`; probes and Service target that name |
| 3 | 31 | Readiness `httpGet.port: 8081` (nothing listens) | Pod Running, **READY 0/1**; never added to Service | `describe pod` Readiness: connection refused :8081 | P1 | Readiness port `http`; path `/ready` (DB ping), not `/health` |
| 4 | 48 | Service selector `app: minipay-backend`; pods labeled `app: minipay-api` | Endpoints empty even after Ready | `kubectl get endpoints minipay-api`; `describe svc` vs pod labels | P1 | Selector `app: minipay-api` |
| 5 | 51 | Service `targetPort: 8081` | Traffic that did reach a pod still hits the wrong port | `get endpoints` then curl through the Service | P1 | `targetPort: http` (named) |
| 6 | 9, 45 | Namespace `minipay` on objects but no Namespace manifest | `kubectl apply` fails: namespace not found | `kubectl apply -f …` error | P2 | `kubernetes/base/namespace.yaml` applied first |
| 7 | 25–27 | Only `DB_HOST`; no `DATABASE_URL` / `API_KEY` | CrashLoopBackOff: Settings validation at import | `kubectl logs --previous` | P1 | Secret `minipay-secrets` + ConfigMap; `envFrom` |
| 8 | 30, 36 | Liveness and readiness both `/health` | DB outage does not make the pod unready; kube-proxy still sends traffic. A liveness `/ready` would restart on DB blips | Compare probe paths to `/health` vs `/ready` in the API | P2 | Liveness `/health`; readiness `/ready` |
| 9 | 32 | `initialDelaySeconds: 2` on readiness | False NotReady while uvicorn/DB still starting | Rapid Ready flip in `describe pod` | P3 | `initialDelaySeconds: 5` on readiness |
| 10 | (absent) | No `resources` | Noisy neighbour; no eviction/QoS signal | `kubectl describe pod` (no Limits) | P2 | requests/limits on API, UI, Postgres |
| 11 | (absent) | No `securityContext` | Process can run as root if the image allows it | `describe pod`; image `USER` | P2 | API image already `USER 10001` in the Dockerfile; working YAML does not add extra `securityContext` |
| 12 | (absent) | No `imagePullPolicy` / pinned tag | `:latest` surprise pulls | Image field | P3 | Tag `1.0.0`; overlay `images:` |
| 13 | (absent) | No rollingUpdate / `maxUnavailable` | All replicas can drop during a rollout | `kubectl get deploy -o yaml` | P3 | Overlay runs 1 replica; `kubectl -n minipay scale` / `rollout` in the runbook |

**Prevention:** name the container port (`http`) and point probes and `targetPort` at that name so 8080/8081/8000 cannot drift. `kubectl get endpoints` is the thirty-second check for selector/probe mistakes. `kubectl apply -k` plus `rollout status --timeout` is the deploy gate.

Working stack: Postgres **ClusterIP only** (not on the k3d load balancer). Ingress to `minipay-web` only. Credentials in a Secret created on the cluster, never committed.
