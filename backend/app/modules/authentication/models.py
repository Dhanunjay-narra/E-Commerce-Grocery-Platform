"""Authentication session, refresh token, OTP and login security models."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class UserSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks active login sessions per device/client."""
    __tablename__ = "user_sessions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token_jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Cryptographic refresh tokens with rotation and revocation."""
    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OTPRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """OTP verification records for phone/email verification and passwordless login."""
    __tablename__ = "otp_records"

    identifier: Mapped[str] = mapped_column(String(255), index=True, nullable=False)  # Phone number or email
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), default="LOGIN", nullable=False)  # LOGIN, REGISTER, RESET_PASSWORD, DELIVERY_POD
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LoginHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log for login attempts, IP tracking, and brute force detection."""
    __tablename__ = "login_history"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
