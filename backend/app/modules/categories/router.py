"""Category endpoints for hierarchical catalog navigation."""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
)
from app.modules.categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """Lists all active categories in flat list representation."""
    service = CategoryService(db)
    return await service.list_all()


@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
):
    """Returns full 3-tier category hierarchy (Department -> Category -> Subcategory)."""
    service = CategoryService(db)
    return await service.get_tree()


@router.get("/featured", response_model=List[CategoryResponse])
async def list_featured_categories(
    db: AsyncSession = Depends(get_db),
):
    """Returns prominent featured categories for homepage carousel."""
    service = CategoryService(db)
    return await service.list_featured()


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves single category metadata by URL slug."""
    service = CategoryService(db)
    return await service.get_by_slug(slug)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves category metadata by UUID."""
    service = CategoryService(db)
    return await service.get_by_id(category_id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to create a new category in the hierarchy."""
    service = CategoryService(db)
    return await service.create(payload)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to update category details or reposition hierarchy."""
    service = CategoryService(db)
    return await service.update(category_id, payload)


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to soft-delete a category."""
    service = CategoryService(db)
    await service.delete(category_id)
    return {"success": True, "message": "Category deleted successfully."}
