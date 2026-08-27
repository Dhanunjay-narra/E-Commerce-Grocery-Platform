"""Smart Replenishment Model, Household Grocery Planner, and Recommendation entities."""
from datetime import datetime, timezone, date
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, Integer, ForeignKey, Text, DateTime, Date
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.modules.products.models import Product


class SmartGroceryPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Weekly household meal and pantry replenishment schedule."""
    __tablename__ = "smart_grocery_plans"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_name: Mapped[str] = mapped_column(String(100), default="Weekly Household Plan", nullable=False)
    frequency_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)  # Every 7 days
    is_recurring_auto_order: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    next_replenishment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items: Mapped[List["SmartPlanItem"]] = relationship("SmartPlanItem", back_populates="plan", cascade="all, delete-orphan")


class SmartPlanItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Line item in a smart weekly grocery schedule."""
    __tablename__ = "smart_plan_items"

    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("smart_grocery_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    aisle_category: Mapped[str] = mapped_column(String(50), default="Pantry", nullable=False)  # Produce, Dairy, Bakery, Staples, Snacks, Household

    plan: Mapped["SmartGroceryPlan"] = relationship("SmartGroceryPlan", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class ReplenishmentCadence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Predictive model tracking customer repurchase cadence per item."""
    __tablename__ = "replenishment_cadences"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    average_interval_days: Mapped[float] = mapped_column(Float, nullable=False)  # e.g., 3.2 days for milk
    last_purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predicted_runout_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)

    product: Mapped["Product"] = relationship("Product")
