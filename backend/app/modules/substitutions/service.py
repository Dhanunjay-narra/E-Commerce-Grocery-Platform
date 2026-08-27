"""Smart Substitution Algorithm engine and suggestion service."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError
from app.modules.substitutions.models import ProductSubstitutionRule, SubstitutionLog
from app.modules.substitutions.schemas import (
    SubstitutionSuggestResponse,
    SubstitutionSuggestionItem,
    SubstitutionRuleCreate,
    SubstitutionRuleResponse,
)
from app.modules.products.models import Product
from app.modules.products.schemas import ProductResponse
from app.modules.products.repository import ProductRepository


class SubstitutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prod_repo = ProductRepository(db)

    async def suggest_substitutes(self, product_id: str, vendor_id: Optional[str] = None) -> SubstitutionSuggestResponse:
        """Algorithmic matching: finds in-stock substitutes within category with close price and brand affinity."""
        orig = await self.prod_repo.get_by_id(product_id)
        if not orig:
            raise EntityNotFoundError("Original product not found.")

        # 1. Check explicit rules
        rule_query = select(ProductSubstitutionRule).where(
            and_(
                ProductSubstitutionRule.original_product_id == product_id,
                ProductSubstitutionRule.is_approved == True,
            )
        ).order_by(ProductSubstitutionRule.priority_score.desc())
        rules_res = await self.db.execute(rule_query)
        rules = list(rules_res.scalars().all())

        explicit_sub_ids = [r.substitute_product_id for r in rules]

        # 2. Query same category products
        cat_query = (
            select(Product)
            .where(
                and_(
                    Product.category_id == orig.category_id,
                    Product.id != orig.id,
                    Product.status == "ACTIVE",
                    Product.is_deleted == False,
                )
            )
            .options(selectinload(Product.images))
        )
        cat_res = await self.db.execute(cat_query)
        candidates = list(cat_res.scalars().all())

        suggestions: List[SubstitutionSuggestionItem] = []

        for p in candidates:
            # Score matching
            score = 0.5
            reason = "Same Category Alternative"

            if p.id in explicit_sub_ids:
                score = 0.95
                reason = "Verified System Substitute"
            elif p.brand.lower() == orig.brand.lower():
                score = 0.85
                reason = "Same Brand Match"
            elif p.unit == orig.unit:
                score = 0.70
                reason = "Same Unit / Pack Match"

            price_diff = round(p.sale_price - orig.sale_price, 2)
            # Only suggest if within +/- 30% price range
            if abs(price_diff) <= (orig.sale_price * 0.35):
                primary_img = next((img.image_url for img in p.images if img.is_primary), None)
                if not primary_img and p.images:
                    primary_img = p.images[0].image_url

                p_dto = ProductResponse(
                    id=p.id,
                    sku=p.sku,
                    barcode=p.barcode,
                    name=p.name,
                    slug=p.slug,
                    brand=p.brand,
                    description=p.description,
                    category_id=p.category_id,
                    unit=p.unit,
                    base_price=p.base_price,
                    sale_price=p.sale_price,
                    tax_rate=p.tax_rate,
                    is_variable_weight=p.is_variable_weight,
                    weight_increment=p.weight_increment,
                    weight_tolerance_pct=p.weight_tolerance_pct,
                    min_order_qty=p.min_order_qty,
                    max_order_qty=p.max_order_qty,
                    is_organic=p.is_organic,
                    is_vegetarian=p.is_vegetarian,
                    is_vegan=p.is_vegan,
                    is_gluten_free=p.is_gluten_free,
                    is_diabetic_friendly=p.is_diabetic_friendly,
                    status=p.status,
                    rating_average=p.rating_average,
                    rating_count=p.rating_count,
                    primary_image_url=primary_img,
                    created_at=p.created_at,
                )

                suggestions.append(
                    SubstitutionSuggestionItem(
                        product=p_dto,
                        match_score=score,
                        price_delta=price_diff,
                        reason=reason,
                    )
                )

        suggestions.sort(key=lambda x: x.match_score, reverse=True)

        return SubstitutionSuggestResponse(
            original_product_id=orig.id,
            suggestions=suggestions[:5],
        )

    async def create_rule(self, payload: SubstitutionRuleCreate) -> SubstitutionRuleResponse:
        rule = ProductSubstitutionRule(
            original_product_id=payload.original_product_id,
            substitute_product_id=payload.substitute_product_id,
            priority_score=payload.priority_score,
        )
        self.db.add(rule)
        await self.db.flush()
        return SubstitutionRuleResponse.model_validate(rule)
