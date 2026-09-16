"""In-memory adapters for unit tests. Same shapes as production ports."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from support_tool.models import (
    ApiProbes,
    Callback,
    FailedBucket,
    Probe,
    StuckRow,
    Transaction,
)


NOW = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)


def make_transaction(**overrides) -> Transaction:
    values = dict(
        id=1,
        transaction_ref="TXN00000001",
        customer_id=1,
        customer_ref="CUST000001",
        customer_name="Customer 1",
        amount=Decimal("10.00"),
        status="SUCCESS",
        created_at=datetime(2026, 9, 16, 11, 0, 0),
        completed_at=datetime(2026, 9, 16, 11, 0, 30),
        failure_code=None,
    )
    values.update(overrides)
    return Transaction(**values)


def make_callback(**overrides) -> Callback:
    values = dict(
        attempt_no=1,
        http_status=200,
        callback_status="SUCCESS",
        attempted_at=datetime(2026, 9, 16, 11, 0, 35),
    )
    values.update(overrides)
    return Callback(**values)


class FakeClock:
    def __init__(self, instant: datetime = NOW):
        self._instant = instant

    def now(self) -> datetime:
        return self._instant


class FakeTransactionStore:
    def __init__(
        self,
        rows: dict[str, list[Transaction]] | None = None,
        callbacks: dict[int, list[Callback]] | None = None,
        stuck_result: tuple[int, list[StuckRow]] | None = None,
        failed: list[FailedBucket] | None = None,
    ):
        self.rows = rows or {}
        self.callback_map = callbacks or {}
        self.stuck_result = stuck_result or (0, [])
        self.failed = failed or []
        self.last_stuck_now: datetime | None = None

    def find_all_by_ref(self, ref: str) -> list[Transaction]:
        return list(self.rows.get(ref, []))

    def callbacks_for(self, txn_id: int) -> list[Callback]:
        return list(self.callback_map.get(txn_id, []))

    def stuck(self, minutes: int, now: datetime, limit: int) -> tuple[int, list[StuckRow]]:
        self.last_stuck_now = now
        count, items = self.stuck_result
        return count, items[:limit]

    def failed_summary(self) -> list[FailedBucket]:
        return list(self.failed)


class FakeHealthChecker:
    def __init__(self, database: Probe, api: ApiProbes):
        self._database = database
        self._api = api

    def ping_db(self) -> Probe:
        return self._database

    def ping_api(self) -> ApiProbes:
        return self._api
