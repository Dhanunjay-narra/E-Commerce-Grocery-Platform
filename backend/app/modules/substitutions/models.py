"""Smart Product Substitution rules and customer decision logs."""
from typing import Optional
from sqlalchemy import String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ProductSubstitutionRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Explicit or ML-learned substitution mapping between master products."""
    __tablename__ = "product_substitution_rules"

    original_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    substitute_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    priority_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SubstitutionLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log of substitutions offered during order fulfillment."""
    __tablename__ = "substitution_logs"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    original_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    substituted_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    customer_response: Mapped[str] = mapped_column(String(30), default="AUTO_ACCEPTED", nullable=False)  # ACCEPTED, REJECTED, AUTO_ACCEPTED
    price_difference: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
