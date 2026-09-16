"""Payment/transaction data access (parameterised SQL only)."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from ..db.helpers import fetch_one_strict
from .interfaces import PAYMENT_SORT_COLUMNS

Row = dict[str, Any]


def _build_filters(filters: dict) -> tuple[str, list]:
    """Build a parameterised WHERE clause from a filters dict.

    Only known keys are honoured and every value is bound via %s, so user
    input can never be interpolated into the SQL text.
    """
    clauses: list[str] = []
    params: list = []
    if filters.get("status"):
        clauses.append("t.status = %s")
        params.append(filters["status"])
    if filters.get("customer_ref"):
        clauses.append("c.customer_ref ILIKE %s")
        params.append(f"%{filters['customer_ref']}%")
    if filters.get("ref"):
        clauses.append("t.transaction_ref ILIKE %s")
        params.append(f"%{filters['ref']}%")
    if filters.get("date_from"):
        clauses.append("t.created_at >= %s")
        params.append(filters["date_from"])
    if filters.get("date_to"):
        clauses.append("t.created_at < %s")
        params.append(filters["date_to"])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params

_SELECT_JOINED = """
SELECT t.id, t.transaction_ref, t.customer_id, c.customer_ref,
       c.name AS customer_name, t.amount, t.status,
       t.created_at, t.completed_at, t.failure_code
FROM transactions t
JOIN customers c ON c.id = t.customer_id
"""


class PgPaymentRepository:
    """psycopg-backed implementation of the PaymentRepository protocol."""

    def get_by_ref(self, cur, ref: str) -> Row | None:
        # Strict single-row fetch. Raises MultipleRowsError when more than one
        # transaction shares this transaction_ref (seed duplicates).
        return fetch_one_strict(cur, _SELECT_JOINED + "WHERE t.transaction_ref = %s", (ref,))

    def get_by_id(self, cur, txn_id: int) -> Row | None:
        cur.execute(_SELECT_JOINED + "WHERE t.id = %s", (txn_id,))
        return cur.fetchone()

    def find_all_by_ref(self, cur, ref: str) -> list[Row]:
        cur.execute(
            _SELECT_JOINED + "WHERE t.transaction_ref = %s ORDER BY t.id", (ref,)
        )
        return cur.fetchall()

    def list_by_customer(self, cur, customer_id: int, limit: int, offset: int) -> list[Row]:
        cur.execute(
            """SELECT id, transaction_ref, amount, status,
                      created_at, completed_at, failure_code
               FROM transactions
               WHERE customer_id = %s
               ORDER BY created_at DESC
               LIMIT %s OFFSET %s""",
            (customer_id, limit, offset),
        )
        return cur.fetchall()

    def count_by_customer(self, cur, customer_id: int) -> int:
        cur.execute(
            "SELECT COUNT(*) AS n FROM transactions WHERE customer_id = %s",
            (customer_id,),
        )
        return cur.fetchone()["n"]

    def create(self, cur, customer_id: int, ref: str, amount: Decimal) -> Row:
        cur.execute(
            """INSERT INTO transactions
                   (transaction_ref, customer_id, amount, status, created_at)
               VALUES (%s, %s, %s, 'PROCESSING', now())
               RETURNING id, created_at""",
            (ref, customer_id, amount),
        )
        return cur.fetchone()

    def callbacks_for(self, cur, txn_id: int) -> list[Row]:
        cur.execute(
            """SELECT attempt_no, http_status, callback_status, attempted_at
               FROM callbacks WHERE transaction_id = %s
               ORDER BY attempt_no""",
            (txn_id,),
        )
        return cur.fetchall()

    def list_filtered(self, cur, filters: dict, limit: int, offset: int) -> list[Row]:
        where, params = _build_filters(filters)
        # sort/order come from a whitelist, never from raw user text.
        sort_col = PAYMENT_SORT_COLUMNS.get(filters.get("sort"), "t.created_at")
        order = "ASC" if str(filters.get("order", "desc")).lower() == "asc" else "DESC"
        cur.execute(
            _SELECT_JOINED
            + where
            + f" ORDER BY {sort_col} {order}, t.id {order} LIMIT %s OFFSET %s",
            (*params, limit, offset),
        )
        return cur.fetchall()

    def count_filtered(self, cur, filters: dict) -> int:
        where, params = _build_filters(filters)
        cur.execute(
            "SELECT COUNT(*) AS n FROM transactions t "
            "JOIN customers c ON c.id = t.customer_id" + where,
            tuple(params),
        )
        return cur.fetchone()["n"]
