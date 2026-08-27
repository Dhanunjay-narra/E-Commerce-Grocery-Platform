"""Coupon database repository layer."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.coupons.models import Coupon, CouponRedemption
from app.modules.coupons.schemas import CouponCreate, CouponUpdate


class CouponRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, code: str) -> Optional[Coupon]:
        query = select(Coupon).where(
            and_(Coupon.code == code.upper().strip(), Coupon.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, coupon_id: str) -> Optional[Coupon]:
        query = select(Coupon).where(and_(Coupon.id == coupon_id, Coupon.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_active(self) -> List[Coupon]:
        now = datetime.now(timezone.utc)
        query = (
            select(Coupon)
            .where(
                and_(
                    Coupon.is_active == True,
                    Coupon.is_deleted == False,
                    Coupon.starts_at <= now,
                    Coupon.expires_at > now,
                )
            )
            .order_by(Coupon.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_redemption_count(self, coupon_id: str, user_id: str) -> int:
        query = select(func.count(CouponRedemption.id)).where(
            and_(CouponRedemption.coupon_id == coupon_id, CouponRedemption.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, payload: CouponCreate) -> Coupon:
        coupon = Coupon(
            code=payload.code.upper().strip(),
            description=payload.description,
            discount_type=payload.discount_type.upper(),
            discount_value=payload.discount_value,
            min_order_value=payload.min_order_value,
            max_discount_cap=payload.max_discount_cap,
            applicable_category_id=payload.applicable_category_id,
            applicable_vendor_id=payload.applicable_vendor_id,
            is_first_order_only=payload.is_first_order_only,
            usage_limit_per_user=payload.usage_limit_per_user,
            total_usage_limit=payload.total_usage_limit,
            expires_at=payload.expires_at,
        )
        self.db.add(coupon)
        await self.db.flush()
        return coupon

    async def record_redemption(
        self, coupon: Coupon, user_id: str, discount_amount: float, order_id: Optional[str] = None
    ) -> CouponRedemption:
        coupon.total_redemptions += 1
        redemption = CouponRedemption(
            coupon_id=coupon.id,
            user_id=user_id,
            order_id=order_id,
            discount_amount=discount_amount,
        )
        self.db.add(redemption)
        await self.db.flush()
        return redemption
