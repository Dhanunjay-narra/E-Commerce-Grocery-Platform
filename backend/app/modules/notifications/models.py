"""In-App and Omnichannel Notification domain models."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Boolean, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer and vendor notification message log."""
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default="IN_APP", nullable=False)  # IN_APP, EMAIL, SMS, PUSH
    type: Mapped[str] = mapped_column(String(50), default="GENERAL", nullable=False, index=True)  # ORDER_CONFIRMED, OUT_FOR_DELIVERY, REPLENISHMENT_REMINDER, PRICE_DROP, PROMO
    data_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON metadata with deep links

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
