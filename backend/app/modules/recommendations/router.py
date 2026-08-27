"""Smart Replenishment and AI Recommendation API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.authentication.permissions import get_current_user
from app.modules.users.models import User
from app.modules.cart.schemas import CartResponse
from app.modules.recommendations.schemas import (
    SmartGroceryPlanCreate,
    SmartGroceryPlanResponse,
    ReplenishmentAlertItem,
    FrequentlyBoughtTogetherResponse,
)
from app.modules.recommendations.service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Planner"])


@router.get("/replenishment-alerts", response_model=List[ReplenishmentAlertItem])
async def get_replenishment_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Personalized replenishment model predicting household pantry run-outs."""
    service = RecommendationService(db)
    return await service.get_replenishment_alerts(current_user.id)


@router.get("/frequently-bought-together/{product_id}", response_model=FrequentlyBoughtTogetherResponse)
async def get_frequently_bought_together(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI recommendations for items frequently purchased alongside the given product."""
    service = RecommendationService(db)
    return await service.get_frequently_bought_together(product_id)


@router.post("/smart-planner", response_model=SmartGroceryPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_smart_plan(
    payload: SmartGroceryPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a weekly household recurring grocery plan."""
    service = RecommendationService(db)
    return await service.create_smart_plan(current_user.id, payload)


@router.get("/smart-planner/{plan_id}", response_model=SmartGroceryPlanResponse)
async def get_smart_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves weekly smart replenishment plan details."""
    service = RecommendationService(db)
    return await service.get_smart_plan(plan_id, current_user.id)


@router.post("/smart-planner/{plan_id}/generate-cart", response_model=CartResponse)
async def generate_cart_from_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transfers the entire weekly smart plan into the active cart in one action."""
    service = RecommendationService(db)
    return await service.generate_cart_from_plan(plan_id, current_user.id)
