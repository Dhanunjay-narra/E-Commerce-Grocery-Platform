"""Wishlist and Price-Drop Alert business service layer."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError
from app.modules.wishlist.models import Wishlist, WishlistItem
from app.modules.products.models import Product
from app.modules.wishlist.schemas import (
    WishlistCreate,
    WishlistItemAdd,
    WishlistResponse,
    WishlistItemResponse,
    MoveToCartResponse,
)
from app.modules.wishlist.repository import WishlistRepository
from app.modules.products.repository import ProductRepository
from app.modules.cart.service import CartService
from app.modules.cart.schemas import CartItemAddRequest


class WishlistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WishlistRepository(db)
        self.prod_repo = ProductRepository(db)
        self.cart_service = CartService(db)

    async def list_wishlists(self, user_id: str) -> List[WishlistResponse]:
        wishlists = await self.repo.list_user_wishlists(user_id)
        if not wishlists:
            # Create default wishlist if none exists
            default_wl = await self.repo.create(user_id=user_id, name="My Grocery Wishlist")
            wishlists = [default_wl]

        result = []
        for wl in wishlists:
            dto = await self._build_wishlist_dto(wl)
            result.append(dto)
        return result

    async def create_wishlist(self, user_id: str, payload: WishlistCreate) -> WishlistResponse:
        wl = await self.repo.create(
            user_id=user_id,
            name=payload.name,
            is_shared=payload.is_shared_with_household,
            is_public=payload.is_public,
        )
        return await self._build_wishlist_dto(wl)

    async def add_item(self, wishlist_id: str, user_id: str, payload: WishlistItemAdd) -> WishlistResponse:
        wl = await self.repo.get_by_id(wishlist_id, user_id)
        if not wl:
            raise EntityNotFoundError("Wishlist not found.")

        product = await self.prod_repo.get_by_id(payload.product_id)
        if not product:
            raise EntityNotFoundError("Product not found.")

        await self.repo.add_item(
            wishlist_id=wl.id,
            product_id=product.id,
            price=product.sale_price,
            desired_qty=payload.desired_qty,
        )

        return await self._build_wishlist_dto(wl)

    async def remove_item(self, wishlist_id: str, item_id: str, user_id: str) -> WishlistResponse:
        wl = await self.repo.get_by_id(wishlist_id, user_id)
        if not wl:
            raise EntityNotFoundError("Wishlist not found.")

        await self.repo.remove_item(wishlist_id, item_id)
        return await self._build_wishlist_dto(wl)

    async def move_all_to_cart(self, wishlist_id: str, user_id: str) -> MoveToCartResponse:
        wl = await self.repo.get_by_id(wishlist_id, user_id)
        if not wl:
            raise EntityNotFoundError("Wishlist not found.")

        item_query = (
            select(WishlistItem)
            .where(WishlistItem.wishlist_id == wishlist_id)
            .options(selectinload(WishlistItem.product))
        )
        res = await self.db.execute(item_query)
        items = list(res.scalars().all())

        items_moved = 0
        for item in items:
            if item.product and item.product.status == "ACTIVE":
                await self.cart_service.add_item(
                    CartItemAddRequest(
                        product_id=item.product_id,
                        quantity=item.desired_qty,
                    ),
                    user_id=user_id,
                )
                items_moved += 1

        return MoveToCartResponse(
            success=True,
            items_moved_count=items_moved,
            message=f"Successfully transferred {items_moved} items from wishlist directly into your cart.",
        )

    async def _build_wishlist_dto(self, wl: Wishlist) -> WishlistResponse:
        item_query = (
            select(WishlistItem)
            .where(WishlistItem.wishlist_id == wl.id)
            .options(selectinload(WishlistItem.product).selectinload(Product.images))
        )
        item_res = await self.db.execute(item_query)
        items = list(item_res.scalars().all())

        items_dto = []
        for i in items:
            current_p = i.product.sale_price if i.product else i.added_price
            price_dropped = current_p < i.added_price
            drop_amount = round(max(0.0, i.added_price - current_p), 2)

            primary_img = None
            if i.product and i.product.images:
                primary_img = i.product.images[0].image_url

            items_dto.append(
                WishlistItemResponse(
                    id=i.id,
                    product_id=i.product_id,
                    product_name=i.product.name if i.product else "Unknown Product",
                    brand=i.product.brand if i.product else "FreshCart",
                    unit=i.product.unit if i.product else "pcs",
                    current_price=current_p,
                    added_price=i.added_price,
                    price_dropped=price_dropped,
                    price_drop_amount=drop_amount,
                    desired_qty=i.desired_qty,
                    image_url=primary_img,
                    created_at=i.created_at,
                )
            )

        return WishlistResponse(
            id=wl.id,
            user_id=wl.user_id,
            name=wl.name,
            is_shared_with_household=wl.is_shared_with_household,
            is_public=wl.is_public,
            items=items_dto,
            created_at=wl.created_at,
        )
