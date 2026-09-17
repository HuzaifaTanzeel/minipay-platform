#!/usr/bin/env bash
# Delete the local k3d cluster created by scripts/k8s-up.sh. Compose volumes are left alone.
set -euo pipefail

CLUSTER="${K3D_CLUSTER:-minipay}"
export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

if ! command -v k3d >/dev/null 2>&1; then
  echo "error: k3d not on PATH" >&2
  exit 1
fi

k3d cluster delete "${CLUSTER}"
echo "Deleted k3d cluster ${CLUSTER}. Compose Postgres (if any) is unchanged."
