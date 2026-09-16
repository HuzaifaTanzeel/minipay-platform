"""Payment business logic: creation with idempotency, and lookups.

Idempotency rules (keyed on transaction_ref):
  - same ref + same (customer, amount)      -> replay: return existing, 200
  - same ref + different payload            -> 409 REFERENCE_CONFLICT
  - ref already maps to multiple rows       -> 409 REFERENCE_AMBIGUOUS
  - no existing ref                         -> create new, 201
"""
from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass

from psycopg_pool import ConnectionPool

from ..db.helpers import MultipleRowsError
from ..errors import ApiError
from ..repositories.interfaces import CustomerRepository, PaymentRepository

log = logging.getLogger("app.payments")


@dataclass
class PaymentResult:
    """Outcome of create_payment: the payment row plus whether it was a replay."""
    payment: dict
    replay: bool


class PaymentService:
    def __init__(
        self,
        pool: ConnectionPool,
        payments: PaymentRepository,
        customers: CustomerRepository,
    ):
        self._pool = pool
        self._payments = payments
        self._customers = customers

    def create_payment(self, customer_ref: str, amount, transaction_ref: str | None) -> PaymentResult:
        with self._pool.connection() as conn, conn.cursor() as cur:
            customer = self._customers.get_by_ref(cur, customer_ref)
            if not customer:
                raise ApiError(404, "CUSTOMER_NOT_FOUND", f"customer {customer_ref} not found")

            ref = transaction_ref or f"TXN{secrets.token_hex(6).upper()}"

            # Lock any existing rows for this ref to make the check-and-insert atomic.
            cur.execute(
                "SELECT id, customer_id, amount FROM transactions "
                "WHERE transaction_ref = %s FOR UPDATE",
                (ref,),
            )
            existing = cur.fetchall()
            if existing:
                if len(existing) > 1:
                    raise ApiError(
                        409,
                        "REFERENCE_AMBIGUOUS",
                        "reference maps to multiple transactions",
                        ids=[r["id"] for r in existing],
                    )
                row = existing[0]
                same_payload = (
                    row["customer_id"] == customer["id"] and row["amount"] == amount
                )
                if same_payload:
                    return PaymentResult(self._payments.get_by_id(cur, row["id"]), replay=True)
                raise ApiError(
                    409,
                    "REFERENCE_CONFLICT",
                    "reference already used with a different payload",
                )

            created = self._payments.create(cur, customer["id"], ref, amount)
            return PaymentResult(self._payments.get_by_id(cur, created["id"]), replay=False)

    def get_payment(self, ref: str) -> dict:
        """Look up a payment by reference, including its callbacks.

        Duplicate seed refs raise MultipleRowsError from fetch_one_strict.
        That is a data-integrity condition, not an unexpected crash: return
        409 REFERENCE_AMBIGUOUS with the row ids so ops can load each via
        GET /api/payments/by-id/{id}.
        """
        with self._pool.connection() as conn, conn.cursor() as cur:
            try:
                row = self._payments.get_by_ref(cur, ref)
            except MultipleRowsError:
                rows = self._payments.find_all_by_ref(cur, ref)
                ids = [r["id"] for r in rows]
                log.warning("ambiguous reference", extra={"ref": ref, "ids": ids})
                raise ApiError(
                    409,
                    "REFERENCE_AMBIGUOUS",
                    "reference maps to multiple transactions; use /api/payments/by-id/{id}",
                    ids=ids,
                )
            if not row:
                raise ApiError(404, "PAYMENT_NOT_FOUND", f"payment {ref} not found")
            row["callbacks"] = self._payments.callbacks_for(cur, row["id"])
            return row

    def get_payment_by_id(self, txn_id: int) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            row = self._payments.get_by_id(cur, txn_id)
            if not row:
                raise ApiError(404, "PAYMENT_NOT_FOUND", f"payment id {txn_id} not found")
            row["callbacks"] = self._payments.callbacks_for(cur, row["id"])
            return row

    def list_payments(self, filters: dict, limit: int, offset: int) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            items = self._payments.list_filtered(cur, filters, limit, offset)
            total = self._payments.count_filtered(cur, filters)
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    def list_customer_payments(self, customer_id: int, limit: int, offset: int) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            customer = self._customers.get_by_id(cur, customer_id)
            if not customer:
                raise ApiError(404, "CUSTOMER_NOT_FOUND", f"customer {customer_id} not found")
            items = self._payments.list_by_customer(cur, customer_id, limit, offset)
            total = self._payments.count_by_customer(cur, customer_id)
            return {
                "customer": customer,
                "limit": limit,
                "offset": offset,
                "total": total,
                "items": items,
            }
