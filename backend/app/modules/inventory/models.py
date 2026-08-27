"""FEFO Inventory Management, Batch Tracking, Warehouses, and Stock Reservations."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Float, Integer, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Warehouse(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Fulfillment warehouse, Dark Store, or local distribution hub."""
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), default="DARK_STORE", nullable=False)  # CENTRAL_WAREHOUSE, DARK_STORE, VENDOR_STORE
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    batches: Mapped[List["InventoryBatch"]] = relationship("InventoryBatch", back_populates="warehouse")


class InventoryBatch(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Authoritative inventory lot/batch with FEFO expiry tracking."""
    __tablename__ = "inventory_batches"

    batch_number: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)
    warehouse_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Dates for FEFO (First-Expiry, First-Out)
    manufacturing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)  # Indexed for fast FEFO sort

    procurement_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    initial_qty: Mapped[float] = mapped_column(Float, nullable=False)
    available_qty: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    reserved_qty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    damaged_qty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Status: ACTIVE, NEAR_EXPIRY, EXPIRED, DEPLETED
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)

    warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse", back_populates="batches")
    reservations: Mapped[List["StockReservation"]] = relationship("StockReservation", back_populates="batch")
    transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="batch")


class StockReservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Temporary TTL-based stock reservation during checkout."""
    __tablename__ = "stock_reservations"

    reference_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # cart_id or order_id
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("inventory_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    reserved_qty: Mapped[float] = mapped_column(Float, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_released: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_committed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    batch: Mapped["InventoryBatch"] = relationship("InventoryBatch", back_populates="reservations")


class InventoryTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable audit trail for all stock movements and adjustments."""
    __tablename__ = "inventory_transactions"

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("inventory_batches.id", ondelete="RESTRICT"), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # RECEIPT, RESERVATION, RELEASE, SALE, DAMAGE, EXPIRED_WASTE, TRANSFER
    quantity: Mapped[float] = mapped_column(Float, nullable=False)  # Positive or negative
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # order_id, po_id

    batch: Mapped["InventoryBatch"] = relationship("InventoryBatch", back_populates="transactions")
