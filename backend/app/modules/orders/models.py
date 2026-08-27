"""Order Lifecycle, 11-stage Finite State Machine, and Order Items domain models."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, Integer, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.modules.shipping.models import Shipment
from app.modules.payments.models import PaymentTransaction


class OrderStatus:
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    PAYMENT_VERIFIED = "PAYMENT_VERIFIED"
    PROCESSING = "PROCESSING"
    PICKING = "PICKING"
    PACKED = "PACKED"
    READY_FOR_DISPATCH = "READY_FOR_DISPATCH"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
    REFUNDED = "REFUNDED"


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Authoritative Order entity driving the 11-stage grocery fulfillment state machine."""
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default=OrderStatus.CREATED, nullable=False, index=True)

    # Financial Totals & Variable-Weight Adjustments
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    grand_total: Mapped[float] = mapped_column(Float, nullable=False)  # Pre-authorized estimated amount
    final_adjusted_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Reconciled after scale weighing

    # Delivery Coordinates & Slot
    delivery_address_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_addresses.id", ondelete="RESTRICT"), nullable=False)
    delivery_slot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("delivery_slots.id", ondelete="SET NULL"), nullable=True)
    substitution_preference: Mapped[str] = mapped_column(String(30), default="ASK_FIRST", nullable=False)  # ALWAYS_SUBSTITUTE, ASK_FIRST, NEVER_SUBSTITUTE
    
    customer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invoice_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history: Mapped[List["OrderStatusHistory"]] = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    shipment: Mapped[Optional["Shipment"]] = relationship("Shipment", uselist=False, cascade="all, delete-orphan")
    payments: Mapped[List["PaymentTransaction"]] = relationship("PaymentTransaction", cascade="all, delete-orphan")


class OrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Line item in order with ordered vs actual picked quantity for variable produce."""
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)

    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    ordered_qty: Mapped[float] = mapped_column(Float, nullable=False)
    picked_qty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Entered by picker during packing
    
    item_subtotal: Mapped[float] = mapped_column(Float, nullable=False)  # ordered_qty * unit_price
    final_item_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # picked_qty * unit_price

    is_variable_weight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    item_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, PICKED, SUBSTITUTED, OUT_OF_STOCK
    substituted_product_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="items")


class OrderStatusHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit trail for finite state machine transitions."""
    __tablename__ = "order_status_history"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="status_history")
