"""Wishlist and Saved Items domain models."""
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Float, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.modules.products.models import Product


class Wishlist(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Named wishlists and grocery reorder templates."""
    __tablename__ = "wishlists"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), default="My Wishlist", nullable=False)
    is_shared_with_household: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    items: Mapped[List["WishlistItem"]] = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Saved product in a wishlist with price-drop tracking."""
    __tablename__ = "wishlist_items"

    wishlist_id: Mapped[str] = mapped_column(String(36), ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    desired_qty: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    added_price: Mapped[float] = mapped_column(Float, nullable=False)  # Price snapshot at the time added to detect price drops

    wishlist: Mapped["Wishlist"] = relationship("Wishlist", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
