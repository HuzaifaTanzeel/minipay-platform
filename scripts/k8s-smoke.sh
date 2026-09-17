#!/usr/bin/env bash
# Fast checks that Path B is serving: pods Ready, Postgres ClusterIP, /ready JSON.
set -euo pipefail

export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "error: kubectl not on PATH" >&2
  exit 1
fi

echo "== pods =="
kubectl -n minipay get pods
echo
echo "== minipay-db Service type (expect ClusterIP) =="
kubectl -n minipay get svc minipay-db -o jsonpath='{.spec.type}{"\n"}'
echo
echo "== endpoints (must not be <none>) =="
kubectl -n minipay get endpoints minipay-api minipay-web
echo
echo "== GET http://localhost:8080/ready =="
curl -sS -f http://localhost:8080/ready
echo
