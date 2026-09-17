# Rancher — import and operations (k3d minipay-local)

Rancher v2.15.1 in Docker; k3d cluster **`minipay`** imported as **`minipay-local`**.  
`server-url` set to **`https://host.docker.internal:8443`** so the cluster agent inside k3d can reach Rancher on Docker Desktop (WSL).

---

## Setup

```bash
docker run -d --name rancher --restart=unless-stopped --privileged \
  -p 8081:80 -p 8443:443 \
  rancher/rancher:latest

docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

Browser: **`https://localhost:8443`** (HTTPS required on port 8443).

Import: **Cluster Management → Import Existing → Generic → minipay-local → Create**, then apply the manifest on k3d:

```bash
kubectl config use-context k3d-minipay

curl --insecure -sfL https://host.docker.internal:8443/v3/import/<REDACTED>.yaml | kubectl apply -f -
```

Import troubleshooting (WSL + k3d):

- Agent with `CATTLE_SERVER=https://localhost:8443` failed: `ping is not accessible` (localhost inside pod ≠ host).
- `host.k3d.internal` failed: `Could not resolve host`.
- **`host.docker.internal`** resolved to `192.168.65.254` from pods; agent connected (`Connected to proxy`).

---

## Cluster dashboard

Active imported cluster: 2 nodes, 10 deployments, capacity (pods/CPU/memory), component health (Etcd, Scheduler, Cattle, Fleet).

![Cluster dashboard](rancher/01-cluster-dashboard.png)

---

## Workloads overview

User namespaces: **minipay** — 2 Deployments, 1 Job, 1 StatefulSet, 4 Pods (3 Running, 1 Completed).

![Workloads overview](rancher/02-workloads-overview.png)

---

## Deployments (minipay namespace)

`minipay-api` and `minipay-web` — Active, Ready 1/1.

![Deployments](rancher/03-deployments-minipay.png)

---

## Job — schema init

`minipay-schema-init` — Completed 1/1 (postgres:16-alpine).

![Schema init job](rancher/04-job-schema-init.png)

---

## StatefulSet — database

`minipay-db` — Active, Ready 1/1 (postgres:16-alpine, PVC).

![StatefulSet minipay-db](rancher/05-statefulset-minipay-db.png)

---

## Pods (minipay namespace)

Pod status: `minipay-api`, `minipay-web`, `minipay-db-0` Running; `minipay-schema-init` Completed.

![Pods](rancher/06-pods-minipay.png)

---

## Pod logs

*(Screenshot pending: Workloads → Pods → minipay-api → Logs.)*

---

## Environment / config

*(Screenshot pending: Deployments → minipay-api → Config → Environment.)*

---

## Scale and rollout (kubectl verification)

After scale/redeploy in Rancher UI:

```bash
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ kubectl -n minipay get pods -l app=minipay-api
kubectl -n minipay rollout status deploy/minipay-api --timeout=120s
kubectl -n minipay get deploy minipay-api
NAME                           READY   STATUS    RESTARTS   AGE
minipay-api-7d85dbd44c-62bsq   1/1     Running   0          89m
deployment "minipay-api" successfully rolled out
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
minipay-api   1/1     1            1           15h
```

*(Add screenshots after scaling minipay-api to 3 replicas and Redeploy in Rancher.)*

---

## Nodes — resource usage

*(Screenshot pending: Cluster → Nodes.)*

---

## What Rancher adds over kubectl

Rancher provides a single UI to inspect and operate imported clusters without memorizing kubectl flags: cluster health and capacity, workload state across namespaces, pod logs, env/Secret references, scale, and redeploy. It also supports multi-cluster management, RBAC/projects for team access, and an audit trail of UI actions — useful for operators who are not full-time on the CLI.
