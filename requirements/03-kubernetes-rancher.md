# 03 – Kubernetes & Rancher

Deploy MiniPay (UI/API/database or equivalent components) to Kubernetes.

Your manifests/Helm/Kustomize configuration should demonstrate, where applicable:
- Deployments/StatefulSets;
- Services;
- ConfigMaps;
- Secrets without committing real secret values;
- readiness and liveness probes;
- CPU/memory requests and limits;
- persistent database storage;
- namespaces;
- restart/rollout procedures; and
- log inspection/troubleshooting.

The supplied starter manifest contains defects. Identify them rather than simply replacing the file without explanation. Record findings in `investigation/kubernetes-findings.md`.

## Rancher
Use Rancher to manage or inspect the cluster where feasible. Provide evidence of:
- cluster/workload visibility;
- pod status and logs;
- configuration/environment inspection;
- scaling or rollout/restart; and
- basic resource/health visibility.

Document the procedure in `evidence/rancher.md`. Screenshots may be included with secrets/redacted data removed.
