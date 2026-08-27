"""Verified review submission, moderation, and star rating recalculation service."""
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ValidationError
from app.modules.reviews.models import ProductReview
from app.modules.reviews.schemas import (
    ReviewCreate,
    ReviewResponse,
    ReviewModerateRequest,
    VendorReplyRequest,
)
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.users.models import User


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prod_repo = ProductRepository(db)

    async def list_for_product(self, product_id: str) -> List[ReviewResponse]:
        query = (
            select(ProductReview)
            .where(
                and_(
                    ProductReview.product_id == product_id,
                    ProductReview.status == "APPROVED",
                    ProductReview.is_deleted == False,
                )
            )
            .options(selectinload(ProductReview.user))
            .order_by(ProductReview.helpful_votes.desc(), ProductReview.created_at.desc())
        )
        res = await self.db.execute(query)
        reviews = list(res.scalars().all())

        return [
            ReviewResponse(
                id=r.id,
                product_id=r.product_id,
                user_id=r.user_id,
                user_name=r.user.full_name if r.user else "Verified Customer",
                rating=r.rating,
                title=r.title,
                comment=r.comment,
                is_verified_purchase=r.is_verified_purchase,
                status=r.status,
                helpful_votes=r.helpful_votes,
                vendor_reply=r.vendor_reply,
                created_at=r.created_at,
            )
            for r in reviews
        ]

    async def create_review(self, product_id: str, user: User, payload: ReviewCreate) -> ReviewResponse:
        product = await self.prod_repo.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product not found.")

        review = ProductReview(
            product_id=product_id,
            user_id=user.id,
            order_id=payload.order_id,
            rating=payload.rating,
            title=payload.title,
            comment=payload.comment,
            is_verified_purchase=bool(payload.order_id),
            status="APPROVED",
        )
        self.db.add(review)
        await self.db.flush()

        # Recalculate average rating on master product
        avg_query = select(func.avg(ProductReview.rating), func.count(ProductReview.id)).where(
            and_(ProductReview.product_id == product_id, ProductReview.status == "APPROVED")
        )
        avg_res = await self.db.execute(avg_query)
        avg_rating, count = avg_res.one()

        product.rating_average = round(float(avg_rating or 0.0), 2)
        product.rating_count = int(count or 0)
        await self.db.flush()

        return ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            user_name=user.full_name,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            is_verified_purchase=review.is_verified_purchase,
            status=review.status,
            helpful_votes=0,
            vendor_reply=None,
            created_at=review.created_at,
        )

    async def vote_helpful(self, review_id: str) -> dict:
        query = select(ProductReview).where(ProductReview.id == review_id)
        res = await self.db.execute(query)
        review = res.scalar_one_or_none()
        if not review:
            raise EntityNotFoundError("Review not found.")

        review.helpful_votes += 1
        await self.db.flush()
        return {"success": True, "helpful_votes": review.helpful_votes}

    async def add_vendor_reply(self, review_id: str, payload: VendorReplyRequest) -> dict:
        query = select(ProductReview).where(ProductReview.id == review_id)
        res = await self.db.execute(query)
        review = res.scalar_one_or_none()
        if not review:
            raise EntityNotFoundError("Review not found.")

        review.vendor_reply = payload.reply
        await self.db.flush()
        return {"success": True, "message": "Vendor reply posted."}
