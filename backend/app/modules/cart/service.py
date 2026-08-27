"""Shopping cart partitioning and checkout computation service."""
from typing import Optional, Dict, Any, List
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import EntityNotFoundError, ValidationError
from app.modules.cart.models import Cart, CartItem
from app.modules.products.models import Product
from app.modules.cart.schemas import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartItemResponse,
    VendorCartGroupResponse,
    CartResponse,
    ApplyCouponRequest,
)
from app.modules.cart.repository import CartRepository
from app.modules.products.repository import ProductRepository
from app.modules.vendors.repository import VendorRepository
from app.modules.coupons.service import CouponService
from app.modules.coupons.schemas import CouponValidateRequest


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CartRepository(db)
        self.prod_repo = ProductRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.coupon_service = CouponService(db)

    async def get_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        return await self._build_cart_response(cart, user_id=user_id)

    async def add_item(
        self, payload: CartItemAddRequest, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> CartResponse:
        product = await self.prod_repo.get_by_id(payload.product_id)
        if not product or product.status != "ACTIVE":
            raise EntityNotFoundError("Product is unavailable for purchase.")

        if payload.quantity < product.min_order_qty or payload.quantity > product.max_order_qty:
            raise ValidationError(
                f"Quantity must be between {product.min_order_qty} and {product.max_order_qty} {product.unit}."
            )

        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        await self.repo.add_item(
            cart_id=cart.id,
            product_id=product.id,
            vendor_id=payload.vendor_id,
            quantity=payload.quantity,
            unit_price=product.sale_price,
            is_variable=product.is_variable_weight,
            notes=payload.notes,
        )

        return await self._build_cart_response(cart, user_id=user_id)

    async def update_item(
        self, item_id: str, payload: CartItemUpdateRequest, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        updated = await self.repo.update_item_qty(item_id, cart.id, payload.quantity, payload.notes)
        if not updated:
            raise EntityNotFoundError("Item not found in cart.")

        return await self._build_cart_response(cart, user_id=user_id)

    async def remove_item(
        self, item_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        await self.repo.remove_item(item_id, cart.id)

        return await self._build_cart_response(cart, user_id=user_id)

    async def clear_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        await self.repo.clear_cart(cart.id)
        await self.repo.set_coupon(cart, None)

        return await self._build_cart_response(cart, user_id=user_id)

    async def apply_coupon(
        self, payload: ApplyCouponRequest, user_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        
        # Load fresh items to compute subtotal
        query = select(CartItem).where(CartItem.cart_id == cart.id)
        res = await self.db.execute(query)
        items = list(res.scalars().all())

        subtotal = sum(i.unit_price * i.quantity for i in items)
        if subtotal <= 0:
            raise ValidationError("Cannot apply coupon to an empty cart.")

        validation = await self.coupon_service.validate_and_calculate_discount(
            CouponValidateRequest(code=payload.coupon_code, order_amount=subtotal),
            user_id=user_id,
        )

        if not validation.is_valid or not validation.coupon_id:
            raise ValidationError(validation.message)

        await self.repo.set_coupon(cart, validation.coupon_id)
        return await self._build_cart_response(cart, user_id=user_id)

    async def remove_coupon(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> CartResponse:
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        await self.repo.set_coupon(cart, None)
        return await self._build_cart_response(cart, user_id=user_id)

    async def _build_cart_response(self, cart: Cart, user_id: Optional[str] = None) -> CartResponse:
        # Query items explicitly with loaded products
        item_query = (
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product).selectinload(Product.images))
        )
        item_res = await self.db.execute(item_query)
        cart_items = list(item_res.scalars().all())

        vendor_buckets = defaultdict(list)
        total_subtotal = 0.0
        total_tax = 0.0

        for item in cart_items:
            item_tot = round(item.unit_price * item.quantity, 2)
            total_subtotal += item_tot

            primary_img = None
            if item.product and item.product.images:
                primary_img = item.product.images[0].image_url

            tax_rate = item.product.tax_rate if item.product else 0.0
            total_tax += item_tot * (tax_rate / 100.0)

            item_dto = CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                vendor_id=item.vendor_id,
                product_name=item.product.name if item.product else "Unknown Product",
                brand=item.product.brand if item.product else "FreshCart",
                sku=item.product.sku if item.product else "",
                unit=item.product.unit if item.product else "pcs",
                unit_price=item.unit_price,
                quantity=item.quantity,
                item_total=item_tot,
                is_variable_weight=item.is_variable_weight,
                notes=item.notes,
                image_url=primary_img,
            )
            vendor_key = item.vendor_id or "FRESHCART_DIRECT"
            vendor_buckets[vendor_key].append(item_dto)

        # Build vendor partition groups
        vendor_groups: List[VendorCartGroupResponse] = []
        for v_id, items in vendor_buckets.items():
            v_name = "FreshCart Central Direct"
            if v_id != "FRESHCART_DIRECT":
                vendor = await self.vendor_repo.get_by_id(v_id)
                if vendor:
                    v_name = vendor.business_name

            group_subtotal = round(sum(i.item_total for i in items), 2)
            vendor_groups.append(
                VendorCartGroupResponse(
                    vendor_id=v_id if v_id != "FRESHCART_DIRECT" else None,
                    vendor_name=v_name,
                    items=items,
                    vendor_subtotal=group_subtotal,
                )
            )

        # Coupon calculation
        discount_amount = 0.0
        coupon_code = None
        if cart.applied_coupon_id:
            coupon = await self.coupon_service.repo.get_by_id(cart.applied_coupon_id)
            if coupon and coupon.is_active and total_subtotal > 0:
                coupon_code = coupon.code
                val_res = await self.coupon_service.validate_and_calculate_discount(
                    CouponValidateRequest(code=coupon.code, order_amount=total_subtotal),
                    user_id=user_id,
                )
                if val_res.is_valid:
                    discount_amount = val_res.discount_amount

        # Delivery fee calculation
        delivery_fee = 0.0
        if total_subtotal > 0 and total_subtotal < settings.FREE_DELIVERY_THRESHOLD:
            delivery_fee = settings.BASE_DELIVERY_FEE

        grand_total = round(max(0.0, total_subtotal - discount_amount + total_tax + delivery_fee), 2)

        return CartResponse(
            cart_id=cart.id,
            vendor_groups=vendor_groups,
            total_items=len(cart_items),
            subtotal=round(total_subtotal, 2),
            coupon_code=coupon_code,
            discount_amount=round(discount_amount, 2),
            tax_estimate=round(total_tax, 2),
            delivery_fee_estimate=round(delivery_fee, 2),
            grand_total=grand_total,
        )
