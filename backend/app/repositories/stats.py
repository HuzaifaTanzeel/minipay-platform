"""Aggregate/reporting data access for the dashboard (read-only)."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

Row = dict[str, Any]


class PgStatsRepository:
    """psycopg-backed implementation of the StatsRepository protocol."""

    def status_counts(self, cur) -> dict[str, int]:
        cur.execute("SELECT status, COUNT(*) AS n FROM transactions GROUP BY status")
        return {r["status"]: r["n"] for r in cur.fetchall()}

    def total_value(self, cur) -> Decimal:
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) AS v FROM transactions "
            "WHERE status = 'SUCCESS'"
        )
        return cur.fetchone()["v"]

    def stuck_processing_count(self, cur, minutes: int) -> int:
        # Parameterised relative to now(); the "stuck" window is configurable.
        cur.execute(
            """SELECT COUNT(*) AS n FROM transactions
               WHERE status = 'PROCESSING'
                 AND created_at < now() - make_interval(mins => %s)""",
            (minutes,),
        )
        return cur.fetchone()["n"]

    def recent_transactions(self, cur, limit: int) -> list[Row]:
        cur.execute(
            """SELECT t.transaction_ref, c.customer_ref, t.amount, t.status,
                      t.created_at
               FROM transactions t
               JOIN customers c ON c.id = t.customer_id
               ORDER BY t.created_at DESC
               LIMIT %s""",
            (limit,),
        )
        return cur.fetchall()

    def timeseries(self, cur, days: int) -> list[Row]:
        # Daily counts for the most recent `days` days present in the data.
        # Anchored to the dataset's own max date so it works on seed data
        # dated in the future (Sept 2026).
        cur.execute(
            """WITH bounds AS (
                   SELECT date_trunc('day', MAX(created_at))::date AS max_day
                   FROM transactions
               )
               SELECT date_trunc('day', t.created_at)::date AS day,
                      COUNT(*) AS total,
                      COUNT(*) FILTER (WHERE t.status = 'SUCCESS') AS success,
                      COUNT(*) FILTER (WHERE t.status = 'FAILED') AS failed,
                      COUNT(*) FILTER (WHERE t.status = 'PROCESSING') AS processing
               FROM transactions t, bounds
               WHERE t.created_at >= (bounds.max_day - make_interval(days => %s - 1))
               GROUP BY 1
               ORDER BY 1""",
            (days,),
        )
        return cur.fetchall()
