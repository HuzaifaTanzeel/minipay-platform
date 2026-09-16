"""HTTP adapter for /health and /ready. Those endpoints do not require an API key."""
from __future__ import annotations

import logging
import time

import requests

from .models import ApiProbes, Probe

log = logging.getLogger("support_tool.api")


class HttpHealthChecker:
    def __init__(self, api_url: str, timeout_s: float = 3.0):
        self._base = api_url.rstrip("/")
        self._timeout_s = timeout_s

    def ping_api(self) -> ApiProbes:
        return ApiProbes(health=self._get("/health"), ready=self._get("/ready"))

    def _get(self, path: str) -> Probe:
        url = f"{self._base}{path}"
        t0 = time.perf_counter()
        try:
            response = requests.get(url, timeout=self._timeout_s)
            ms = round((time.perf_counter() - t0) * 1000, 1)
            ok = response.status_code == 200
            detail = f"HTTP {response.status_code}"
            return Probe(name=path.lstrip("/"), ok=ok, latency_ms=ms, detail=detail)
        except requests.RequestException as e:
            ms = round((time.perf_counter() - t0) * 1000, 1)
            log.error("api probe %s failed: %s", path, type(e).__name__)
            return Probe(
                name=path.lstrip("/"),
                ok=False,
                latency_ms=ms,
                detail=type(e).__name__,
            )
