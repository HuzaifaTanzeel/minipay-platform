"""Live API fixtures. Tests hit Compose at MINIPAY_BASE_URL, not TestClient."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest
import requests

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

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
