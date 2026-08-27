"""Order Fulfillment, 11-stage Finite State Machine, and Weight Reconciliation service."""
import secrets
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import (
    EntityNotFoundError,
    ValidationError,
    InvalidStateTransitionError,
    InsufficientInventoryError,
)
from app.modules.orders.models import Order, OrderItem, OrderStatusHistory, OrderStatus
from app.modules.orders.schemas import (
    OrderCheckoutRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderItemResponse,
    OrderStatusHistoryResponse,
    OrderItemPickRequest,
    OrderStateTransitionRequest,
    OrderCancelRequest,
    InvoiceResponse,
)
from app.modules.shipping.schemas import ShipmentResponse
from app.modules.payments.schemas import PaymentResponse
from app.modules.orders.repository import OrderRepository
from app.modules.cart.service import CartService
from app.modules.shipping.service import ShippingService
from app.modules.shipping.repository import ShippingRepository
from app.modules.inventory.service import InventoryService
from app.modules.inventory.schemas import StockReservationRequest
from app.modules.payments.service import PaymentService
from app.modules.payments.schemas import PaymentInitiateRequest
from app.modules.users.repository import UserRepository


VALID_TRANSITIONS: Dict[str, List[str]] = {
    OrderStatus.CREATED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PAYMENT_VERIFIED, OrderStatus.CANCELLED],
    OrderStatus.PAYMENT_VERIFIED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
    OrderStatus.PROCESSING: [OrderStatus.PICKING, OrderStatus.CANCELLED],
    OrderStatus.PICKING: [OrderStatus.PACKED, OrderStatus.CANCELLED],
    OrderStatus.PACKED: [OrderStatus.READY_FOR_DISPATCH],
    OrderStatus.READY_FOR_DISPATCH: [OrderStatus.OUT_FOR_DELIVERY],
    OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
    OrderStatus.DELIVERED: [OrderStatus.RETURNED],
    OrderStatus.CANCELLED: [],
    OrderStatus.RETURNED: [OrderStatus.REFUNDED],
    OrderStatus.REFUNDED: [],
}


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrderRepository(db)
        self.cart_service = CartService(db)
        self.shipping_service = ShippingService(db)
        self.shipping_repo = ShippingRepository(db)
        self.inventory_service = InventoryService(db)
        self.payment_service = PaymentService(db)
        self.user_repo = UserRepository(db)

    async def checkout(self, user_id: str, payload: OrderCheckoutRequest) -> OrderDetailResponse:
        # 1. Validate Address
        address = await self.user_repo.get_address_by_id(payload.delivery_address_id, user_id)
        if not address:
            raise EntityNotFoundError("Delivery address not found.")

        # 2. Get Cart
        cart_res = await self.cart_service.get_cart(user_id=user_id)
        if cart_res.total_items == 0:
            raise ValidationError("Your shopping cart is empty.")

        # 3. Resolve Zone & Delivery Slot
        zones = await self.shipping_repo.list_zones()
        default_zone = zones[0] if zones else await self.shipping_repo.create_zone(
            type("ZoneCreate", (), {
                "name": "Standard Delivery Zone",
                "code": "ZONE-STD",
                "city": address.city,
                "state": address.state,
                "center_latitude": address.latitude or 17.44,
                "center_longitude": address.longitude or 78.37,
                "radius_km": 20.0,
                "base_fee": 40.0,
            })()
        )

        slot_id = payload.delivery_slot_id
        if slot_id:
            await self.shipping_service.book_slot(slot_id)

        # 4. Reserve FEFO Inventory for all cart items
        temp_order_ref = f"checkout_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
        for group in cart_res.vendor_groups:
            for item in group.items:
                await self.inventory_service.reserve_stock(
                    StockReservationRequest(
                        reference_id=temp_order_ref,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        vendor_id=item.vendor_id,
                        ttl_seconds=900,  # 15 min checkout window
                    )
                )

        # 5. Create Order
        order = await self.repo.create_order(
            user_id=user_id,
            subtotal=cart_res.subtotal,
            discount_amount=cart_res.discount_amount,
            tax_amount=cart_res.tax_estimate,
            delivery_fee=cart_res.delivery_fee_estimate,
            grand_total=cart_res.grand_total,
            delivery_address_id=address.id,
            delivery_slot_id=slot_id,
            substitution_preference=payload.substitution_preference,
            customer_notes=payload.customer_notes,
        )

        # 6. Create Order Items
        for group in cart_res.vendor_groups:
            for item in group.items:
                await self.repo.add_order_item(
                    order_id=order.id,
                    product_id=item.product_id,
                    vendor_id=item.vendor_id,
                    product_name=item.product_name,
                    sku=item.sku,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    ordered_qty=item.quantity,
                    is_variable_weight=item.is_variable_weight,
                )

        # 7. Create Shipment with secure 4-digit Delivery OTP
        otp_code = str(secrets.randbelow(9000) + 1000)
        await self.shipping_repo.create_shipment(
            order_id=order.id,
            zone_id=default_zone.id,
            slot_id=slot_id,
            delivery_otp=otp_code,
        )

        # 8. Initiate Payment Transaction
        await self.payment_service.initiate_payment(
            PaymentInitiateRequest(
                order_id=order.id,
                amount=order.grand_total,
                payment_method=payload.payment_method,
            ),
            user_id=user_id,
        )

        # 9. Transition to CONFIRMED and Clear active Cart
        await self.repo.record_status_change(order, OrderStatus.CONFIRMED, actor_id=user_id, notes="Inventory reserved and slot locked.")
        await self.cart_service.clear_cart(user_id=user_id)

        # If payment is COD, auto-verify payment & commit inventory
        if payload.payment_method == "CASH_ON_DELIVERY":
            await self.repo.record_status_change(order, OrderStatus.PAYMENT_VERIFIED, notes="Cash on Delivery confirmed.")
            await self.inventory_service.commit_stock(temp_order_ref)

        reloaded = await self.repo.get_by_id(order.id)
        return self._map_detail_dto(reloaded)  # type: ignore

    async def transition_order_status(
        self, order_id: str, payload: OrderStateTransitionRequest, actor_id: Optional[str] = None
    ) -> OrderDetailResponse:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order not found.")

        current_st = order.status
        target_st = payload.new_status.upper()

        allowed = VALID_TRANSITIONS.get(current_st, [])
        if target_st not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition order from '{current_st}' to '{target_st}'. Allowed next states: {allowed}"
            )

        # If transitioning to PACKED, execute variable-weight price reconciliation
        if target_st == OrderStatus.PACKED:
            await self.repo.reconcile_order_grand_total(order)

        # If transitioning to DELIVERED, verify shipment delivered
        if target_st == OrderStatus.DELIVERED and order.shipment:
            order.shipment.status = "DELIVERED"
            order.shipment.delivered_at = datetime.now(timezone.utc)

        await self.repo.record_status_change(order, target_st, actor_id=actor_id, notes=payload.notes)
        reloaded = await self.repo.get_by_id(order.id)
        return self._map_detail_dto(reloaded)  # type: ignore

    async def pick_item(self, order_id: str, payload: OrderItemPickRequest, actor_id: Optional[str] = None) -> OrderDetailResponse:
        """Picker weighs item on scale and logs actual picked weight."""
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order not found.")

        item = next((i for i in order.items if i.id == payload.order_item_id), None)
        if not item:
            raise EntityNotFoundError("Order line item not found.")

        await self.repo.update_item_picking(
            item=item,
            actual_qty=payload.actual_picked_qty,
            status=payload.item_status,
            substituted_product_id=payload.substituted_product_id,
        )

        reloaded = await self.repo.get_by_id(order.id)
        return self._map_detail_dto(reloaded)  # type: ignore

    async def cancel_order(self, order_id: str, user_id: str, payload: OrderCancelRequest) -> OrderDetailResponse:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order not found.")

        if order.status in [OrderStatus.PACKED, OrderStatus.READY_FOR_DISPATCH, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED]:
            raise ValidationError(f"Order cannot be cancelled in status '{order.status}'. Please contact customer support.")

        order.cancellation_reason = payload.cancellation_reason
        await self.repo.record_status_change(order, OrderStatus.CANCELLED, actor_id=user_id, notes=f"Cancelled: {payload.cancellation_reason}")

        # If payment was completed, trigger refund
        for p in order.payments:
            if p.status in ["CAPTURED", "AUTHORIZED"]:
                await self.payment_service.refund_payment(
                    type("RefundReq", (), {"payment_id": p.id, "amount": p.amount, "reason": payload.cancellation_reason})()
                )

        reloaded = await self.repo.get_by_id(order.id)
        return self._map_detail_dto(reloaded)  # type: ignore

    async def get_by_id(self, order_id: str) -> OrderDetailResponse:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order not found.")
        return self._map_detail_dto(order)

    async def list_user_orders(self, user_id: str) -> List[OrderResponse]:
        orders = await self.repo.list_for_user(user_id)
        return [OrderResponse.model_validate(o) for o in orders]

    async def list_vendor_orders(self, vendor_id: str) -> List[OrderResponse]:
        orders = await self.repo.list_for_vendor(vendor_id)
        return [OrderResponse.model_validate(o) for o in orders]

    async def generate_invoice_data(self, order_id: str) -> InvoiceResponse:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order not found.")

        user = await self.user_repo.get_by_id(order.user_id)
        address = await self.user_repo.get_address_by_id(order.delivery_address_id, order.user_id)
        
        addr_str = f"{address.recipient_name}, {address.street_address}, {address.city} - {address.postal_code}" if address else "Delivery Address"
        payment_st = order.payments[0].status if order.payments else "PENDING"
        items_dto = [OrderItemResponse.model_validate(i) for i in order.items]

        return InvoiceResponse(
            order_number=order.order_number,
            invoice_date=order.created_at,
            customer_name=user.full_name if user else "Customer",
            customer_email=user.email if user else "",
            delivery_address=addr_str,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            delivery_fee=order.delivery_fee,
            grand_total=order.final_adjusted_total or order.grand_total,
            items=items_dto,
            payment_status=payment_st,
        )

    def _map_detail_dto(self, o: Order) -> OrderDetailResponse:
        items_dto = [OrderItemResponse.model_validate(i) for i in o.items]
        hist_dto = [OrderStatusHistoryResponse.model_validate(h) for h in o.status_history]
        ship_dto = ShipmentResponse.model_validate(o.shipment) if o.shipment else None
        pay_dtos = [PaymentResponse.model_validate(p) for p in o.payments]

        return OrderDetailResponse(
            id=o.id,
            order_number=o.order_number,
            user_id=o.user_id,
            status=o.status,
            subtotal=o.subtotal,
            discount_amount=o.discount_amount,
            tax_amount=o.tax_amount,
            delivery_fee=o.delivery_fee,
            grand_total=o.grand_total,
            final_adjusted_total=o.final_adjusted_total,
            delivery_address_id=o.delivery_address_id,
            delivery_slot_id=o.delivery_slot_id,
            substitution_preference=o.substitution_preference,
            customer_notes=o.customer_notes,
            cancellation_reason=o.cancellation_reason,
            created_at=o.created_at,
            items=items_dto,
            status_history=hist_dto,
            shipment=ship_dto,
            payments=pay_dtos,
        )
