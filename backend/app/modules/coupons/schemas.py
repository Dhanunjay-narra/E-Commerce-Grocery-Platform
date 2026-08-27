"""Pydantic schemas for coupon management and discount validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CouponCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=30)
    description: Optional[str] = None
    discount_type: str = Field(default="PERCENTAGE", description="PERCENTAGE, FIXED_AMOUNT")
    discount_value: float = Field(..., gt=0)
    min_order_value: float = Field(default=0.0, ge=0)
    max_discount_cap: Optional[float] = Field(None, ge=0)
    applicable_category_id: Optional[str] = None
    applicable_vendor_id: Optional[str] = None
    is_first_order_only: bool = False
    usage_limit_per_user: int = 1
    total_usage_limit: Optional[int] = None
    expires_at: datetime


class CouponUpdate(BaseModel):
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    max_discount_cap: Optional[float] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class CouponResponse(BaseModel):
    id: str
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    min_order_value: float
    max_discount_cap: Optional[float] = None
    applicable_category_id: Optional[str] = None
    applicable_vendor_id: Optional[str] = None
    is_first_order_only: bool
    usage_limit_per_user: int
    total_usage_limit: Optional[int] = None
    total_redemptions: int
    starts_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CouponValidateRequest(BaseModel):
    code: str
    order_amount: float = Field(..., gt=0)
    category_ids: Optional[list[str]] = None
    vendor_ids: Optional[list[str]] = None


class CouponValidateResponse(BaseModel):
    is_valid: bool
    coupon_id: Optional[str] = None
    code: str
    discount_amount: float = 0.0
    final_amount: float
    message: str
