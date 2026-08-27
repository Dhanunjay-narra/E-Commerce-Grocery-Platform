"""Shopping Cart and Multi-Vendor Fulfillment Partitioning API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.modules.cart.schemas import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartResponse,
    ApplyCouponRequest,
)
from app.modules.cart.service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_cart_identifiers(request: Request) -> tuple[Optional[str], Optional[str]]:
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    user_id = None
    if auth_header and "Bearer " in auth_header:
        try:
            token = auth_header.replace("Bearer ", "").strip()
            payload = decode_token(token)
            user_id = payload.get("sub")
        except Exception:
            pass
    session_id = request.headers.get("x-session-id") or request.cookies.get("cart_session_id") or "guest_default_session"
    return user_id, session_id


@router.get("", response_model=CartResponse)
async def get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current customer's cart grouped by vendor store partitions."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.get_cart(user_id=user_id, session_id=session_id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    payload: CartItemAddRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Adds a fixed or variable-weight product to the shopping cart."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.add_item(payload, user_id=user_id, session_id=session_id)


@router.patch("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: str,
    payload: CartItemUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Updates item quantity or special handling/cutting instructions."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.update_item(item_id, payload, user_id=user_id, session_id=session_id)


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
    item_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Removes a product line item from the shopping cart."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.remove_item(item_id, user_id=user_id, session_id=session_id)


@router.post("/clear", response_model=CartResponse)
async def clear_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Empties all items from the current cart."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.clear_cart(user_id=user_id, session_id=session_id)


@router.post("/apply-coupon", response_model=CartResponse)
async def apply_coupon(
    payload: ApplyCouponRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Applies a promotional discount coupon code to the active cart."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.apply_coupon(payload, user_id=user_id, session_id=session_id)


@router.delete("/remove-coupon", response_model=CartResponse)
async def remove_coupon(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Removes the applied promo code from the cart."""
    user_id, session_id = get_cart_identifiers(request)
    service = CartService(db)
    return await service.remove_coupon(user_id=user_id, session_id=session_id)
