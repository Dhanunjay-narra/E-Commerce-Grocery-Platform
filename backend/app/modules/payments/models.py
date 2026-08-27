"""Payment Transactions and Refunds database models."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Float, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class PaymentTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Payment record associated with an order with idempotency controls."""
    __tablename__ = "payment_transactions"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)  # UPI, CARD, NETBANKING, WALLET, CASH_ON_DELIVERY
    gateway_provider: Mapped[str] = mapped_column(String(30), default="MOCK_GATEWAY", nullable=False)  # MOCK_GATEWAY, STRIPE, RAZORPAY
    gateway_txn_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, AUTHORIZED, CAPTURED, FAILED, REFUNDED
    error_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)

    refunds: Mapped[List["PaymentRefund"]] = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")


class PaymentRefund(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Refunds issued for cancelled orders or damaged items."""
    __tablename__ = "payment_refunds"

    payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("payment_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    refund_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, PROCESSED, FAILED
    refund_txn_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    payment: Mapped["PaymentTransaction"] = relationship("PaymentTransaction", back_populates="refunds")
