"""Search and intelligent grocery discovery service."""
import re
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.products.models import Product, ProductImage
from app.modules.categories.models import Category
from app.modules.products.schemas import ProductResponse
from app.modules.search.schemas import (
    SearchResponse,
    SearchFacets,
    SearchFacetItem,
    SearchSuggestion,
    PopularSearch,
)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_organic: Optional[bool] = None,
        is_vegan: Optional[bool] = None,
        is_gluten_free: Optional[bool] = None,
        is_variable_weight: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SearchResponse:
        clean_q = query.strip().lower() if query else ""
        detected_intents = self._parse_grocery_intents(clean_q)

        # Base active products
        base_query = (
            select(Product)
            .where(and_(Product.is_deleted == False, Product.status == "ACTIVE"))
            .options(selectinload(Product.images), selectinload(Product.category))
        )

        all_products_res = await self.db.execute(base_query)
        all_products = list(all_products_res.scalars().all())

        # Match scoring and typo tolerance
        matched_scored: List[Tuple[Product, int]] = []
        tokens = [t for t in re.split(r"\s+", clean_q) if t]

        for p in all_products:
            score = 0
            p_name = p.name.lower()
            p_brand = p.brand.lower()
            p_desc = (p.description or "").lower()
            p_cat = (p.category.name if p.category else "").lower()

            if not tokens:
                # No query specified: all match
                score = 100
            else:
                for token in tokens:
                    if token in p_name:
                        score += 50
                    elif token in p_brand:
                        score += 40
                    elif token in p_cat:
                        score += 30
                    elif token in p_desc:
                        score += 10
                    else:
                        # Check typo tolerance on word tokens (distance <= 2)
                        for word in p_name.split() + p_brand.split():
                            dist = levenshtein_distance(token, word)
                            if dist <= 1:
                                score += 25
                            elif dist == 2 and len(token) > 4:
                                score += 15

            if score > 0:
                # Apply explicit filters
                if category_id and p.category_id != category_id:
                    continue
                if brand and p.brand.lower() != brand.lower():
                    continue
                if min_price is not None and p.sale_price < min_price:
                    continue
                if max_price is not None and p.sale_price > max_price:
                    continue
                if is_organic is not None and p.is_organic != is_organic:
                    continue
                if is_vegan is not None and p.is_vegan != is_vegan:
                    continue
                if is_gluten_free is not None and p.is_gluten_free != is_gluten_free:
                    continue
                if is_variable_weight is not None and p.is_variable_weight != is_variable_weight:
                    continue

                matched_scored.append((p, score))

        # Sort by score descending, then rating
        matched_scored.sort(key=lambda x: (x[1], x[0].rating_average), reverse=True)
        total = len(matched_scored)
        paged_items = matched_scored[skip : skip + limit]

        product_dtos = []
        for p, _ in paged_items:
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url

            product_dtos.append(
                ProductResponse(
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
            )

        # Aggregate dynamic facets from all matches
        facets = self._build_facets([p for p, _ in matched_scored])

        return SearchResponse(
            query=query,
            corrected_query=None,
            items=product_dtos,
            total=total,
            facets=facets,
            detected_intents=detected_intents,
        )

    async def get_suggestions(self, prefix: str, limit: int = 8) -> List[SearchSuggestion]:
        if not prefix or len(prefix.strip()) < 2:
            return []

        clean_p = prefix.strip().lower()
        suggestions: List[SearchSuggestion] = []

        # 1. Product Name matches
        p_query = (
            select(Product.id, Product.name, Product.brand)
            .where(and_(Product.is_deleted == False, Product.name.ilike(f"%{clean_p}%")))
            .limit(5)
        )
        p_res = await self.db.execute(p_query)
        for row in p_res.all():
            suggestions.append(
                SearchSuggestion(
                    text=f"{row.name} ({row.brand})",
                    product_id=row.id,
                    type="product",
                )
            )

        # 2. Category matches
        c_query = (
            select(Category.name, Category.slug)
            .where(and_(Category.is_deleted == False, Category.name.ilike(f"%{clean_p}%")))
            .limit(3)
        )
        c_res = await self.db.execute(c_query)
        for row in c_res.all():
            suggestions.append(
                SearchSuggestion(
                    text=f"in {row.name}",
                    category=row.name,
                    type="category",
                )
            )

        return suggestions[:limit]

    async def get_popular_searches(self) -> List[PopularSearch]:
        return [
            PopularSearch(keyword="Organic Farm Milk", search_count=15420),
            PopularSearch(keyword="Farm Fresh Tomatoes", search_count=12300),
            PopularSearch(keyword="Whole Wheat Atta 5kg", search_count=10890),
            PopularSearch(keyword="Greek Yogurt", search_count=8760),
            PopularSearch(keyword="Alphonso Mangoes", search_count=8450),
            PopularSearch(keyword="Sourdough Bread", search_count=6120),
        ]

    def _parse_grocery_intents(self, query: str) -> List[str]:
        intents = []
        if "organic" in query:
            intents.append("INTENT_ORGANIC_PREFERENCE")
        if "vegan" in query:
            intents.append("INTENT_VEGAN_PREFERENCE")
        if "gluten" in query:
            intents.append("INTENT_GLUTEN_FREE_PREFERENCE")
        if any(k in query for k in ["kid", "baby", "infant"]):
            intents.append("INTENT_CHILD_SAFE_NUTRITION")
        if any(k in query for k in ["diabetic", "sugar free", "low sugar"]):
            intents.append("INTENT_DIABETIC_FRIENDLY")
        return intents

    def _build_facets(self, products: List[Product]) -> SearchFacets:
        cat_counts: Dict[str, int] = {}
        brand_counts: Dict[str, int] = {}
        diet_counts = {"is_organic": 0, "is_vegan": 0, "is_vegetarian": 0, "is_gluten_free": 0}
        price_buckets = {"Under ₹100": 0, "₹100 - ₹300": 0, "₹300 - ₹500": 0, "Above ₹500": 0}

        for p in products:
            cat_name = p.category.name if p.category else "Other"
            cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1

            brand_counts[p.brand] = brand_counts.get(p.brand, 0) + 1

            if p.is_organic:
                diet_counts["is_organic"] += 1
            if p.is_vegan:
                diet_counts["is_vegan"] += 1
            if p.is_vegetarian:
                diet_counts["is_vegetarian"] += 1
            if p.is_gluten_free:
                diet_counts["is_gluten_free"] += 1

            if p.sale_price < 100:
                price_buckets["Under ₹100"] += 1
            elif p.sale_price <= 300:
                price_buckets["₹100 - ₹300"] += 1
            elif p.sale_price <= 500:
                price_buckets["₹300 - ₹500"] += 1
            else:
                price_buckets["Above ₹500"] += 1

        cat_items = [SearchFacetItem(label=k, value=k, count=v) for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])]
        brand_items = [SearchFacetItem(label=k, value=k, count=v) for k, v in sorted(brand_counts.items(), key=lambda x: -x[1])]
        price_items = [SearchFacetItem(label=k, value=k, count=v) for k, v in price_buckets.items() if v > 0]

        return SearchFacets(
            categories=cat_items,
            brands=brand_items,
            dietary=diet_counts,
            price_ranges=price_items,
        )
