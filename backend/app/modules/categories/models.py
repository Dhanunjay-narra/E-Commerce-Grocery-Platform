"""Category domain database model with 3-tier hierarchy support."""
from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Department -> Category -> Subcategory hierarchical classification."""
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0=Department, 1=Category, 2=Subcategory
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    icon_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Lucide icon name (e.g. 'Apple', 'Milk')
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id", back_populates="subcategories")
    subcategories: Mapped[List["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
