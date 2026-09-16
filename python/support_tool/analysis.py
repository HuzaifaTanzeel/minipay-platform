"""Anomaly detectors. Pure functions: no I/O, no config files, no SQL.

Add a rule by writing a detector and appending it to DETECTORS. The CLI and
use cases do not change (open/closed).
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, timedelta, timezone

from .models import Anomaly, Callback, Severity, Transaction

Detector = Callable[
    [Transaction, Sequence[Callback], Sequence[int], datetime, int],
    Anomaly | None,
]


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def detect_duplicate_reference(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if len(duplicate_ids) <= 1:
        return None
    ids = list(duplicate_ids)
    return Anomaly(
        code="DUPLICATE_REFERENCE",
        severity=Severity.HIGH,
        detail=f"reference shared by transaction ids {ids}",
    )


def detect_stuck_processing(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if txn.status != "PROCESSING" or txn.completed_at is not None:
        return None
    age = _utc(now) - _utc(txn.created_at)
    if age <= timedelta(minutes=stuck_minutes):
        return None
    return Anomaly(
        code="STUCK_PROCESSING",
        severity=Severity.HIGH,
        detail=f"processing for {age} (> {stuck_minutes}m)",
    )


def detect_completed_before_created(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if txn.completed_at is None:
        return None
    if _utc(txn.completed_at) >= _utc(txn.created_at):
        return None
    return Anomaly(
        code="COMPLETED_BEFORE_CREATED",
        severity=Severity.HIGH,
        detail="timestamp integrity violation",
    )


def detect_success_without_callback(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if txn.status != "SUCCESS":
        return None
    if any(c.callback_status == "SUCCESS" for c in callbacks):
        return None
    return Anomaly(
        code="SUCCESS_WITHOUT_CALLBACK",
        severity=Severity.MEDIUM,
        detail="successful payment never confirmed to merchant",
    )


def detect_callback_retries_exhausted(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if len(callbacks) < 3:
        return None
    if not all(c.callback_status == "FAILED" for c in callbacks):
        return None
    last = callbacks[-1]
    return Anomaly(
        code="CALLBACK_RETRIES_EXHAUSTED",
        severity=Severity.MEDIUM,
        detail=f"{len(callbacks)} attempts, last HTTP {last.http_status}",
    )


def detect_failed(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int,
) -> Anomaly | None:
    if txn.status != "FAILED" or not txn.failure_code:
        return None
    if txn.failure_code == "UPSTREAM_ERROR":
        return Anomaly(
            code="FAILED_UPSTREAM",
            severity=Severity.INFO,
            detail=txn.failure_code,
        )
    return Anomaly(
        code="FAILED",
        severity=Severity.INFO,
        detail=txn.failure_code,
    )


DETECTORS: tuple[Detector, ...] = (
    detect_duplicate_reference,
    detect_stuck_processing,
    detect_completed_before_created,
    detect_success_without_callback,
    detect_callback_retries_exhausted,
    detect_failed,
)

RECOMMENDATIONS: dict[str, str] = {
    "DUPLICATE_REFERENCE": (
        "Escalate to L3: identify canonical transaction, void the other, "
        "enforce uniqueness at ingestion."
    ),
    "STUCK_PROCESSING": (
        "Check upstream provider status; if >60m, query provider for final "
        "state and reconcile."
    ),
    "SUCCESS_WITHOUT_CALLBACK": (
        "Replay callback to merchant endpoint; confirm merchant received it."
    ),
    "CALLBACK_RETRIES_EXHAUSTED": (
        "Merchant endpoint returning 5xx — contact merchant, then replay callback."
    ),
    "FAILED_UPSTREAM": (
        "No action on our side; advise customer to retry. Track upstream error rate."
    ),
    "FAILED": "Review failure_code with the customer; retry if the fault was transient.",
    "COMPLETED_BEFORE_CREATED": "Data-integrity incident: raise with DBA/L3.",
}


def detect_anomalies(
    txn: Transaction,
    callbacks: Sequence[Callback],
    duplicate_ids: Sequence[int],
    now: datetime,
    stuck_minutes: int = 15,
) -> tuple[Anomaly, ...]:
    found: list[Anomaly] = []
    for detector in DETECTORS:
        anomaly = detector(txn, callbacks, duplicate_ids, now, stuck_minutes)
        if anomaly is not None:
            found.append(anomaly)
    return tuple(found)


def recommend(anomalies: Sequence[Anomaly]) -> str:
    if not anomalies:
        return "No anomalies detected. No action required."
    top = max(anomalies, key=lambda a: a.severity)
    return RECOMMENDATIONS.get(top.code, "Review manually.")
