"""Pydantic schemas for smart grocery planner, replenishment cadence, and recommendations."""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.modules.products.schemas import ProductResponse


class SmartPlanItemCreate(BaseModel):
    product_id: str
    quantity: float = Field(default=1.0, gt=0)
    aisle_category: str = "Pantry"


class SmartPlanItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: float
    aisle_category: str
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SmartGroceryPlanCreate(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=100)
    frequency_days: int = Field(default=7, ge=1, le=60)
    is_recurring_auto_order: bool = False
    next_replenishment_date: date
    items: List[SmartPlanItemCreate] = []


class SmartGroceryPlanResponse(BaseModel):
    id: str
    user_id: str
    plan_name: str
    frequency_days: int
    is_recurring_auto_order: bool
    next_replenishment_date: date
    is_active: bool
    items: List[SmartPlanItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReplenishmentAlertItem(BaseModel):
    product: ProductResponse
    average_interval_days: float
    last_purchased_at: datetime
    predicted_runout_date: date
    confidence_score: float
    days_until_runout: int
    is_urgent: bool  # True if <= 1 day


class FrequentlyBoughtTogetherResponse(BaseModel):
    primary_product_id: str
    recommended_products: List[ProductResponse] = []
