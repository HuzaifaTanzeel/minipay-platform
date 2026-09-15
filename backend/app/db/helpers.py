"""Cursor helpers shared by repositories."""
from typing import Any


class MultipleRowsError(RuntimeError):
    """Raised when a query expected to match one row matched more than one.

    NOTE (INCIDENT-001): the seed data intentionally contains duplicate
    transaction_ref values and the schema does not enforce uniqueness. The
    payment-lookup path uses fetch_one_strict and leaves this exception
    unhandled, so those ~10 references return HTTP 500. This is the planted
    defect investigated in Phase 7; do not "fix" it here.
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
