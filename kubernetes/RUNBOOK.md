# Kubernetes runbook

Cluster: **k3d** (not Minikube). Namespace `minipay`. Day-to-day bring-up is `./scripts/k8s-up.sh` (Secret from `.env`, apply overlay, seed). Equivalent apply: `kubectl apply -k kubernetes/overlays/local` after `minipay-secrets` exists. Postgres is ClusterIP-only; Ingress points at `minipay-web`. Smoke: `./scripts/k8s-smoke.sh`. Tear down: `./scripts/k8s-down.sh`.

## Status

```bash
kubectl -n minipay get all,ingress,endpoints
kubectl -n minipay rollout status statefulset/minipay-db
kubectl -n minipay rollout status deploy/minipay-api
kubectl -n minipay rollout status deploy/minipay-web
kubectl -n minipay wait --for=condition=complete job/minipay-schema-init --timeout=120s
```

`minipay-db` Service must be `type: ClusterIP` with no `nodePort`. `get endpoints minipay-api` must list pod IPs, not `<none>`.

## Rollout

```bash
kubectl -n minipay rollout status deploy/minipay-api --timeout=120s
kubectl -n minipay rollout history deploy/minipay-api
kubectl -n minipay rollout undo deploy/minipay-api
kubectl -n minipay rollout restart deploy/minipay-api
kubectl -n minipay scale deploy/minipay-api --replicas=2
```

## Logs and crashes

```bash
kubectl -n minipay logs deploy/minipay-api --tail=50
kubectl -n minipay logs deploy/minipay-api --previous --tail=50
kubectl -n minipay describe pod -l app=minipay-api
```

**CrashLoopBackOff:** `logs --previous` first. Missing `DATABASE_URL` / `API_KEY` fails at import. OOMKilled is on `describe` (Last State).

**Running but READY 0/1:** readiness probe. `describe` Events. Connection refused on the wrong port is the v0 defect (8081). Empty `get endpoints` is a selector mismatch.

## Database (in-cluster only)

```bash
kubectl -n minipay exec -it minipay-db-0 -- psql -U minipay -d minipay
```

Re-run schema Job after a wipe: `kubectl -n minipay delete job minipay-schema-init` then `kubectl apply -k kubernetes/overlays/local`.

```bash
python database/generate_data.py | kubectl -n minipay exec -i minipay-db-0 -- psql -U minipay -d minipay -v ON_ERROR_STOP=1
```

## Port-forward (if Ingress is awkward)

```bash
kubectl -n minipay port-forward svc/minipay-web 8080:80
```

## INCIDENT-002 capture (throwaway namespace)

Substitute only the image name. Do not use this as the live `minipay` deploy.

```bash
kubectl create ns minipay-legacy
sed 's#YOUR_IMAGE_HERE#minipay-api:1.0.0#; s#namespace: minipay$#namespace: minipay-legacy#' kubernetes/legacy/api-deployment-v0.yaml | kubectl apply -f -
kubectl -n minipay-legacy get pods
kubectl -n minipay-legacy describe pod -l app=minipay-api
kubectl -n minipay-legacy get endpoints minipay-api
kubectl -n minipay-legacy logs -l app=minipay-api --tail=20
```

Save that output under `evidence/kubernetes/` (READY 0/1, probe :8081, endpoints `<none>`). Then write `investigation/INCIDENT-002-RCA.md`. Delete with `kubectl delete ns minipay-legacy`.
