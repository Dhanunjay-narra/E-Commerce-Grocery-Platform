"""Pydantic schemas for Orders, Checkout, Variable-Weight picking, and Invoicing."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.modules.shipping.schemas import ShipmentResponse
from app.modules.payments.schemas import PaymentResponse


class OrderItemResponse(BaseModel):
    id: str
    order_id: str
    product_id: str
    vendor_id: Optional[str] = None
    product_name: str
    sku: str
    unit: str
    unit_price: float
    ordered_qty: float
    picked_qty: Optional[float] = None
    item_subtotal: float
    final_item_total: Optional[float] = None
    is_variable_weight: bool
    item_status: str
    substituted_product_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderStatusHistoryResponse(BaseModel):
    from_status: Optional[str] = None
    to_status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderCheckoutRequest(BaseModel):
    delivery_address_id: str
    delivery_slot_id: Optional[str] = None
    payment_method: str = Field(default="UPI", description="UPI, CARD, NETBANKING, WALLET, CASH_ON_DELIVERY")
    substitution_preference: str = Field(default="ASK_FIRST", description="ALWAYS_SUBSTITUTE, ASK_FIRST, NEVER_SUBSTITUTE")
    customer_notes: Optional[str] = None


class OrderItemPickRequest(BaseModel):
    order_item_id: str
    actual_picked_qty: float = Field(..., gt=0, description="Scale weight from packing scale")
    item_status: str = Field(default="PICKED", description="PICKED, SUBSTITUTED, OUT_OF_STOCK")
    substituted_product_id: Optional[str] = None


class OrderStateTransitionRequest(BaseModel):
    new_status: str
    notes: Optional[str] = None


class OrderCancelRequest(BaseModel):
    cancellation_reason: str = Field(..., min_length=3, max_length=255)


class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: str
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    delivery_fee: float
    grand_total: float
    final_adjusted_total: Optional[float] = None
    delivery_address_id: str
    delivery_slot_id: Optional[str] = None
    substitution_preference: str
    customer_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    items: List[OrderItemResponse] = []
    status_history: List[OrderStatusHistoryResponse] = []
    shipment: Optional[ShipmentResponse] = None
    payments: List[PaymentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(BaseModel):
    order_number: str
    invoice_date: datetime
    customer_name: str
    customer_email: str
    delivery_address: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    delivery_fee: float
    grand_total: float
    items: List[OrderItemResponse] = []
    payment_status: str
