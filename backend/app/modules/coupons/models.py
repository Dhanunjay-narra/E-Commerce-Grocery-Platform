"""Coupons, Promotions, and Redemption database models."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Float, Integer, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Coupon(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Discount coupon rules and eligibility constraints."""
    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), default="PERCENTAGE", nullable=False)  # PERCENTAGE, FIXED_AMOUNT
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 20.0 (20%) or 100.0 (₹100)
    min_order_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_discount_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Cap on % discount
    
    # Specificity restrictions
    applicable_category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    applicable_vendor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    
    is_first_order_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    usage_limit_per_user: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_redemptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    redemptions: Mapped[List["CouponRedemption"]] = relationship("CouponRedemption", back_populates="coupon", cascade="all, delete-orphan")


class CouponRedemption(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable log of coupon redemptions."""
    __tablename__ = "coupon_redemptions"

    coupon_id: Mapped[str] = mapped_column(String(36), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False)

    coupon: Mapped["Coupon"] = relationship("Coupon", back_populates="redemptions")
