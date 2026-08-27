"""Rule Engine for Tiered Quantity Discounts, Bundle Pricing, and Buy-X-Get-Y."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PromotionType(str, Enum):
    FLAT_DISCOUNT = "FLAT_DISCOUNT"
    PERCENTAGE = "PERCENTAGE"
    BUY_X_GET_Y = "BUY_X_GET_Y"
    TIERED_QUANTITY = "TIERED_QUANTITY"
    CATEGORY_BUNDLE = "CATEGORY_BUNDLE"
    CART_THRESHOLD = "CART_THRESHOLD"

class PromotionRule(BaseModel):
    id: str
    code: str
    title: str
    description: str
    promo_type: PromotionType
    discount_value: float
    min_order_amount: float = 0.0
    max_discount_cap: Optional[float] = None
    buy_quantity: int = 1
    free_quantity: int = 0
    target_product_ids: List[str] = Field(default_factory=list)
    target_category_ids: List[str] = Field(default_factory=list)
    is_stackable: bool = False
    is_active: bool = True

class CartItemInput(BaseModel):
    product_id: str
    category_id: str
    quantity: float
    unit_price: float

class AppliedPromotionResult(BaseModel):
    rule_code: str
    title: str
    discount_amount: float
    message: str

class PromotionEvaluationResult(BaseModel):
    original_subtotal: float
    total_discount: float
    final_subtotal: float
    applied_promotions: List[AppliedPromotionResult]

class AdvancedPromotionsEngine:
    """Evaluates complex multi-tier promotional discounts on a shopping cart."""

    @classmethod
    def evaluate_cart_promotions(cls, items: List[CartItemInput], active_rules: List[PromotionRule], entered_coupon: Optional[str] = None) -> PromotionEvaluationResult:
        subtotal = sum(i.quantity * i.unit_price for i in items)
        applied = []
        running_discount = 0.0

        for rule in active_rules:
            if not rule.is_active:
                continue

            if entered_coupon and rule.code.upper() != entered_coupon.upper():
                continue

            if subtotal < rule.min_order_amount:
                continue

            discount = 0.0
            msg = ""

            if rule.promo_type == PromotionType.FLAT_DISCOUNT:
                discount = min(rule.discount_value, subtotal)
                msg = f"Flat ₹{discount:.2f} discount applied."

            elif rule.promo_type == PromotionType.PERCENTAGE:
                disc = (subtotal * rule.discount_value) / 100.0
                if rule.max_discount_cap:
                    disc = min(disc, rule.max_discount_cap)
                discount = disc
                msg = f"{rule.discount_value}% discount applied (Max: ₹{rule.max_discount_cap or 'Unlimited'})."

            elif rule.promo_type == PromotionType.BUY_X_GET_Y:
                for it in items:
                    if not rule.target_product_ids or it.product_id in rule.target_product_ids:
                        sets = int(it.quantity // (rule.buy_quantity + rule.free_quantity))
                        free_count = sets * rule.free_quantity
                        item_disc = free_count * it.unit_price
                        discount += item_disc
                msg = f"Buy {rule.buy_quantity} Get {rule.free_quantity} Free discount applied."

            elif rule.promo_type == PromotionType.TIERED_QUANTITY:
                for it in items:
                    if not rule.target_product_ids or it.product_id in rule.target_product_ids:
                        if it.quantity >= rule.buy_quantity:
                            item_disc = (it.quantity * it.unit_price * rule.discount_value) / 100.0
                            discount += item_disc
                msg = f"Bulk tier quantity discount applied."

            if discount > 0:
                applied.append(AppliedPromotionResult(
                    rule_code=rule.code,
                    title=rule.title,
                    discount_amount=round(discount, 2),
                    message=msg,
                ))
                running_discount += discount
                if not rule.is_stackable:
                    break

        final_subtotal = max(0.0, round(subtotal - running_discount, 2))
        return PromotionEvaluationResult(
            original_subtotal=round(subtotal, 2),
            total_discount=round(running_discount, 2),
            final_subtotal=final_subtotal,
            applied_promotions=applied,
        )
