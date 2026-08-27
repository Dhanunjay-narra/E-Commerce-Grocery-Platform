"""Pydantic schemas for category hierarchy management."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_featured: bool = False
    sort_order: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    level: int
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_featured: bool
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTreeResponse(CategoryResponse):
    subcategories: List["CategoryTreeResponse"] = []

    model_config = ConfigDict(from_attributes=True)


CategoryTreeResponse.model_rebuild()
