"""Verified Customer Product and Store Reviews database models."""
from typing import Optional
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.modules.users.models import User
from app.modules.products.models import Product


class ProductReview(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Verified purchaser reviews and ratings."""
    __tablename__ = "product_reviews"

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default="APPROVED", nullable=False, index=True)  # APPROVED, PENDING_MODERATION, REJECTED
    helpful_votes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vendor_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User")
    product: Mapped["Product"] = relationship("Product")
