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
