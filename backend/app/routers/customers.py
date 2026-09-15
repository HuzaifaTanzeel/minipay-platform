"""Customer JSON API (guarded by X-API-Key)."""
from fastapi import APIRouter, Depends, Query

from ..auth import require_api_key
from ..dependencies import get_customer_service, get_payment_service
from ..schemas import CustomerCreate
from ..services.customer_service import CustomerService
from ..services.payment_service import PaymentService

router = APIRouter(prefix="/api", tags=["customers"], dependencies=[Depends(require_api_key)])


@router.post("/customers", status_code=201)
def create_customer(
    body: CustomerCreate,
    svc: CustomerService = Depends(get_customer_service),
):
    return svc.create_customer(body)


@router.get("/customers")
def list_customers(
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: CustomerService = Depends(get_customer_service),
):
    return svc.list_customers(q, limit, offset)


@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    svc: CustomerService = Depends(get_customer_service),
):
    return svc.get_customer_detail(customer_id)


@router.get("/customers/{customer_id}/payments")
def customer_payments(
    customer_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: PaymentService = Depends(get_payment_service),
):
    return svc.list_customer_payments(customer_id, limit, offset)
