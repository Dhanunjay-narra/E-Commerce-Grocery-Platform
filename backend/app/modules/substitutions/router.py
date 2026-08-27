"""Smart Product Substitution endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.substitutions.schemas import (
    SubstitutionSuggestResponse,
    SubstitutionRuleCreate,
    SubstitutionRuleResponse,
)
from app.modules.substitutions.service import SubstitutionService

router = APIRouter(prefix="/substitutions", tags=["Substitutions"])


@router.get("/suggest/{product_id}", response_model=SubstitutionSuggestResponse)
async def suggest_substitutes(
    product_id: str,
    vendor_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Algorithmic recommendation of in-stock substitute grocery products."""
    service = SubstitutionService(db)
    return await service.suggest_substitutes(product_id, vendor_id=vendor_id)


@router.post("/rules", response_model=SubstitutionRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_substitution_rule(
    payload: SubstitutionRuleCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to create explicit product substitute mappings."""
    service = SubstitutionService(db)
    return await service.create_rule(payload)
