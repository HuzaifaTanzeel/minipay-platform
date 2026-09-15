"""Liveness and readiness probes.

/health  = process is up (no dependencies checked).
/ready   = can we serve traffic? (short database ping) -> 503 if not.
Never point a liveness probe at /ready, or a DB blip would restart pods.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..db import pool

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    try:
        with pool.connection(timeout=1) as conn:
            conn.execute("SELECT 1")
        return {"status": "ready", "checks": {"database": "ok"}}
    except Exception as exc:  # noqa: BLE001 - report any dependency failure as not-ready
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "checks": {"database": f"error: {type(exc).__name__}"}},
        )
