"""Pydantic schemas for wishlist management and price-drop alerts."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class WishlistCreate(BaseModel):
    name: str = Field(default="My Grocery List", min_length=2, max_length=100)
    is_shared_with_household: bool = False
    is_public: bool = False


class WishlistItemAdd(BaseModel):
    product_id: str
    desired_qty: float = Field(default=1.0, gt=0)


class WishlistItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    brand: str
    unit: str
    current_price: float
    added_price: float
    price_dropped: bool
    price_drop_amount: float
    desired_qty: float
    image_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishlistResponse(BaseModel):
    id: str
    user_id: str
    name: str
    is_shared_with_household: bool
    is_public: bool
    items: List[WishlistItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MoveToCartResponse(BaseModel):
    success: bool
    items_moved_count: int
    message: str
