"""Coupon discount calculation and validation service."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError, ValidationError
from app.modules.coupons.models import Coupon
from app.modules.coupons.schemas import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
)
from app.modules.coupons.repository import CouponRepository


class CouponService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CouponRepository(db)

    async def list_active(self) -> List[CouponResponse]:
        coupons = await self.repo.list_active()
        return [CouponResponse.model_validate(c) for c in coupons]

    async def create(self, payload: CouponCreate) -> CouponResponse:
        existing = await self.repo.get_by_code(payload.code)
        if existing:
            raise ConflictError(f"A coupon with code '{payload.code}' already exists.")

        coupon = await self.repo.create(payload)
        return CouponResponse.model_validate(coupon)

    async def validate_and_calculate_discount(
        self, payload: CouponValidateRequest, user_id: Optional[str] = None, is_first_order: bool = False
    ) -> CouponValidateResponse:
        coupon = await self.repo.get_by_code(payload.code)
        if not coupon or not coupon.is_active or coupon.is_deleted:
            return CouponValidateResponse(
                is_valid=False,
                code=payload.code,
                discount_amount=0.0,
                final_amount=payload.order_amount,
                message="Invalid or expired coupon code.",
            )

        now = datetime.now(timezone.utc)
        exp_dt = coupon.expires_at if coupon.expires_at.tzinfo else coupon.expires_at.replace(tzinfo=timezone.utc)
        starts_dt = coupon.starts_at if coupon.starts_at.tzinfo else coupon.starts_at.replace(tzinfo=timezone.utc)

        if exp_dt < now or starts_dt > now:
            return CouponValidateResponse(
                is_valid=False,
                code=payload.code,
                discount_amount=0.0,
                final_amount=payload.order_amount,
                message="This coupon has expired.",
            )

        if payload.order_amount < coupon.min_order_value:
            return CouponValidateResponse(
                is_valid=False,
                code=payload.code,
                discount_amount=0.0,
                final_amount=payload.order_amount,
                message=f"Minimum order value for this coupon is ₹{coupon.min_order_value:.2f}.",
            )

        if coupon.is_first_order_only and not is_first_order and user_id:
            return CouponValidateResponse(
                is_valid=False,
                code=payload.code,
                discount_amount=0.0,
                final_amount=payload.order_amount,
                message="This coupon is valid only for your first order.",
            )

        if coupon.total_usage_limit and coupon.total_redemptions >= coupon.total_usage_limit:
            return CouponValidateResponse(
                is_valid=False,
                code=payload.code,
                discount_amount=0.0,
                final_amount=payload.order_amount,
                message="This coupon has reached its maximum total redemptions.",
            )

        if user_id:
            user_count = await self.repo.get_user_redemption_count(coupon.id, user_id)
            if user_count >= coupon.usage_limit_per_user:
                return CouponValidateResponse(
                    is_valid=False,
                    code=payload.code,
                    discount_amount=0.0,
                    final_amount=payload.order_amount,
                    message="You have reached the maximum allowed redemptions for this coupon.",
                )

        # Calculate discount
        if coupon.discount_type == "PERCENTAGE":
            discount = payload.order_amount * (coupon.discount_value / 100.0)
            if coupon.max_discount_cap:
                discount = min(discount, coupon.max_discount_cap)
        else:  # FIXED_AMOUNT
            discount = min(coupon.discount_value, payload.order_amount)

        discount = round(discount, 2)
        final_amt = round(max(0.0, payload.order_amount - discount), 2)

        return CouponValidateResponse(
            is_valid=True,
            coupon_id=coupon.id,
            code=coupon.code,
            discount_amount=discount,
            final_amount=final_amt,
            message=f"Coupon applied! You saved ₹{discount:.2f}.",
        )
