"""Pydantic schemas for verified customer reviews and ratings."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="1 to 5 stars")
    title: str = Field(..., min_length=2, max_length=150)
    comment: str = Field(..., min_length=5)
    order_id: Optional[str] = None


class ReviewModerateRequest(BaseModel):
    status: str = Field(..., description="APPROVED, REJECTED")


class VendorReplyRequest(BaseModel):
    reply: str = Field(..., min_length=2)


class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    title: str
    comment: str
    is_verified_purchase: bool
    status: str
    helpful_votes: int
    vendor_reply: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
