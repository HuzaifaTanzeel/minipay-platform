#!/usr/bin/env bash
# Bring up MiniPay on k3d from a clone: cluster, images, Secret from .env, apply, seed.
# Prerequisites: Docker Desktop (engine reachable). kubectl and k3d are installed
# into ~/.local/bin if missing. Does not start Rancher (import this cluster later).
#
# Usage (repo root, or anywhere):
#   ./scripts/k8s-up.sh
# Skip seed: SKIP_SEED=1 ./scripts/k8s-up.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
ORIG_ARGS=("$@")
cd "$ROOT"

CLUSTER="${K3D_CLUSTER:-minipay}"
API_IMAGE="${API_IMAGE:-minipay-api:1.0.0}"
WEB_IMAGE="${WEB_IMAGE:-minipay-web:1.0.0}"
export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

fail() {
  echo "error: $*" >&2
  exit 1
}

ensure_docker() {
  need_cmd docker || fail "Docker not on PATH. Install Docker Desktop and retry."
  if docker info >/dev/null 2>&1; then
    return
  fi
  local err
  err="$(docker info 2>&1 || true)"
  if echo "$err" | grep -qi "permission denied"; then
    if [ "${K8S_UP_DOCKER_GROUP:-}" = "1" ]; then
      fail "Still cannot use /var/run/docker.sock. Enable Ubuntu under Docker Desktop → Settings → Resources → WSL integration, then retry."
    fi
    echo "Docker socket permission denied; adding ${USER} to group docker (sudo once) ..."
    sudo usermod -aG docker "$USER"
    echo "Continuing with group docker ..."
    export K8S_UP_DOCKER_GROUP=1
    # Minimal Ubuntu has no `sg`; sudo -g docker is enough after usermod.
    exec sudo -E -u "$USER" -g docker -- "$SCRIPT_PATH" "${ORIG_ARGS[@]}"
  fi
  fail "Cannot talk to the Docker engine. Start Docker Desktop. On WSL: enable Ubuntu under Settings → Resources → WSL integration."
}

ensure_kubectl() {
  if need_cmd kubectl; then
    return
  fi
  echo "kubectl not found; installing to ~/.local/bin ..."
  local os arch ver
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"
  case "$arch" in
    x86_64) arch=amd64 ;;
    aarch64 | arm64) arch=arm64 ;;
    *) fail "Unsupported architecture: $arch" ;;
  esac
  ver="$(curl -L -s https://dl.k8s.io/release/stable.txt)"
  mkdir -p "${HOME}/.local/bin"
  curl -fsSL -o "${HOME}/.local/bin/kubectl" \
    "https://dl.k8s.io/release/${ver}/bin/${os}/${arch}/kubectl"
  chmod +x "${HOME}/.local/bin/kubectl"
}

ensure_k3d() {
  if need_cmd k3d; then
    return
  fi
  echo "k3d not found; installing to ~/.local/bin ..."
  mkdir -p "${HOME}/.local/bin"
  curl -fsSL https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh \
    | USE_SUDO=false K3D_INSTALL_DIR="${HOME}/.local/bin" bash
  need_cmd k3d || fail "k3d install finished but k3d is still not on PATH."
}

load_env() {
  if [ ! -f .env ]; then
    fail "Missing .env. Copy .env.example to .env and set DB_PASSWORD and API_KEY."
  fi
  set -a
  # strip CR so Windows-edited .env sources cleanly in bash
  # shellcheck disable=SC1090
  source <(sed 's/\r$//' .env)
  set +a
  if [ -z "${DB_PASSWORD:-}" ] || [ "$DB_PASSWORD" = "CHANGE_ME" ]; then
    fail "Set DB_PASSWORD in .env (not CHANGE_ME)."
  fi
  if [ -z "${API_KEY:-}" ] || [ "$API_KEY" = "CHANGE_ME" ]; then
    fail "Set API_KEY in .env (not CHANGE_ME)."
  fi
  DB_USER="${DB_USER:-minipay}"
  DB_NAME="${DB_NAME:-minipay}"
  # In-cluster host is the Service name, never localhost from Compose .env
  K8S_DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@minipay-db:5432/${DB_NAME}"
}

cluster_exists() {
  k3d cluster list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$CLUSTER"
}

apply_secret() {
  kubectl apply -f kubernetes/base/namespace.yaml
  kubectl -n minipay create secret generic minipay-secrets \
    --from-literal=DB_PASSWORD="${DB_PASSWORD}" \
    --from-literal=API_KEY="${API_KEY}" \
    --from-literal=DATABASE_URL="${K8S_DATABASE_URL}" \
    --dry-run=client -o yaml | kubectl apply -f -
}

seed_if_needed() {
  if [ "${SKIP_SEED:-0}" = "1" ]; then
    echo "SKIP_SEED=1; not loading generate_data.py"
    return
  fi
  local py count
  if need_cmd python3; then
    py=python3
  elif need_cmd python; then
    py=python
  else
    fail "python3 not found (needed to seed). Install Python or re-run with SKIP_SEED=1."
  fi
  count="$(kubectl -n minipay exec minipay-db-0 -- psql -U minipay -d minipay -tAc 'SELECT count(*) FROM transactions;' | tr -d '[:space:]')"
  if [ "${count:-0}" != "0" ]; then
    echo "transactions already seeded (${count} rows); skip generate_data.py"
    return
  fi
  echo "Seeding in-cluster Postgres (several minutes) ..."
  "$py" database/generate_data.py | kubectl -n minipay exec -i minipay-db-0 -- \
    psql -U minipay -d minipay -v ON_ERROR_STOP=1 >/dev/null
}

ensure_docker
ensure_kubectl
ensure_k3d
load_env

echo "Stopping Compose web if it is bound to :8080 ..."
docker compose stop web >/dev/null 2>&1 || true

if cluster_exists; then
  echo "k3d cluster ${CLUSTER} already exists"
  k3d kubeconfig merge "${CLUSTER}" --kubeconfig-switch-context >/dev/null 2>&1 || true
else
  echo "Creating k3d cluster ${CLUSTER} ..."
  k3d cluster create "${CLUSTER}" --servers 1 --agents 1 -p "8080:80@loadbalancer"
fi

echo "Building images ..."
docker build -t "${API_IMAGE}" ./backend
docker build -t "${WEB_IMAGE}" ./frontend
echo "Importing images into k3d ..."
k3d image import "${API_IMAGE}" "${WEB_IMAGE}" -c "${CLUSTER}"

apply_secret
echo "Applying kubernetes/overlays/local ..."
kubectl apply -k kubernetes/overlays/local
kubectl -n minipay rollout status statefulset/minipay-db --timeout=180s
kubectl -n minipay wait --for=condition=complete job/minipay-schema-init --timeout=180s
kubectl -n minipay rollout status deploy/minipay-api --timeout=180s
kubectl -n minipay rollout status deploy/minipay-web --timeout=180s

seed_if_needed

echo
kubectl -n minipay get pods
echo
curl -sS http://localhost:8080/ready || echo "(Ingress not ready yet; try: kubectl -n minipay port-forward svc/minipay-web 8080:80)"
echo
echo "UI: http://localhost:8080  lookup TXN00000001"
echo "Namespace: kubectl -n minipay get pods,svc,ingress,endpoints"
echo "Tear down: ./scripts/k8s-down.sh"
echo "Rancher is not started here; import cluster ${CLUSTER} later from this kubeconfig."
