"""Shopping Cart and Cart Items domain models."""
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, ForeignKey, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.modules.products.models import Product
from app.modules.coupons.models import Coupon


class Cart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Shopping cart entity supporting authenticated users and guest sessions."""
    __tablename__ = "carts"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # Guest browser token
    applied_coupon_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)

    items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    coupon: Mapped[Optional["Coupon"]] = relationship("Coupon")


class CartItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Line item in cart associated with a master product and specific vendor store."""
    __tablename__ = "cart_items"

    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)
    
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    is_variable_weight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # e.g., "Cut into small cubes"

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
