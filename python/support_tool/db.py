"""PostgreSQL adapter. Parameterised SQL only. Does not import the API package."""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from .models import Callback, FailedBucket, Probe, StuckRow, Transaction

log = logging.getLogger("support_tool.db")

_SELECT_JOINED = """
SELECT t.id, t.transaction_ref, t.customer_id, c.customer_ref,
       c.name AS customer_name, t.amount, t.status,
       t.created_at, t.completed_at, t.failure_code
FROM transactions t
JOIN customers c ON c.id = t.customer_id
"""


def _naive_utc(dt: datetime) -> datetime:
    """Bind naive timestamps: the schema columns are TIMESTAMP WITHOUT TIME ZONE."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _age_seconds(created_at: datetime, now: datetime) -> float:
    a = created_at.replace(tzinfo=timezone.utc) if created_at.tzinfo is None else created_at
    b = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now
    return (b - a).total_seconds()


def _transaction(row: dict) -> Transaction:
    return Transaction(
        id=row["id"],
        transaction_ref=row["transaction_ref"],
        customer_id=row["customer_id"],
        customer_ref=row["customer_ref"],
        customer_name=row["customer_name"],
        amount=row["amount"],
        status=row["status"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
        failure_code=row["failure_code"],
    )


class PostgresTransactionStore:
    def __init__(self, dsn: str, timeout_s: float = 3.0, statement_timeout_ms: int = 3000):
        self._dsn = dsn
        self._timeout_s = timeout_s
        self._statement_timeout_ms = statement_timeout_ms

    @contextmanager
    def _connect(self) -> Iterator[psycopg.Connection]:
        conn = psycopg.connect(
            self._dsn,
            connect_timeout=int(max(1, self._timeout_s)),
            options=f"-c statement_timeout={self._statement_timeout_ms}",
            row_factory=dict_row,
        )
        try:
            yield conn
        finally:
            conn.close()

    def find_all_by_ref(self, ref: str) -> list[Transaction]:
        sql = _SELECT_JOINED + "WHERE t.transaction_ref = %s ORDER BY t.id"
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (ref,))
            return [_transaction(r) for r in cur.fetchall()]

    def callbacks_for(self, txn_id: int) -> list[Callback]:
        sql = """
            SELECT attempt_no, http_status, callback_status, attempted_at
            FROM callbacks
            WHERE transaction_id = %s
            ORDER BY attempt_no
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (txn_id,))
            return [
                Callback(
                    attempt_no=r["attempt_no"],
                    http_status=r["http_status"],
                    callback_status=r["callback_status"],
                    attempted_at=r["attempted_at"],
                )
                for r in cur.fetchall()
            ]

    def stuck(self, minutes: int, now: datetime, limit: int) -> tuple[int, list[StuckRow]]:
        cutoff = _naive_utc(now) - timedelta(minutes=minutes)
        count_sql = """
            SELECT COUNT(*) AS n
            FROM transactions
            WHERE status = 'PROCESSING'
              AND completed_at IS NULL
              AND created_at < %s
        """
        list_sql = """
            SELECT id, transaction_ref, customer_id, amount, created_at
            FROM transactions
            WHERE status = 'PROCESSING'
              AND completed_at IS NULL
              AND created_at < %s
            ORDER BY created_at
            LIMIT %s
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(count_sql, (cutoff,))
            total = int(cur.fetchone()["n"])
            cur.execute(list_sql, (cutoff, limit))
            rows = [
                StuckRow(
                    id=r["id"],
                    transaction_ref=r["transaction_ref"],
                    customer_id=r["customer_id"],
                    amount=r["amount"],
                    created_at=r["created_at"],
                    age_seconds=_age_seconds(r["created_at"], now),
                )
                for r in cur.fetchall()
            ]
        return total, rows

    def failed_summary(self) -> list[FailedBucket]:
        sql = """
            SELECT failure_code, COUNT(*) AS count
            FROM transactions
            WHERE status = 'FAILED'
            GROUP BY failure_code
            ORDER BY count DESC
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql)
            return [
                FailedBucket(failure_code=r["failure_code"], count=int(r["count"]))
                for r in cur.fetchall()
            ]


def ping_database(dsn: str, timeout_s: float) -> Probe:
    """SELECT 1 with the same timeouts as the store. Never includes the DSN in detail."""
    t0 = time.perf_counter()
    try:
        with psycopg.connect(
            dsn,
            connect_timeout=int(max(1, timeout_s)),
            options="-c statement_timeout=3000",
        ) as conn:
            conn.execute("SELECT 1")
        ms = round((time.perf_counter() - t0) * 1000, 1)
        return Probe(name="database", ok=True, latency_ms=ms, detail="ok")
    except Exception as e:
        ms = round((time.perf_counter() - t0) * 1000, 1)
        log.error("database probe failed: %s", type(e).__name__)
        return Probe(name="database", ok=False, latency_ms=ms, detail=type(e).__name__)
