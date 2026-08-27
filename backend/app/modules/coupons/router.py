"""Coupon and Discount Promotion API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import get_current_user, require_role
from app.modules.users.models import User
from app.modules.coupons.schemas import (
    CouponCreate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
)
from app.modules.coupons.service import CouponService

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.get("", response_model=List[CouponResponse])
async def list_active_coupons(
    db: AsyncSession = Depends(get_db),
):
    """Lists currently active promo codes and discount deals."""
    service = CouponService(db)
    return await service.list_active()


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    payload: CouponCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to create a new promotional coupon code."""
    service = CouponService(db)
    return await service.create(payload)


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    payload: CouponValidateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Checks coupon code validity and computes exact discounted order total."""
    service = CouponService(db)
    return await service.validate_and_calculate_discount(payload, user_id=current_user.id)
