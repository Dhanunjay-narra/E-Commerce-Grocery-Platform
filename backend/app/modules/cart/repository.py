"""Shopping Cart database repository layer."""
from typing import Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.cart.models import Cart, CartItem
from app.modules.products.models import Product


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Cart:
        conditions = []
        if user_id:
            conditions.append(Cart.user_id == user_id)
        elif session_id:
            conditions.append(Cart.session_id == session_id)
        else:
            raise ValueError("Either user_id or session_id must be provided to resolve cart.")

        query = (
            select(Cart)
            .where(and_(*conditions))
            .options(
                selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.images),
                selectinload(Cart.coupon),
            )
        )
        result = await self.db.execute(query)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            self.db.add(cart)
            await self.db.flush()
            # Reload with relationships
            return await self.get_cart_by_id(cart.id)  # type: ignore

        return cart

    async def get_cart_by_id(self, cart_id: str) -> Optional[Cart]:
        query = (
            select(Cart)
            .where(Cart.id == cart_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.images),
                selectinload(Cart.coupon),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_item(
        self, cart_id: str, product_id: str, vendor_id: Optional[str], quantity: float, unit_price: float, is_variable: bool, notes: Optional[str] = None
    ) -> CartItem:
        # Check if item already exists in this cart for this vendor
        query = select(CartItem).where(
            and_(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
                CartItem.vendor_id == vendor_id,
            )
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
            if notes:
                item.notes = notes
        else:
            item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                vendor_id=vendor_id,
                quantity=quantity,
                unit_price=unit_price,
                is_variable_weight=is_variable,
                notes=notes,
            )
            self.db.add(item)

        await self.db.flush()
        return item

    async def update_item_qty(self, item_id: str, cart_id: str, quantity: float, notes: Optional[str] = None) -> Optional[CartItem]:
        query = select(CartItem).where(and_(CartItem.id == item_id, CartItem.cart_id == cart_id))
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        if item:
            item.quantity = quantity
            if notes is not None:
                item.notes = notes
            await self.db.flush()
        return item

    async def remove_item(self, item_id: str, cart_id: str) -> bool:
        stmt = delete(CartItem).where(and_(CartItem.id == item_id, CartItem.cart_id == cart_id))
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def clear_cart(self, cart_id: str) -> None:
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        await self.db.execute(stmt)

    async def set_coupon(self, cart: Cart, coupon_id: Optional[str]) -> None:
        cart.applied_coupon_id = coupon_id
        await self.db.flush()
