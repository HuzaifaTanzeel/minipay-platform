"""API-key authentication for /api/* routes.

Uses a constant-time comparison to avoid leaking the key via timing.
/health, /ready and the server-rendered UI stay unauthenticated (the UI
posts server-side, so the key never reaches the browser).
"""
import secrets

from fastapi import Header

from .config import settings
from .errors import ApiError


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None:
        raise ApiError(401, "MISSING_API_KEY", "X-API-Key header required")
    if not secrets.compare_digest(x_api_key, settings.api_key):
        raise ApiError(403, "INVALID_API_KEY", "API key not accepted")
