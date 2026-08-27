"""Pydantic schemas for payment initiation, mock gateway processing, and refunds."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PaymentInitiateRequest(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)
    payment_method: str = Field(default="UPI", description="UPI, CARD, NETBANKING, WALLET, CASH_ON_DELIVERY")
    gateway_provider: str = Field(default="MOCK_GATEWAY", description="MOCK_GATEWAY, STRIPE, RAZORPAY")
    idempotency_key: Optional[str] = None


class PaymentInitiateResponse(BaseModel):
    transaction_id: str
    order_id: str
    amount: float
    currency: str
    payment_method: str
    gateway_provider: str
    client_secret: Optional[str] = None
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class PaymentVerifyRequest(BaseModel):
    transaction_id: str
    gateway_txn_id: Optional[str] = None
    simulate_success: bool = True  # For mock gateway testing


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    gateway_provider: str
    gateway_txn_id: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefundRequest(BaseModel):
    payment_id: str
    amount: float = Field(..., gt=0)
    reason: str


class RefundResponse(BaseModel):
    refund_id: str
    payment_id: str
    amount: float
    refund_status: str
    message: str
