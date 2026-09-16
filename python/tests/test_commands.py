"""Use cases against fakes: not-found, duplicates, injected clock, health."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from support_tool.commands import (
    CheckHealth,
    DiagnosePayment,
    NotFoundError,
    SummarizeFailed,
    SummarizeStuck,
)
from support_tool.models import ApiProbes, FailedBucket, Probe, StuckRow

from fakes import FakeClock, FakeHealthChecker, FakeTransactionStore, NOW, make_callback, make_transaction


def test_diagnose_unknown_ref_raises_not_found():
    cmd = DiagnosePayment(FakeTransactionStore(), FakeClock())
    with pytest.raises(NotFoundError) as exc:
        cmd.run("NOPE")
    assert "NOPE" in str(exc.value)


def test_diagnose_duplicate_reference_sets_ids_and_anomaly():
    t1 = make_transaction(id=10, transaction_ref="TXN00004999")
    t2 = make_transaction(id=11, transaction_ref="TXN00004999")
    store = FakeTransactionStore(
        rows={"TXN00004999": [t1, t2]},
        callbacks={10: [make_callback()]},
    )
    report = DiagnosePayment(store, FakeClock()).run("TXN00004999")
    assert report.duplicate_ids == (10, 11)
    assert any(a.code == "DUPLICATE_REFERENCE" for a in report.anomalies)
    assert report.transaction.id == 10


def test_diagnose_clean_success_has_no_anomalies():
    t = make_transaction()
    store = FakeTransactionStore(rows={t.transaction_ref: [t]}, callbacks={t.id: [make_callback()]})
    report = DiagnosePayment(store, FakeClock()).run(t.transaction_ref)
    assert report.anomalies == ()
    assert "No action" in report.recommendation


def test_stuck_summary_uses_injected_clock():
    now = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)
    created = datetime(2026, 9, 11, 0, 0, 0)
    row = StuckRow(
        id=7,
        transaction_ref="TXN00000007",
        customer_id=1,
        amount=Decimal("1.00"),
        created_at=created,
        age_seconds=(now.replace(tzinfo=None) - created).total_seconds(),
    )
    store = FakeTransactionStore(stuck_result=(25, [row]))
    summary = SummarizeStuck(store, FakeClock(now), stuck_minutes=15, limit=20).run()
    assert store.last_stuck_now == now
    assert summary.as_of == now
    assert summary.count == 25
    assert summary.oldest[0].id == 7
    assert summary.minutes == 15


def test_diagnose_stuck_depends_on_clock_not_wall_time():
    created = datetime(2026, 9, 11, 0, 0, 0)
    t = make_transaction(
        status="PROCESSING",
        completed_at=None,
        created_at=created,
        transaction_ref="TXN_STUCK",
    )
    store = FakeTransactionStore(rows={"TXN_STUCK": [t]})
    as_of = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)
    report = DiagnosePayment(store, FakeClock(as_of), stuck_minutes=15).run("TXN_STUCK")
    assert any(a.code == "STUCK_PROCESSING" for a in report.anomalies)
    too_early = created.replace(tzinfo=timezone.utc) + timedelta(minutes=1)
    report_early = DiagnosePayment(store, FakeClock(too_early), stuck_minutes=15).run("TXN_STUCK")
    assert not any(a.code == "STUCK_PROCESSING" for a in report_early.anomalies)


def test_failed_summary_totals_buckets():
    store = FakeTransactionStore(
        failed=[
            FailedBucket("UPSTREAM_ERROR", 10),
            FailedBucket(None, 2),
        ]
    )
    summary = SummarizeFailed(store).run()
    assert summary.total == 12
    assert summary.buckets[0].count == 10


def test_health_unhealthy_when_database_fails():
    health = FakeHealthChecker(
        Probe("database", False, 12.0, "OperationalError"),
        ApiProbes(
            health=Probe("health", True, 3.0, "HTTP 200"),
            ready=Probe("ready", True, 4.0, "HTTP 200"),
        ),
    )
    snapshot = CheckHealth(health).run()
    assert snapshot.healthy is False
    assert snapshot.database.ok is False
