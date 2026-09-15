"""Payment JSON API (guarded by X-API-Key) plus dashboard stats."""
from enum import Enum

from fastapi import APIRouter, Depends, Query, Response

from ..auth import require_api_key
from ..dependencies import get_dashboard_service, get_payment_service
from ..schemas import PaymentCreate
from ..services.dashboard_service import DashboardService
from ..services.payment_service import PaymentService

router = APIRouter(prefix="/api", tags=["payments"], dependencies=[Depends(require_api_key)])


class StatusFilter(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"


class SortField(str, Enum):
    created_at = "created_at"
    amount = "amount"
    status = "status"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


@router.post("/payments", status_code=201)
def create_payment(
    body: PaymentCreate,
    response: Response,
    svc: PaymentService = Depends(get_payment_service),
):
    result = svc.create_payment(body.customer_ref, body.amount, body.transaction_ref)
    if result.replay:
        response.status_code = 200
        response.headers["Idempotent-Replay"] = "true"
    return result.payment


@router.get("/payments")
def list_payments(
    status: StatusFilter | None = Query(default=None),
    customer_ref: str | None = Query(default=None, max_length=40),
    ref: str | None = Query(default=None, max_length=50),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    sort: SortField = Query(default=SortField.created_at),
    order: SortOrder = Query(default=SortOrder.desc),
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: PaymentService = Depends(get_payment_service),
):
    filters = {
        "status": status.value if status else None,
        "customer_ref": customer_ref,
        "ref": ref,
        "date_from": date_from,
        "date_to": date_to,
        "sort": sort.value,
        "order": order.value,
    }
    return svc.list_payments(filters, limit, offset)


@router.get("/payments/by-id/{txn_id}")
def get_payment_by_id(
    txn_id: int,
    svc: PaymentService = Depends(get_payment_service),
):
    return svc.get_payment_by_id(txn_id)


@router.get("/payments/{ref}")
def get_payment(
    ref: str,
    svc: PaymentService = Depends(get_payment_service),
):
    # INCIDENT-001: duplicate transaction_ref values (e.g. TXN00004999) raise
    # MultipleRowsError inside the service and surface as a 500. Left as-is.
    return svc.get_payment(ref)


@router.get("/stats")
def stats(svc: DashboardService = Depends(get_dashboard_service)):
    return svc.get_overview()


@router.get("/stats/timeseries")
def stats_timeseries(
    days: int = Query(14, ge=1, le=90),
    svc: DashboardService = Depends(get_dashboard_service),
):
    return svc.get_timeseries(days)
