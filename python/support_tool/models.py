"""Domain types. Frozen so reports are values, not mutable bags."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import IntEnum


class Severity(IntEnum):
    """Ordered so max(anomalies, key=severity) is the recommendation pick."""

    INFO = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class Transaction:
    id: int
    transaction_ref: str
    customer_id: int
    customer_ref: str
    customer_name: str
    amount: Decimal
    status: str
    created_at: datetime
    completed_at: datetime | None
    failure_code: str | None


@dataclass(frozen=True)
class Callback:
    attempt_no: int
    http_status: int | None
    callback_status: str
    attempted_at: datetime


@dataclass(frozen=True)
class Anomaly:
    code: str
    severity: Severity
    detail: str


@dataclass(frozen=True)
class Report:
    transaction: Transaction
    callbacks: tuple[Callback, ...]
    anomalies: tuple[Anomaly, ...]
    recommendation: str
    duplicate_ids: tuple[int, ...]


@dataclass(frozen=True)
class StuckRow:
    id: int
    transaction_ref: str
    customer_id: int
    amount: Decimal
    created_at: datetime
    age_seconds: float


@dataclass(frozen=True)
class StuckSummary:
    minutes: int
    as_of: datetime
    count: int
    oldest: tuple[StuckRow, ...]


@dataclass(frozen=True)
class FailedBucket:
    failure_code: str | None
    count: int


@dataclass(frozen=True)
class FailedSummary:
    buckets: tuple[FailedBucket, ...]
    total: int


@dataclass(frozen=True)
class Probe:
    name: str
    ok: bool
    latency_ms: float | None
    detail: str


@dataclass(frozen=True)
class ApiProbes:
    health: Probe
    ready: Probe


@dataclass(frozen=True)
class HealthSnapshot:
    database: Probe
    api_health: Probe
    api_ready: Probe

    @property
    def healthy(self) -> bool:
        return self.database.ok and self.api_health.ok and self.api_ready.ok
