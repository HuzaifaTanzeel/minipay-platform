"""Cursor helpers shared by repositories."""
from typing import Any


class MultipleRowsError(RuntimeError):
    """Raised when a query expected to match one row matched more than one.

    Seed data contains duplicate transaction_ref values and the schema does
    not enforce uniqueness. Callers that assume a single payment per ref
    (GET /api/payments/{ref}) must handle this; do not swallow it here.
    """


def fetch_one_strict(cur, sql: str, params: tuple) -> dict[str, Any] | None:
    """Fetch exactly one row.

    Returns the row, None if there are no matches, or raises
    MultipleRowsError if the query matches more than one row.
    """
    cur.execute(sql, params)
    rows = cur.fetchmany(2)
    if len(rows) > 1:
        raise MultipleRowsError(f"expected one row, got more for params={params}")
    return rows[0] if rows else None
