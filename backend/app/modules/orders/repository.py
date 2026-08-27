"""Order domain database repository layer."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.orders.models import Order, OrderItem, OrderStatusHistory, OrderStatus
from app.modules.shipping.models import Shipment
from app.modules.payments.models import PaymentTransaction


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
                selectinload(Order.shipment),
                selectinload(Order.payments),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_number(self, order_number: str) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.order_number == order_number)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
                selectinload(Order.shipment),
                selectinload(Order.payments),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: str) -> List[Order]:
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.shipment),
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_for_vendor(self, vendor_id: str) -> List[Order]:
        query = (
            select(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(OrderItem.vendor_id == vendor_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.shipment),
            )
            .distinct()
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_order(
        self,
        user_id: str,
        subtotal: float,
        discount_amount: float,
        tax_amount: float,
        delivery_fee: float,
        grand_total: float,
        delivery_address_id: str,
        delivery_slot_id: Optional[str],
        substitution_preference: str,
        customer_notes: Optional[str] = None,
    ) -> Order:
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        order_num = f"ORD-{today_str}-{uuid.uuid4().hex[:6].upper()}"

        order = Order(
            order_number=order_num,
            user_id=user_id,
            status=OrderStatus.CREATED,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            delivery_fee=delivery_fee,
            grand_total=grand_total,
            delivery_address_id=delivery_address_id,
            delivery_slot_id=delivery_slot_id,
            substitution_preference=substitution_preference,
            customer_notes=customer_notes,
        )
        self.db.add(order)
        await self.db.flush()

        # Initial status history
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatus.CREATED,
            notes="Order checkout initiated by customer.",
        )
        self.db.add(history)
        await self.db.flush()
        return order

    async def add_order_item(
        self,
        order_id: str,
        product_id: str,
        vendor_id: Optional[str],
        product_name: str,
        sku: str,
        unit: str,
        unit_price: float,
        ordered_qty: float,
        is_variable_weight: bool,
    ) -> OrderItem:
        subtot = round(ordered_qty * unit_price, 2)
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            vendor_id=vendor_id,
            product_name=product_name,
            sku=sku,
            unit=unit,
            unit_price=unit_price,
            ordered_qty=ordered_qty,
            item_subtotal=subtot,
            is_variable_weight=is_variable_weight,
            item_status="PENDING",
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def record_status_change(
        self, order: Order, new_status: str, actor_id: Optional[str] = None, notes: Optional[str] = None
    ) -> None:
        old_status = order.status
        order.status = new_status
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=old_status,
            to_status=new_status,
            actor_id=actor_id,
            notes=notes,
        )
        self.db.add(history)
        await self.db.flush()

    async def update_item_picking(
        self,
        item: OrderItem,
        actual_qty: float,
        status: str = "PICKED",
        substituted_product_id: Optional[str] = None,
    ) -> OrderItem:
        item.picked_qty = actual_qty
        item.final_item_total = round(actual_qty * item.unit_price, 2)
        item.item_status = status
        if substituted_product_id:
            item.substituted_product_id = substituted_product_id
        await self.db.flush()
        return item

    async def reconcile_order_grand_total(self, order: Order) -> float:
        """Recomputes total based on actual scale weights and picked items."""
        final_item_sum = 0.0
        for item in order.items:
            if item.item_status == "OUT_OF_STOCK":
                continue
            qty = item.picked_qty if item.picked_qty is not None else item.ordered_qty
            final_item_sum += qty * item.unit_price

        final_total = round(max(0.0, final_item_sum - order.discount_amount + order.tax_amount + order.delivery_fee), 2)
        order.final_adjusted_total = final_total
        await self.db.flush()
        return final_total
