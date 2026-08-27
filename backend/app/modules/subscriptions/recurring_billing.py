"""Household Grocery Recurring Cadence and Subscription Billing Scheduler."""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta, timezone
from pydantic import BaseModel, Field

class CadenceType(str, Enum):
    DAILY = "DAILY"                 # Fresh milk, bread, coriander, eggs
    ALTERNATE_DAYS = "ALTERNATE_DAYS"
    WEEKLY = "WEEKLY"               # Vegetables, fruits, paneer
    BI_WEEKLY = "BI_WEEKLY"         # Snacks, beverages
    MONTHLY = "MONTHLY"             # Rice, Atta, Cooking oils, Ghee, Cleaning

class SubscriptionItem(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    unit: str
    unit_price: float

class GrocerySubscription(BaseModel):
    id: str
    user_id: str
    household_id: Optional[str] = None
    items: List[SubscriptionItem]
    cadence: CadenceType
    preferred_slot_time: str = "07:00-09:00"
    is_paused: bool = False
    pause_until: Optional[date] = None
    next_delivery_date: date
    auto_pay_enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SubscriptionSchedulerEngine:
    """Computes next recurring delivery triggers and handles skip/pause workflows."""

    @staticmethod
    def calculate_next_date(current_date: date, cadence: CadenceType) -> date:
        if cadence == CadenceType.DAILY:
            return current_date + timedelta(days=1)
        elif cadence == CadenceType.ALTERNATE_DAYS:
            return current_date + timedelta(days=2)
        elif cadence == CadenceType.WEEKLY:
            return current_date + timedelta(days=7)
        elif cadence == CadenceType.BI_WEEKLY:
            return current_date + timedelta(days=14)
        elif cadence == CadenceType.MONTHLY:
            # Approximate 30-day month cadence
            return current_date + timedelta(days=30)
        return current_date + timedelta(days=7)

    @classmethod
    def generate_scheduled_orders(cls, subscriptions: List[GrocerySubscription], target_date: date) -> List[Dict[str, Any]]:
        orders_to_create = []
        
        for sub in subscriptions:
            if sub.is_paused:
                if sub.pause_until and target_date >= sub.pause_until:
                    sub.is_paused = False
                    sub.pause_until = None
                else:
                    continue
                    
            if sub.next_delivery_date == target_date:
                total_amt = sum(item.quantity * item.unit_price for item in sub.items)
                orders_to_create.append({
                    "subscription_id": sub.id,
                    "user_id": sub.user_id,
                    "household_id": sub.household_id,
                    "scheduled_date": str(target_date),
                    "delivery_slot": sub.preferred_slot_time,
                    "order_type": "SUBSCRIPTION_RECURRING",
                    "total_amount": round(total_amt, 2),
                    "items": [item.dict() for item in sub.items],
                })
                
        return orders_to_create
