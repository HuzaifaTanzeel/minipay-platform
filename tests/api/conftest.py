"""Live API fixtures. Tests hit Compose at MINIPAY_BASE_URL, not TestClient."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
import requests

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    """Fill os.environ from repo-root .env without overriding already-set vars."""
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

BASE = os.getenv("MINIPAY_BASE_URL", "http://localhost:8000")
KEY = os.getenv("API_KEY") or os.getenv("MINIPAY_API_KEY")


def _bind(session: requests.Session, timeout: float = 5.0) -> requests.Session:
    orig = session.request

    def request(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        if not str(url).startswith("http"):
            url = BASE.rstrip("/") + url
        return orig(method, url, **kwargs)

    session.request = request  # type: ignore[method-assign]
    return session


@pytest.fixture(scope="session")
def api():
    if not KEY:
        pytest.fail("API_KEY or MINIPAY_API_KEY must be set (env or .env)")
    session = requests.Session()
    session.headers["X-API-Key"] = KEY
    return _bind(session)


@pytest.fixture(scope="session")
def anon():
    return _bind(requests.Session())


@pytest.fixture
def uniq():
    return "T" + uuid.uuid4().hex[:10].upper()


@pytest.fixture(scope="session")
def customer(api):
    ref = "CUST" + uuid.uuid4().hex[:8].upper()
    response = api.request(
        "POST",
        "/api/customers",
        json={"customer_ref": ref, "name": "Test Customer"},
    )
    assert response.status_code == 201, response.text
    return response.json()
