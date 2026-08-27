"""Master Product Catalog, Images, and Variants domain models."""
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Integer, Float, ForeignKey, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Product(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Authoritative master grocery product catalog."""
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Unit & Pricing
    unit: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)  # kg, g, L, ml, pcs, bunch, pack
    base_price: Mapped[float] = mapped_column(Float, nullable=False)  # MRP
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)  # Discounted selling price
    cost_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # Procurement benchmark
    tax_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # GST/VAT percentage (0%, 5%, 12%, 18%)

    # Variable Weight Grocery Specifics (Tomatoes, Apples, Meat, Cheese)
    is_variable_weight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    weight_increment: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # e.g. 0.25 kg increments
    weight_tolerance_pct: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)  # Max allowed picker variance
    min_order_qty: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_order_qty: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)

    # Grocery Ingredients, Nutrition, Storage & Shelf Life
    ingredients: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nutritional_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON or descriptive text
    allergen_info: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    storage_instructions: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)  # Ambient, Chilled (2-4C), Frozen (-18C)
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    country_of_origin: Mapped[str] = mapped_column(String(60), default="India", nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Dietary & Lifestyle Tags
    is_organic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_vegan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_gluten_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_diabetic_friendly: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Status & Rating Aggregations
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)  # ACTIVE, DRAFT, OUT_OF_STOCK
    rating_average: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Media gallery images for master products."""
    __tablename__ = "product_images"

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="images")


class ProductVariant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Packaging or flavor variations of a parent product."""
    __tablename__ = "product_variants"

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "500g Pouch", "1kg Economy Jar"
    price_override: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attributes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON attributes

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
