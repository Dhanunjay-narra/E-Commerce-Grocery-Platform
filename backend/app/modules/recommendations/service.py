"""Smart Replenishment forecasting, Meal Pantry planning, and AI recommendation service."""
from datetime import datetime, timezone, date, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError
from app.modules.recommendations.models import SmartGroceryPlan, SmartPlanItem, ReplenishmentCadence
from app.modules.recommendations.schemas import (
    SmartGroceryPlanCreate,
    SmartGroceryPlanResponse,
    SmartPlanItemResponse,
    ReplenishmentAlertItem,
    FrequentlyBoughtTogetherResponse,
)
from app.modules.products.models import Product
from app.modules.products.schemas import ProductResponse
from app.modules.products.repository import ProductRepository
from app.modules.cart.service import CartService
from app.modules.cart.schemas import CartItemAddRequest, CartResponse
from app.modules.orders.models import Order, OrderItem


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prod_repo = ProductRepository(db)
        self.cart_service = CartService(db)

    async def get_replenishment_alerts(self, user_id: str) -> List[ReplenishmentAlertItem]:
        """Calculates personalized replenishment alerts from past purchase cadence."""
        today = date.today()
        # Query user orders
        orders_query = (
            select(Order)
            .where(and_(Order.user_id == user_id, Order.status != "CANCELLED"))
            .options(selectinload(Order.items).selectinload(OrderItem.order))
            .order_by(Order.created_at.asc())
        )
        orders_res = await self.db.execute(orders_query)
        orders = list(orders_res.scalars().all())

        alerts: List[ReplenishmentAlertItem] = []
        product_purchase_history = {}

        for o in orders:
            for item in o.items:
                if item.product_id not in product_purchase_history:
                    product_purchase_history[item.product_id] = []
                product_purchase_history[item.product_id].append(o.created_at)

        for p_id, timestamps in product_purchase_history.items():
            if len(timestamps) >= 2:
                # Calculate average cadence interval
                intervals = []
                for i in range(1, len(timestamps)):
                    diff_days = (timestamps[i] - timestamps[i - 1]).total_seconds() / 86400.0
                    intervals.append(diff_days)

                avg_interval = sum(intervals) / len(intervals)
                last_dt = timestamps[-1]
                predicted_runout = (last_dt + timedelta(days=avg_interval)).date()
                days_left = (predicted_runout - today).days

                # If runout within next 3 days
                if days_left <= 3:
                    prod = await self.prod_repo.get_by_id(p_id)
                    if prod and prod.status == "ACTIVE":
                        p_dto = self._map_product_dto(prod)
                        alerts.append(
                            ReplenishmentAlertItem(
                                product=p_dto,
                                average_interval_days=round(avg_interval, 1),
                                last_purchased_at=last_dt,
                                predicted_runout_date=predicted_runout,
                                confidence_score=0.92,
                                days_until_runout=days_left,
                                is_urgent=(days_left <= 1),
                            )
                        )

        alerts.sort(key=lambda x: x.days_until_runout)
        return alerts

    async def get_frequently_bought_together(self, product_id: str) -> FrequentlyBoughtTogetherResponse:
        """Finds co-occurring products in previous orders or category peers."""
        # Find other products in orders that contained product_id
        order_ids_subq = (
            select(OrderItem.order_id)
            .where(OrderItem.product_id == product_id)
            .distinct()
        )
        
        co_query = (
            select(OrderItem.product_id, func.count(OrderItem.id).label("freq"))
            .where(and_(OrderItem.order_id.in_(order_ids_subq), OrderItem.product_id != product_id))
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.id).desc())
            .limit(4)
        )
        co_res = await self.db.execute(co_query)
        co_rows = co_res.all()

        recommended: List[ProductResponse] = []
        for row in co_rows:
            p = await self.prod_repo.get_by_id(row[0])
            if p and p.status == "ACTIVE":
                recommended.append(self._map_product_dto(p))

        if len(recommended) < 3:
            # Fallback to same-category top rated items
            orig = await self.prod_repo.get_by_id(product_id)
            if orig:
                cat_peers = (
                    select(Product)
                    .where(and_(Product.category_id == orig.category_id, Product.id != orig.id, Product.status == "ACTIVE"))
                    .options(selectinload(Product.images))
                    .order_by(Product.rating_average.desc())
                    .limit(4)
                )
                peers_res = await self.db.execute(cat_peers)
                for p in peers_res.scalars().all():
                    if p.id not in [r.id for r in recommended]:
                        recommended.append(self._map_product_dto(p))

        return FrequentlyBoughtTogetherResponse(
            primary_product_id=product_id,
            recommended_products=recommended[:4],
        )

    async def create_smart_plan(self, user_id: str, payload: SmartGroceryPlanCreate) -> SmartGroceryPlanResponse:
        plan = SmartGroceryPlan(
            user_id=user_id,
            plan_name=payload.plan_name,
            frequency_days=payload.frequency_days,
            is_recurring_auto_order=payload.is_recurring_auto_order,
            next_replenishment_date=payload.next_replenishment_date,
        )
        self.db.add(plan)
        await self.db.flush()

        for item in payload.items:
            p_item = SmartPlanItem(
                plan_id=plan.id,
                product_id=item.product_id,
                quantity=item.quantity,
                aisle_category=item.aisle_category,
            )
            self.db.add(p_item)

        await self.db.flush()
        return await self.get_smart_plan(plan.id, user_id)

    async def get_smart_plan(self, plan_id: str, user_id: str) -> SmartGroceryPlanResponse:
        query = (
            select(SmartGroceryPlan)
            .where(and_(SmartGroceryPlan.id == plan_id, SmartGroceryPlan.user_id == user_id))
            .options(selectinload(SmartGroceryPlan.items).selectinload(SmartPlanItem.product).selectinload(Product.images))
        )
        result = await self.db.execute(query)
        plan = result.scalar_one_or_none()
        if not plan:
            raise EntityNotFoundError("Smart grocery plan not found.")

        items_dto = []
        for i in plan.items:
            p_dto = self._map_product_dto(i.product) if i.product else None
            items_dto.append(
                SmartPlanItemResponse(
                    id=i.id,
                    product_id=i.product_id,
                    quantity=i.quantity,
                    aisle_category=i.aisle_category,
                    product=p_dto,
                )
            )

        return SmartGroceryPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            plan_name=plan.plan_name,
            frequency_days=plan.frequency_days,
            is_recurring_auto_order=plan.is_recurring_auto_order,
            next_replenishment_date=plan.next_replenishment_date,
            is_active=plan.is_active,
            items=items_dto,
            created_at=plan.created_at,
        )

    async def generate_cart_from_plan(self, plan_id: str, user_id: str) -> CartResponse:
        """Pours an entire weekly replenishment plan directly into the active cart."""
        plan = await self.get_smart_plan(plan_id, user_id)
        for item in plan.items:
            await self.cart_service.add_item(
                CartItemAddRequest(
                    product_id=item.product_id,
                    quantity=item.quantity,
                ),
                user_id=user_id,
            )
        return await self.cart_service.get_cart(user_id=user_id)

    def _map_product_dto(self, p: Product) -> ProductResponse:
        primary_img = next((img.image_url for img in p.images if img.is_primary), None)
        if not primary_img and p.images:
            primary_img = p.images[0].image_url

        return ProductResponse(
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
