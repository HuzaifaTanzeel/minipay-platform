"""Uniform JSON error envelope and exception handlers.

Every error response has the shape:
    {"error": {"code": "...", "message": "...", "request_id": "..."}}
plus any extra structured fields passed by the raiser.
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from .logging_config import request_id_var

log = logging.getLogger("app.errors")


class ApiError(Exception):
    """Domain/HTTP error carrying a status, a machine code and a message.

    New error conditions extend this class or raise it directly; handlers and
    callers stay unchanged (open/closed).
    """

    def __init__(self, status: int, code: str, message: str, **extra):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.extra = extra


def envelope(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id_var.get(),
                **extra,
            }
        },
    )


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return envelope(exc.status, exc.code, exc.message, **exc.extra)


async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled error")
    return envelope(
        500,
        "INTERNAL_ERROR",
        "Unexpected error. Quote the request_id when contacting support.",
    )
