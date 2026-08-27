"""User domain database models including profiles, addresses, dietary preferences, and households."""
from datetime import datetime, date, timezone
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, DateTime, Date, Float, ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.core.security import UserRole


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Primary user identity table."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default=UserRole.CUSTOMER.value, nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    lockout_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses: Mapped[List["UserAddress"]] = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    dietary_preference: Mapped[Optional["DietaryPreference"]] = relationship("DietaryPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    household_memberships: Mapped[List["HouseholdMember"]] = relationship("HouseholdMember", back_populates="user")


class UserProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Extended customer profile data."""
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    preferred_currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    substitution_preference: Mapped[str] = mapped_column(String(30), default="ASK_FIRST", nullable=False)  # ALWAYS_SUBSTITUTE, ASK_FIRST, NEVER_SUBSTITUTE

    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserAddress(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Saved delivery and billing addresses."""
    __tablename__ = "user_addresses"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(50), default="Home", nullable=False)  # Home, Work, Other
    recipient_name: Mapped[str] = mapped_column(String(150), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    street_address: Mapped[str] = mapped_column(String(255), nullable=False)
    apartment_suite: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    landmark: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(50), default="India", nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="addresses")


class DietaryPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Dietary preferences and allergen exclusions."""
    __tablename__ = "dietary_preferences"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_vegan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_gluten_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dairy_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_organic_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_diabetic_friendly: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allergies: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated list

    user: Mapped["User"] = relationship("User", back_populates="dietary_preference")


class Household(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Household unit for collaborative grocery shopping."""
    __tablename__ = "households"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    members: Mapped[List["HouseholdMember"]] = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan")
    items: Mapped[List["HouseholdShoppingItem"]] = relationship("HouseholdShoppingItem", back_populates="household", cascade="all, delete-orphan")


class HouseholdMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Member linking users to households."""
    __tablename__ = "household_members"

    household_id: Mapped[str] = mapped_column(String(36), ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), default="MEMBER", nullable=False)  # OWNER, ADMIN, MEMBER
    can_edit_list: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_order: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    household: Mapped["Household"] = relationship("Household", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="household_memberships")


class HouseholdShoppingItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Collaborative household shopping list items."""
    __tablename__ = "household_shopping_items"

    household_id: Mapped[str] = mapped_column(String(36), ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    custom_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    added_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    household: Mapped["Household"] = relationship("Household", back_populates="items")
