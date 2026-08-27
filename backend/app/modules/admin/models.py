"""Immutable Administrative Action and Compliance Audit Trail database models."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable audit trail for administrative interventions, KYC approvals, and price adjustments."""
    __tablename__ = "audit_logs"

    actor_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # KYC_APPROVED, PRICE_OVERRIDE, INVENTORY_BATCH_WRITEOFF, REFUND_ISSUED, COUPON_CREATED
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # VENDOR, PRODUCT, INVENTORY, ORDER, PAYMENT, COUPON
    entity_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    
    changes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON before / after state
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
