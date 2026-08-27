"""Pydantic schemas for vendor management, store geofencing, and payouts."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class VendorStoreCreate(BaseModel):
    store_name: str = Field(..., min_length=2, max_length=150)
    address_street: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    delivery_radius_km: float = 12.0
    opens_at: str = "07:00"
    closes_at: str = "22:00"


class VendorStoreUpdate(BaseModel):
    store_name: Optional[str] = None
    address_street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    delivery_radius_km: Optional[float] = None
    opens_at: Optional[str] = None
    closes_at: Optional[str] = None
    is_accepting_orders: Optional[bool] = None
    store_status: Optional[str] = None


class VendorStoreResponse(BaseModel):
    id: str
    vendor_id: str
    store_name: str
    address_street: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    delivery_radius_km: float
    opens_at: str
    closes_at: str
    is_accepting_orders: bool
    store_status: str

    model_config = ConfigDict(from_attributes=True)


class VendorCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: str
    tax_id: Optional[str] = None
    store: Optional[VendorStoreCreate] = None


class VendorUpdate(BaseModel):
    business_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    commission_rate: Optional[float] = None
    is_active: Optional[bool] = None


class VendorKYCReviewRequest(BaseModel):
    kyc_status: str = Field(..., description="APPROVED or REJECTED")
    kyc_notes: Optional[str] = None
    commission_rate: Optional[float] = None


class VendorResponse(BaseModel):
    id: str
    business_name: str
    slug: str
    owner_id: str
    email: str
    phone: str
    tax_id: Optional[str] = None
    kyc_status: str
    commission_rate: float
    is_active: bool
    rating_average: float
    rating_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorDetailResponse(VendorResponse):
    stores: List[VendorStoreResponse] = []

    model_config = ConfigDict(from_attributes=True)


class VendorPayoutResponse(BaseModel):
    id: str
    vendor_id: str
    amount: float
    currency: str
    period_start: datetime
    period_end: datetime
    status: str
    transaction_ref: Optional[str] = None
    payout_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
