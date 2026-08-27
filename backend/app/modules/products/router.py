"""Master Product Catalog API endpoints."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductDetailResponse,
    VariableWeightPricingCalcRequest,
    VariableWeightPricingCalcResponse,
)
from app.modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
async def list_products(
    category_id: Optional[str] = Query(None, description="Filter by Category ID"),
    brand: Optional[str] = Query(None, description="Filter by Brand name"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    is_organic: Optional[bool] = Query(None),
    is_vegan: Optional[bool] = Query(None),
    is_vegetarian: Optional[bool] = Query(None),
    is_gluten_free: Optional[bool] = Query(None),
    status: Optional[str] = Query("ACTIVE"),
    sort_by: Optional[str] = Query("newest", description="newest, price_low, price_high, rating"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lists products with faceted filters for dietary tags, categories, price range, and sorting."""
    service = ProductService(db)
    return await service.list_products(
        category_id=category_id,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        is_organic=is_organic,
        is_vegan=is_vegan,
        is_vegetarian=is_vegetarian,
        is_gluten_free=is_gluten_free,
        status=status,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )


@router.get("/barcode/{barcode}", response_model=ProductDetailResponse)
async def get_product_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_db),
):
    """Rapid barcode scanning lookup for in-store/warehouse pickers or shoppers."""
    service = ProductService(db)
    return await service.get_by_barcode(barcode)


@router.get("/{id_or_slug}", response_model=ProductDetailResponse)
async def get_product_detail(
    id_or_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full product specifications, nutritional tags, images, and variants."""
    service = ProductService(db)
    return await service.get_by_id_or_slug(id_or_slug)


@router.post("", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.VENDOR_OWNER.value)),
):
    """Creates a new master product catalog entry."""
    service = ProductService(db)
    return await service.create(payload)


@router.patch("/{product_id}", response_model=ProductDetailResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.VENDOR_OWNER.value)),
):
    """Updates master product specifications or prices."""
    service = ProductService(db)
    return await service.update(product_id, payload)


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Soft-deletes a product from the active catalog."""
    service = ProductService(db)
    await service.delete(product_id)
    return {"success": True, "message": "Product removed successfully."}


@router.post("/{product_id}/calc-variable-price", response_model=VariableWeightPricingCalcResponse)
async def calculate_variable_weight_price(
    product_id: str,
    payload: VariableWeightPricingCalcRequest,
    db: AsyncSession = Depends(get_db),
):
    """Simulates or calculates variable weight price reconciliation for picked produce/meat."""
    service = ProductService(db)
    return await service.calculate_variable_weight_pricing(product_id, payload)
