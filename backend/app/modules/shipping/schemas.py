"""Pydantic schemas for delivery zones, slots, and proof-of-delivery."""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DeliveryZoneCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=30)
    city: str
    state: str
    center_latitude: float
    center_longitude: float
    radius_km: float = 15.0
    base_fee: float = 40.0


class DeliveryZoneResponse(BaseModel):
    id: str
    name: str
    code: str
    city: str
    state: str
    center_latitude: float
    center_longitude: float
    radius_km: float
    base_fee: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DeliverySlotCreate(BaseModel):
    zone_id: str
    slot_date: date
    start_time: str = "08:00"
    end_time: str = "10:00"
    slot_type: str = "STANDARD_2HOUR"
    max_capacity: int = 25


class DeliverySlotResponse(BaseModel):
    id: str
    zone_id: str
    slot_date: date
    start_time: str
    end_time: str
    slot_type: str
    max_capacity: int
    current_bookings: int
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class ShipmentResponse(BaseModel):
    id: str
    order_id: str
    vendor_id: Optional[str] = None
    tracking_number: str
    status: str
    delivery_otp: str
    delivery_notes: Optional[str] = None
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryOTPVerifyRequest(BaseModel):
    otp: str = Field(..., min_length=4, max_length=6)
