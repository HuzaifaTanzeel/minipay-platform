"""Customer business logic."""
from __future__ import annotations

from psycopg import errors as pg_errors
from psycopg_pool import ConnectionPool

from ..errors import ApiError
from ..repositories.interfaces import CustomerRepository
from ..schemas import CustomerCreate


class CustomerService:
    def __init__(self, pool: ConnectionPool, customers: CustomerRepository):
        self._pool = pool
        self._customers = customers

    def create_customer(self, body: CustomerCreate) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            try:
                return self._customers.create(cur, body.customer_ref, body.name)
            except pg_errors.UniqueViolation:
                raise ApiError(
                    409,
                    "CUSTOMER_EXISTS",
                    f"customer {body.customer_ref} already exists",
                )

    def list_customers(self, q: str | None, limit: int, offset: int) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            items = self._customers.list(cur, q, limit, offset)
            total = self._customers.count(cur, q)
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    def get_customer_detail(self, customer_id: int) -> dict:
        with self._pool.connection() as conn, conn.cursor() as cur:
            customer = self._customers.get_by_id(cur, customer_id)
            if not customer:
                raise ApiError(404, "CUSTOMER_NOT_FOUND", f"customer {customer_id} not found")
            summary = self._customers.summary(cur, customer_id)
        return {"customer": customer, "summary": summary}
