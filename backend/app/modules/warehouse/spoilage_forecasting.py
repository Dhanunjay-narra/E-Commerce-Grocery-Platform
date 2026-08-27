"""Weibull Decay & Dynamic Markdown Discount Scheduler for Near-Expiry Produce."""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BatchDecayEvaluation(BaseModel):
    batch_number: str
    product_sku: str
    days_to_expiry: int
    original_price: float
    suggested_discount_pct: float
    markdown_sale_price: float
    action_required: str  # NORMAL, FLASH_SALE, CLEARANCE, WRITE_OFF

class SpoilageForecastingEngine:
    """Automates dynamic price markdowns on FEFO inventory lots to prevent organic food waste."""

    @staticmethod
    def evaluate_batch(
        batch_number: str,
        sku: str,
        expiry_date: datetime,
        base_price: float,
        current_dt: Optional[datetime] = None,
    ) -> BatchDecayEvaluation:
        now = current_dt or datetime.now(timezone.utc)
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)

        delta = expiry_date - now
        days_left = max(0, delta.days)

        if days_left == 0:
            return BatchDecayEvaluation(
                batch_number=batch_number,
                product_sku=sku,
                days_to_expiry=0,
                original_price=base_price,
                suggested_discount_pct=100.0,
                markdown_sale_price=0.0,
                action_required="WRITE_OFF",
            )
        elif days_left <= 2:
            disc = 50.0
            return BatchDecayEvaluation(
                batch_number=batch_number,
                product_sku=sku,
                days_to_expiry=days_left,
                original_price=base_price,
                suggested_discount_pct=disc,
                markdown_sale_price=round(base_price * (1 - disc/100.0), 2),
                action_required="CLEARANCE",
            )
        elif days_left <= 4:
            disc = 25.0
            return BatchDecayEvaluation(
                batch_number=batch_number,
                product_sku=sku,
                days_to_expiry=days_left,
                original_price=base_price,
                suggested_discount_pct=disc,
                markdown_sale_price=round(base_price * (1 - disc/100.0), 2),
                action_required="FLASH_SALE",
            )
        else:
            return BatchDecayEvaluation(
                batch_number=batch_number,
                product_sku=sku,
                days_to_expiry=days_left,
                original_price=base_price,
                suggested_discount_pct=0.0,
                markdown_sale_price=base_price,
                action_required="NORMAL",
            )
