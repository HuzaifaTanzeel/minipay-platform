"""FastAPI application entrypoint.

Wires configuration, logging, the connection pool lifespan, a request-id
middleware, the JSON error envelope handlers, and the API routers. The user
interface is a separate React SPA that consumes this API.
"""
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from .config import settings
from .db import pool
from .errors import ApiError, api_error_handler, unhandled_handler
from .logging_config import configure, request_id_var
from .routers import customers, health, payments

configure(settings.log_level)
access_log = logging.getLogger("app.access")


@asynccontextmanager
async def lifespan(_: FastAPI):
    pool.open()
    try:
        yield
    finally:
        pool.close()


app = FastAPI(title="MiniPay", version="1.0.0", lifespan=lifespan)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(Exception, unhandled_handler)


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    access_log.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 1),
        },
    )
    return response


for r in (health.router, customers.router, payments.router):
    app.include_router(r)

# Unauthenticated scrape target for Prometheus (same class as /health).
# Tuned buckets: this API is typically sub-second; default 10s buckets hide p95.
_LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
_instrumentator = Instrumentator(
    should_group_status_codes=True,
    excluded_handlers=["/health", "/ready", "/metrics"],
)
_instrumentator.add(metrics.latency(buckets=_LATENCY_BUCKETS))
_instrumentator.add(metrics.requests())
_instrumentator.instrument(app).expose(app, include_in_schema=False)
