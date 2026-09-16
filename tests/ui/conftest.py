"""Live UI fixtures. Tests hit Compose `web` at MINIPAY_UI_URL, not Vite.

Loads repo-root .env itself so the suite still works when invoked with
`-c tests/ui/pytest.ini` (pytest then treats tests/ui as rootdir and does
not load tests/conftest.py).
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
import requests

_REPO_ROOT = Path(__file__).resolve().parents[2]


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

UI_URL = os.getenv("MINIPAY_UI_URL", "http://localhost:8080").rstrip("/")
API_URL = os.getenv("MINIPAY_BASE_URL", "http://localhost:8000").rstrip("/")


def _api_key() -> str | None:
    return os.getenv("API_KEY") or os.getenv("MINIPAY_API_KEY")


@pytest.fixture(scope="session")
def base_url() -> str:
    return UI_URL


@pytest.fixture(scope="session", autouse=True)
def ui_is_up(base_url: str) -> None:
    try:
        response = requests.get(base_url + "/", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        pytest.exit(
            f"UI not reachable at {base_url}. "
            "Start Compose and wait until the web service is healthy "
            "(http://localhost:8080). "
            f"{exc}",
            returncode=1,
        )


@pytest.fixture
def unique_customer() -> dict:
    """Arrange a customer through the API so the create-payment form has a real ref."""
    key = _api_key()
    if not key:
        pytest.fail("API_KEY or MINIPAY_API_KEY must be set (env or .env)")
    ref = "CUST" + uuid.uuid4().hex[:8].upper()
    response = requests.post(
        f"{API_URL}/api/customers",
        json={"customer_ref": ref, "name": "UI Test Customer"},
        headers={"X-API-Key": key},
        timeout=5,
    )
    assert response.status_code == 201, response.text
    return response.json()
