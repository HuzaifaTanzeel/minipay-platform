"""Shared pytest bootstrap for live API and UI suites.

Loads repo-root .env into os.environ without overriding variables already set
in the shell. Keep secrets out of git; copy .env.example to .env locally.
"""
from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    path = _REPO_ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()
