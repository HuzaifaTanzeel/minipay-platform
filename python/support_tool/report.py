"""Text and JSON presenters. stdout-only; no logging."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from .models import FailedSummary, HealthSnapshot, Report, StuckSummary


def _duration(created_at: datetime, completed_at: datetime | None) -> str:
    if completed_at is None:
        return "-"
    delta = completed_at - created_at
    if isinstance(delta, timedelta):
        return str(delta)
    return str(delta)


def render_report(report: Report) -> str:
    t = report.transaction
    lines = [
        "TRANSACTION",
        f"  id:              {t.id}",
        f"  transaction_ref: {t.transaction_ref}",
        f"  amount:          {t.amount}",
        f"  status:          {t.status}",
        f"  failure_code:    {t.failure_code or '-'}",
        "",
        "CUSTOMER",
        f"  customer_ref:    {t.customer_ref}",
        f"  name:            {t.customer_name}",
        f"  customer_id:     {t.customer_id}",
        "",
        "TIMELINE",
        f"  created_at:      {t.created_at}",
        f"  completed_at:    {t.completed_at or '-'}",
        f"  duration:        {_duration(t.created_at, t.completed_at)}",
        "",
        "CALLBACKS",
    ]
    if not report.callbacks:
        lines.append("  (none)")
    else:
        for c in report.callbacks:
            lines.append(
                f"  attempt {c.attempt_no}: HTTP {c.http_status} "
                f"{c.callback_status} at {c.attempted_at}"
            )
    lines.extend(["", "ANOMALIES"])
    if not report.anomalies:
        lines.append("  (none)")
    else:
        for a in report.anomalies:
            lines.append(f"  [{a.severity.name}] {a.code}: {a.detail}")
    if len(report.duplicate_ids) > 1:
        lines.append(f"  duplicate ids: {list(report.duplicate_ids)}")
    lines.extend(["", "RECOMMENDATION", f"  {report.recommendation}"])
    return "\n".join(lines)


def render_stuck(summary: StuckSummary) -> str:
    lines = [
        "STUCK PROCESSING",
        f"  threshold: {summary.minutes} minutes",
        f"  as_of:     {summary.as_of}",
        f"  count:     {summary.count}",
        f"  showing:   {len(summary.oldest)} oldest",
        "",
    ]
    if not summary.oldest:
        lines.append("  (none)")
        return "\n".join(lines)
    for row in summary.oldest:
        age_m = round(row.age_seconds / 60, 1)
        lines.append(
            f"  id={row.id} {row.transaction_ref} amount={row.amount} "
            f"created_at={row.created_at} age_min={age_m}"
        )
    return "\n".join(lines)


def render_failed(summary: FailedSummary) -> str:
    lines = ["FAILED SUMMARY", f"  total: {summary.total}", ""]
    if not summary.buckets:
        lines.append("  (none)")
        return "\n".join(lines)
    for b in summary.buckets:
        lines.append(f"  {b.failure_code or '(null)'}: {b.count}")
    return "\n".join(lines)


def render_health(snapshot: HealthSnapshot) -> str:
    def line(p) -> str:
        status = "ok" if p.ok else "FAIL"
        ms = "-" if p.latency_ms is None else f"{p.latency_ms} ms"
        return f"  {p.name:12} {status:4}  {ms}  {p.detail}"

    overall = "healthy" if snapshot.healthy else "unhealthy"
    return "\n".join(
        [
            f"HEALTH  ({overall})",
            line(snapshot.database),
            line(snapshot.api_health),
            line(snapshot.api_ready),
        ]
    )


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.name
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, tuple):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    return obj


def to_json(obj: Any) -> str:
    return json.dumps(_jsonable(obj), indent=2, default=str)
