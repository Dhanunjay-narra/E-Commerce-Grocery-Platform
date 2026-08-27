"""Verified Product Reviews and Rating API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import get_current_user, require_role
from app.modules.users.models import User
from app.modules.reviews.schemas import (
    ReviewCreate,
    ReviewResponse,
    VendorReplyRequest,
)
from app.modules.reviews.service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def list_product_reviews(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Lists verified customer reviews for a grocery product."""
    service = ReviewService(db)
    return await service.list_for_product(product_id)


@router.post("/product/{product_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def post_product_review(
    product_id: str,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submits a verified buyer review and triggers product rating re-computation."""
    service = ReviewService(db)
    return await service.create_review(product_id, current_user, payload)


@router.post("/{review_id}/vote-helpful")
async def vote_review_helpful(
    review_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Increments helpful upvote count for a review."""
    service = ReviewService(db)
    return await service.vote_helpful(review_id)


@router.post("/{review_id}/vendor-reply")
async def add_vendor_reply(
    review_id: str,
    payload: VendorReplyRequest,
    _vendor=Depends(require_role(UserRole.VENDOR_OWNER.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
    db: AsyncSession = Depends(get_db),
):
    """Merchant response to a customer review."""
    service = ReviewService(db)
    return await service.add_vendor_reply(review_id, payload)
