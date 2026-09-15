"""Dependency-injection wiring.

Repositories are stateless singletons. Services are constructed per request
(cheap: they just hold references to the pool and repositories). Routers
depend on the service abstractions via FastAPI's Depends, so swapping an
implementation (e.g. for tests) is a one-line change here.
"""
from __future__ import annotations

from .db import pool
from .repositories.customers import PgCustomerRepository
from .repositories.payments import PgPaymentRepository
from .repositories.stats import PgStatsRepository
from .services.customer_service import CustomerService
from .services.dashboard_service import DashboardService
from .services.payment_service import PaymentService

# Stateless repository singletons.
_customer_repo = PgCustomerRepository()
_payment_repo = PgPaymentRepository()
_stats_repo = PgStatsRepository()


def get_customer_service() -> CustomerService:
    return CustomerService(pool, _customer_repo)


def get_payment_service() -> PaymentService:
    return PaymentService(pool, _payment_repo, _customer_repo)


def get_dashboard_service() -> DashboardService:
    return DashboardService(pool, _stats_repo)
