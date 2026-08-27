"""Delivery Zones, Capacity-Aware Delivery Slots, and Shipments domain models."""
from datetime import datetime, timezone, date
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, Integer, ForeignKey, Text, DateTime, Date
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class DeliveryZone(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Geographic service area for delivery routing and fee calculation."""
    __tablename__ = "delivery_zones"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    center_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    center_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    base_fee: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    slots: Mapped[List["DeliverySlot"]] = relationship("DeliverySlot", back_populates="zone", cascade="all, delete-orphan")


class DeliverySlot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Capacity-managed delivery time window."""
    __tablename__ = "delivery_slots"

    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("delivery_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)  # "08:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)    # "10:00"
    slot_type: Mapped[str] = mapped_column(String(30), default="STANDARD_2HOUR", nullable=False)  # EXPRESS_30MIN, STANDARD_2HOUR, NEXT_DAY
    max_capacity: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    current_bookings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zone: Mapped["DeliveryZone"] = relationship("DeliveryZone", back_populates="slots")


class Shipment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Shipment dispatch and last-mile proof-of-delivery record."""
    __tablename__ = "shipments"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    vendor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)
    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("delivery_zones.id", ondelete="RESTRICT"), nullable=False)
    slot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("delivery_slots.id", ondelete="SET NULL"), nullable=True)
    delivery_agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    tracking_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, PICKING, PACKED, DISPATCHED, OUT_FOR_DELIVERY, DELIVERED, FAILED
    delivery_otp: Mapped[str] = mapped_column(String(10), nullable=False)  # 4-digit code for POD
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
