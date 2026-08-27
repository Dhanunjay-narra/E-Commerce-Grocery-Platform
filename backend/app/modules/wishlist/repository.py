"""Wishlist database repository layer."""
from typing import List, Optional
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.wishlist.models import Wishlist, WishlistItem
from app.modules.products.models import Product


class WishlistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, wishlist_id: str, user_id: str) -> Optional[Wishlist]:
        query = (
            select(Wishlist)
            .where(and_(Wishlist.id == wishlist_id, Wishlist.user_id == user_id))
            .options(
                selectinload(Wishlist.items).selectinload(WishlistItem.product).selectinload(Product.images)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_user_wishlists(self, user_id: str) -> List[Wishlist]:
        query = (
            select(Wishlist)
            .where(Wishlist.user_id == user_id)
            .options(
                selectinload(Wishlist.items).selectinload(WishlistItem.product).selectinload(Product.images)
            )
            .order_by(Wishlist.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, user_id: str, name: str, is_shared: bool = False, is_public: bool = False) -> Wishlist:
        wl = Wishlist(
            user_id=user_id,
            name=name,
            is_shared_with_household=is_shared,
            is_public=is_public,
        )
        self.db.add(wl)
        await self.db.flush()
        return await self.get_by_id(wl.id, user_id)  # type: ignore

    async def add_item(self, wishlist_id: str, product_id: str, price: float, desired_qty: float = 1.0) -> WishlistItem:
        query = select(WishlistItem).where(
            and_(WishlistItem.wishlist_id == wishlist_id, WishlistItem.product_id == product_id)
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()

        if item:
            item.desired_qty += desired_qty
        else:
            item = WishlistItem(
                wishlist_id=wishlist_id,
                product_id=product_id,
                desired_qty=desired_qty,
                added_price=price,
            )
            self.db.add(item)

        await self.db.flush()
        return item

    async def remove_item(self, wishlist_id: str, item_id: str) -> bool:
        stmt = delete(WishlistItem).where(
            and_(WishlistItem.id == item_id, WishlistItem.wishlist_id == wishlist_id)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_wishlist(self, wishlist: Wishlist) -> None:
        await self.db.delete(wishlist)
        await self.db.flush()
