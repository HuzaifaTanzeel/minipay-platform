"""Dashboard business logic: assemble the overview view-model."""
from __future__ import annotations

from psycopg_pool import ConnectionPool

from ..config import settings
from ..repositories.interfaces import StatsRepository


class DashboardService:
    def __init__(self, pool: ConnectionPool, stats: StatsRepository):
        self._pool = pool
        self._stats = stats

    def get_overview(self) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            counts = self._stats.status_counts(cur)
            total_value = self._stats.total_value(cur)
            stuck = self._stats.stuck_processing_count(cur, settings.stuck_processing_minutes)
            recent = self._stats.recent_transactions(cur, settings.dashboard_recent_limit)

        success = counts.get("SUCCESS", 0)
        failed = counts.get("FAILED", 0)
        processing = counts.get("PROCESSING", 0)
        total = success + failed + processing
        success_rate = round(100.0 * success / total, 2) if total else 0.0

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "processing": processing,
            "success_rate": success_rate,
            "stuck": stuck,
            "stuck_minutes": settings.stuck_processing_minutes,
            "total_value": total_value,
            "recent": recent,
        }

    def get_timeseries(self, days: int) -> list[dict]:
        with self._pool.connection() as conn, conn.cursor() as cur:
            return self._stats.timeseries(cur, days)
