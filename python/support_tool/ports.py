"""Inbound ports. Use cases depend on these, never on psycopg or requests."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from .models import ApiProbes, FailedBucket, Probe, StuckRow, Transaction, Callback


class TransactionStore(Protocol):
    def find_all_by_ref(self, ref: str) -> list[Transaction]:
        """Every row for a reference, oldest id first. May be empty or >1."""
        ...

    def callbacks_for(self, txn_id: int) -> list[Callback]:
        ...

    def stuck(self, minutes: int, now: datetime, limit: int) -> tuple[int, list[StuckRow]]:
        """(total matching count, oldest `limit` rows). Age is relative to `now`."""
        ...

    def failed_summary(self) -> list[FailedBucket]:
        ...


class HealthChecker(Protocol):
    def ping_db(self) -> Probe:
        ...

    def ping_api(self) -> ApiProbes:
        ...


class Clock(Protocol):
    def now(self) -> datetime:
        """Timezone-aware UTC instant used for stuck detection."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
