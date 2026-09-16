#!/usr/bin/env bash
# Create .venv, install requirements-dev.txt, download Chromium for Playwright.
# Run from anywhere; the repo root is inferred from this script's location.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
  SYS_PY=python3
elif command -v python >/dev/null 2>&1; then
  SYS_PY=python
else
  echo "Python 3.12+ not found on PATH. Install Python and retry." >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "Creating .venv ..."
  "$SYS_PY" -m venv .venv
fi

echo "Installing requirements-dev.txt ..."
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r "$ROOT/requirements-dev.txt"

echo "Installing Playwright Chromium (with OS deps) ..."
.venv/bin/python -m playwright install --with-deps chromium

cat <<'EOF'

Venv ready at .venv

Activate:
  source .venv/bin/activate

Compose must be up (web healthy on http://localhost:8080) before UI tests.

API tests:
  python -m pytest tests/api -v

UI tests:
  python -m pytest -c tests/ui/pytest.ini tests/ui -v

CLI tests:
  python -m pytest python/tests -q

Without activating, prefix the same commands with .venv/bin/python -m
EOF
