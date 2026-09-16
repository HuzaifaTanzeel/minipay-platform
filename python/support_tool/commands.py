"""Use cases. Depend on ports + analysis; they do not parse argv or print."""
from __future__ import annotations

from .analysis import detect_anomalies, recommend
from .models import FailedSummary, HealthSnapshot, Report, StuckSummary
from .ports import Clock, HealthChecker, TransactionStore


class NotFoundError(Exception):
    def __init__(self, ref: str):
        super().__init__(f"transaction {ref} not found")
        self.ref = ref


class DiagnosePayment:
    def __init__(self, store: TransactionStore, clock: Clock, stuck_minutes: int = 15):
        self._store = store
        self._clock = clock
        self._stuck_minutes = stuck_minutes

    def run(self, ref: str) -> Report:
        rows = self._store.find_all_by_ref(ref)
        if not rows:
            raise NotFoundError(ref)
        primary = rows[0]
        duplicate_ids = tuple(r.id for r in rows)
        callbacks = tuple(self._store.callbacks_for(primary.id))
        anomalies = detect_anomalies(
            primary,
            callbacks,
            duplicate_ids,
            self._clock.now(),
            self._stuck_minutes,
        )
        return Report(
            transaction=primary,
            callbacks=callbacks,
            anomalies=anomalies,
            recommendation=recommend(anomalies),
            duplicate_ids=duplicate_ids,
        )


class SummarizeStuck:
    def __init__(self, store: TransactionStore, clock: Clock, stuck_minutes: int = 15, limit: int = 20):
        self._store = store
        self._clock = clock
        self._stuck_minutes = stuck_minutes
        self._limit = limit

    def run(self) -> StuckSummary:
        now = self._clock.now()
        count, oldest = self._store.stuck(self._stuck_minutes, now, self._limit)
        return StuckSummary(
            minutes=self._stuck_minutes,
            as_of=now,
            count=count,
            oldest=tuple(oldest),
        )


class SummarizeFailed:
    def __init__(self, store: TransactionStore):
        self._store = store

    def run(self) -> FailedSummary:
        buckets = tuple(self._store.failed_summary())
        return FailedSummary(buckets=buckets, total=sum(b.count for b in buckets))


class CheckHealth:
    def __init__(self, health: HealthChecker):
        self._health = health

    def run(self) -> HealthSnapshot:
        db = self._health.ping_db()
        api = self._health.ping_api()
        return HealthSnapshot(
            database=db,
            api_health=api.health,
            api_ready=api.ready,
        )
