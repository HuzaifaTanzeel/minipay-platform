"""Anomaly registry: one test per rule, plus recommendation priority."""
from datetime import datetime, timedelta

from support_tool.analysis import detect_anomalies, recommend
from support_tool.models import Anomaly, Severity

from fakes import NOW, make_callback, make_transaction


def test_no_anomalies_on_clean_success():
    txn = make_transaction()
    cbs = [make_callback()]
    found = detect_anomalies(txn, cbs, [txn.id], NOW)
    assert found == ()
    assert recommend(found) == "No anomalies detected. No action required."


def test_duplicate_reference():
    txn = make_transaction()
    found = detect_anomalies(txn, [], [1, 2], NOW)
    assert found[0].code == "DUPLICATE_REFERENCE"
    assert found[0].severity == Severity.HIGH
    assert "1" in found[0].detail and "2" in found[0].detail


def test_stuck_processing():
    created = NOW.replace(tzinfo=None) - timedelta(minutes=20)
    txn = make_transaction(status="PROCESSING", completed_at=None, created_at=created)
    found = detect_anomalies(txn, [], [txn.id], NOW, stuck_minutes=15)
    assert any(a.code == "STUCK_PROCESSING" for a in found)


def test_stuck_processing_not_fired_when_recent():
    created = NOW.replace(tzinfo=None) - timedelta(minutes=5)
    txn = make_transaction(status="PROCESSING", completed_at=None, created_at=created)
    found = detect_anomalies(txn, [], [txn.id], NOW, stuck_minutes=15)
    assert not any(a.code == "STUCK_PROCESSING" for a in found)


def test_completed_before_created():
    created = datetime(2026, 9, 16, 12, 0, 0)
    completed = datetime(2026, 9, 16, 11, 0, 0)
    txn = make_transaction(created_at=created, completed_at=completed)
    found = detect_anomalies(txn, [], [txn.id], NOW)
    assert any(a.code == "COMPLETED_BEFORE_CREATED" for a in found)


def test_success_without_callback():
    txn = make_transaction(status="SUCCESS")
    found = detect_anomalies(txn, [], [txn.id], NOW)
    assert any(a.code == "SUCCESS_WITHOUT_CALLBACK" for a in found)


def test_callback_retries_exhausted():
    txn = make_transaction(status="FAILED", failure_code="UPSTREAM_ERROR")
    cbs = [
        make_callback(attempt_no=n, http_status=503, callback_status="FAILED")
        for n in (1, 2, 3)
    ]
    found = detect_anomalies(txn, cbs, [txn.id], NOW)
    assert any(a.code == "CALLBACK_RETRIES_EXHAUSTED" for a in found)


def test_failed_upstream():
    txn = make_transaction(status="FAILED", failure_code="UPSTREAM_ERROR", completed_at=NOW.replace(tzinfo=None))
    found = detect_anomalies(txn, [], [txn.id], NOW)
    assert any(a.code == "FAILED_UPSTREAM" for a in found)


def test_failed_other_code():
    txn = make_transaction(status="FAILED", failure_code="INSUFFICIENT_FUNDS")
    found = detect_anomalies(txn, [], [txn.id], NOW)
    assert any(a.code == "FAILED" and a.detail == "INSUFFICIENT_FUNDS" for a in found)


def test_recommend_picks_high_over_medium():
    anomalies = (
        Anomaly("SUCCESS_WITHOUT_CALLBACK", Severity.MEDIUM, "x"),
        Anomaly("DUPLICATE_REFERENCE", Severity.HIGH, "y"),
    )
    text = recommend(anomalies)
    assert "canonical" in text.lower() or "L3" in text
