"""Pydantic request/response models.

Validation lives here so routers stay thin: FastAPI returns 422 automatically
when a request body fails these constraints.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

REF_PATTERN = r"^[A-Z0-9_-]+$"


class CustomerCreate(BaseModel):
    customer_ref: str = Field(min_length=3, max_length=40, pattern=REF_PATTERN)
    name: str = Field(min_length=1, max_length=120)


class PaymentCreate(BaseModel):
    customer_ref: str = Field(min_length=3, max_length=40, pattern=REF_PATTERN)
    amount: Decimal = Field(gt=0, le=Decimal("999999999999.99"))
    transaction_ref: str | None = Field(
        default=None, min_length=3, max_length=50, pattern=REF_PATTERN
    )

    @field_validator("amount")
    @classmethod
    def at_most_two_dp(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("amount must have at most 2 decimal places")
        return v


class CustomerOut(BaseModel):
    id: int
    customer_ref: str
    name: str
    created_at: datetime
