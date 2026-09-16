"""JSON is stable and parseable; text report has the required sections."""
import json

from support_tool.models import Report
from support_tool.report import render_report, to_json

from fakes import make_callback, make_transaction


def _report(**overrides) -> Report:
    t = make_transaction()
    base = dict(
        transaction=t,
        callbacks=(make_callback(),),
        anomalies=(),
        recommendation="No anomalies detected. No action required.",
        duplicate_ids=(t.id,),
    )
    base.update(overrides)
    return Report(**base)


def test_json_has_required_keys_and_parses():
    raw = to_json(_report())
    data = json.loads(raw)
    assert set(data) >= {
        "transaction",
        "callbacks",
        "anomalies",
        "recommendation",
        "duplicate_ids",
    }
    assert data["transaction"]["transaction_ref"] == "TXN00000001"
    assert isinstance(data["anomalies"], list)
    assert isinstance(data["duplicate_ids"], list)


def test_json_serializes_severity_as_name():
    from support_tool.models import Anomaly, Severity

    report = _report(
        anomalies=(Anomaly("DUPLICATE_REFERENCE", Severity.HIGH, "ids [1, 2]"),),
        duplicate_ids=(1, 2),
    )
    data = json.loads(to_json(report))
    assert data["anomalies"][0]["severity"] == "HIGH"
    assert data["anomalies"][0]["code"] == "DUPLICATE_REFERENCE"


def test_text_report_has_sections():
    text = render_report(_report())
    for heading in (
        "TRANSACTION",
        "CUSTOMER",
        "TIMELINE",
        "CALLBACKS",
        "ANOMALIES",
        "RECOMMENDATION",
    ):
        assert heading in text
