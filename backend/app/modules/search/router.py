"""Search and Grocery Autocomplete discovery endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.search.schemas import (
    SearchResponse,
    SearchSuggestion,
    PopularSearch,
)
from app.modules.search.service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
async def search_products(
    q: str = Query("", description="Full-text search query (e.g. 'organic milk for kids')"),
    category_id: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    is_organic: Optional[bool] = Query(None),
    is_vegan: Optional[bool] = Query(None),
    is_gluten_free: Optional[bool] = Query(None),
    is_variable_weight: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Executes typo-tolerant full-text grocery search with dynamic facet extraction and intent classification."""
    service = SearchService(db)
    return await service.search(
        query=q,
        category_id=category_id,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        is_organic=is_organic,
        is_vegan=is_vegan,
        is_gluten_free=is_gluten_free,
        is_variable_weight=is_variable_weight,
        skip=skip,
        limit=limit,
    )


@router.get("/suggestions", response_model=List[SearchSuggestion])
async def get_autocomplete_suggestions(
    q: str = Query(..., min_length=2, description="Prefix characters typed so far"),
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Rapid keystroke autocomplete suggestions across products, categories, and brands."""
    service = SearchService(db)
    return await service.get_suggestions(prefix=q, limit=limit)


@router.get("/popular", response_model=List[PopularSearch])
async def get_popular_searches(
    db: AsyncSession = Depends(get_db),
):
    """Trending search queries across the grocery marketplace."""
    service = SearchService(db)
    return await service.get_popular_searches()
