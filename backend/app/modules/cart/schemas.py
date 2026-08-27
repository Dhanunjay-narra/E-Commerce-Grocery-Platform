"""Pydantic schemas for shopping cart, multi-vendor cart partitioning, and item modifications."""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CartItemAddRequest(BaseModel):
    product_id: str
    vendor_id: Optional[str] = None
    quantity: float = Field(default=1.0, gt=0)
    notes: Optional[str] = None


class CartItemUpdateRequest(BaseModel):
    quantity: float = Field(..., gt=0)
    notes: Optional[str] = None


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    vendor_id: Optional[str] = None
    product_name: str
    brand: str
    sku: str
    unit: str
    unit_price: float
    quantity: float
    item_total: float
    is_variable_weight: bool
    notes: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VendorCartGroupResponse(BaseModel):
    vendor_id: Optional[str] = None
    vendor_name: str
    items: List[CartItemResponse] = []
    vendor_subtotal: float

    model_config = ConfigDict(from_attributes=True)


class ApplyCouponRequest(BaseModel):
    coupon_code: str


class CartResponse(BaseModel):
    cart_id: str
    vendor_groups: List[VendorCartGroupResponse] = []
    total_items: int
    subtotal: float
    coupon_code: Optional[str] = None
    discount_amount: float = 0.0
    tax_estimate: float = 0.0
    delivery_fee_estimate: float = 0.0
    grand_total: float

    model_config = ConfigDict(from_attributes=True)
