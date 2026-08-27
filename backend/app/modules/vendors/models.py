"""Multi-Vendor marketplace, Store Locations, and Vendor Payout models."""
from datetime import datetime, timezone, time
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, ForeignKey, Text, Time, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Vendor(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Vendor business account entity."""
    __tablename__ = "vendors"

    business_name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # GSTIN / Tax ID
    kyc_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    kyc_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    commission_rate: Mapped[float] = mapped_column(Float, default=8.5, nullable=False)  # 8.5% platform commission
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    rating_average: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    stores: Mapped[List["VendorStore"]] = relationship("VendorStore", back_populates="vendor", cascade="all, delete-orphan")
    payouts: Mapped[List["VendorPayout"]] = relationship("VendorPayout", back_populates="vendor", cascade="all, delete-orphan")


class VendorStore(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Physical store, Dark Store, or fulfillment center operated by vendor."""
    __tablename__ = "vendor_stores"

    vendor_id: Mapped[str] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    store_name: Mapped[str] = mapped_column(String(150), nullable=False)
    address_street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_radius_km: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    opens_at: Mapped[str] = mapped_column(String(10), default="07:00", nullable=False)  # "07:00"
    closes_at: Mapped[str] = mapped_column(String(10), default="22:00", nullable=False)  # "22:00"
    is_accepting_orders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    store_status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)  # OPEN, CLOSED, TEMPORARILY_BUSY

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="stores")


class VendorPayout(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Financial settlement records for marketplace vendor payouts."""
    __tablename__ = "vendor_payouts"

    vendor_id: Mapped[str] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # PENDING, PROCESSING, PAID, FAILED
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payout_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="payouts")
