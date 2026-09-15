"""Customer data access (parameterised SQL only)."""
from __future__ import annotations

from typing import Any

Row = dict[str, Any]


class PgCustomerRepository:
    """psycopg-backed implementation of the CustomerRepository protocol."""

    def get_by_ref(self, cur, customer_ref: str) -> Row | None:
        cur.execute(
            "SELECT id, customer_ref, name, created_at "
            "FROM customers WHERE customer_ref = %s",
            (customer_ref,),
        )
        return cur.fetchone()

    def get_by_id(self, cur, customer_id: int) -> Row | None:
        cur.execute(
            "SELECT id, customer_ref, name, created_at "
            "FROM customers WHERE id = %s",
            (customer_id,),
        )
        return cur.fetchone()

    def create(self, cur, customer_ref: str, name: str) -> Row:
        cur.execute(
            "INSERT INTO customers(customer_ref, name) VALUES (%s, %s) "
            "RETURNING id, customer_ref, name, created_at",
            (customer_ref, name),
        )
        return cur.fetchone()

    def list(self, cur, q: str | None, limit: int, offset: int) -> list[Row]:
        if q:
            like = f"%{q}%"
            cur.execute(
                """SELECT id, customer_ref, name, created_at
                   FROM customers
                   WHERE customer_ref ILIKE %s OR name ILIKE %s
                   ORDER BY id
                   LIMIT %s OFFSET %s""",
                (like, like, limit, offset),
            )
        else:
            cur.execute(
                """SELECT id, customer_ref, name, created_at
                   FROM customers
                   ORDER BY id
                   LIMIT %s OFFSET %s""",
                (limit, offset),
            )
        return cur.fetchall()

    def count(self, cur, q: str | None) -> int:
        if q:
            like = f"%{q}%"
            cur.execute(
                "SELECT COUNT(*) AS n FROM customers "
                "WHERE customer_ref ILIKE %s OR name ILIKE %s",
                (like, like),
            )
        else:
            cur.execute("SELECT COUNT(*) AS n FROM customers")
        return cur.fetchone()["n"]

    def summary(self, cur, customer_id: int) -> Row:
        cur.execute(
            """SELECT
                   COUNT(*) AS txn_count,
                   COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success_count,
                   COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_count,
                   COUNT(*) FILTER (WHERE status = 'PROCESSING') AS processing_count,
                   COALESCE(SUM(amount) FILTER (WHERE status = 'SUCCESS'), 0) AS success_value
               FROM transactions
               WHERE customer_id = %s""",
            (customer_id,),
        )
        return cur.fetchone()
