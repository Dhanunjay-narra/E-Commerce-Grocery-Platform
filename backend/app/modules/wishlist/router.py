"""Wishlist and Saved Item API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.authentication.permissions import get_current_user
from app.modules.users.models import User
from app.modules.wishlist.schemas import (
    WishlistCreate,
    WishlistItemAdd,
    WishlistResponse,
    MoveToCartResponse,
)
from app.modules.wishlist.service import WishlistService

router = APIRouter(prefix="/wishlists", tags=["Wishlist"])


@router.get("", response_model=List[WishlistResponse])
async def list_wishlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all saved grocery wishlists with automatic price-drop alerts."""
    service = WishlistService(db)
    return await service.list_wishlists(current_user.id)


@router.post("", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def create_wishlist(
    payload: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new named grocery wishlist or household shared list."""
    service = WishlistService(db)
    return await service.create_wishlist(current_user.id, payload)


@router.post("/{wishlist_id}/items", response_model=WishlistResponse)
async def add_item_to_wishlist(
    wishlist_id: str,
    payload: WishlistItemAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Adds a product to the selected wishlist."""
    service = WishlistService(db)
    return await service.add_item(wishlist_id, current_user.id, payload)


@router.delete("/{wishlist_id}/items/{item_id}", response_model=WishlistResponse)
async def remove_item_from_wishlist(
    wishlist_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes a product from the wishlist."""
    service = WishlistService(db)
    return await service.remove_item(wishlist_id, item_id, current_user.id)


@router.post("/{wishlist_id}/move-to-cart", response_model=MoveToCartResponse)
async def move_wishlist_to_cart(
    wishlist_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transfers all items from a wishlist directly into active shopping cart in one click."""
    service = WishlistService(db)
    return await service.move_all_to_cart(wishlist_id, current_user.id)
