"""FEFO Inventory Management, Batch Allocation, and Warehouse API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.inventory.schemas import (
    WarehouseCreate,
    WarehouseResponse,
    InventoryBatchCreate,
    InventoryBatchResponse,
    FEFOAllocationRequest,
    FEFOAllocationResponse,
    StockReservationRequest,
    StockReservationResponse,
    StockReleaseRequest,
    InventoryAdjustRequest,
)
from app.modules.inventory.service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/warehouses", response_model=List[WarehouseResponse])
async def list_warehouses(
    db: AsyncSession = Depends(get_db),
):
    """Lists fulfillment centers, dark stores, and central warehouses."""
    service = InventoryService(db)
    return await service.list_warehouses()


@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to create a new warehouse or dark store."""
    service = InventoryService(db)
    return await service.create_warehouse(payload)


@router.get("/batches", response_model=List[InventoryBatchResponse])
async def list_batches(
    product_id: Optional[str] = Query(None),
    vendor_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lists inventory batches sorted by expiry date."""
    service = InventoryService(db)
    return await service.list_batches(product_id=product_id, vendor_id=vendor_id, status=status)


@router.post("/batches", response_model=InventoryBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: InventoryBatchCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_role(UserRole.VENDOR_OWNER.value, UserRole.VENDOR_STAFF.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Registers a new inventory lot with manufacture & expiry dates for FEFO fulfillment."""
    service = InventoryService(db)
    return await service.create_batch(payload)


@router.get("/fefo-preview/{product_id}", response_model=FEFOAllocationResponse)
async def preview_fefo_allocation(
    product_id: str,
    qty: float = Query(1.0, gt=0),
    vendor_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Previews which specific batches will be consumed first based on FEFO ordering."""
    service = InventoryService(db)
    return await service.preview_fefo_allocation(
        FEFOAllocationRequest(product_id=product_id, requested_qty=qty, vendor_id=vendor_id)
    )


@router.post("/reserve", response_model=StockReservationResponse)
async def reserve_stock(
    payload: StockReservationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Locks inventory across nearest-expiring batches with a TTL expiration during checkout."""
    service = InventoryService(db)
    return await service.reserve_stock(payload)


@router.post("/release")
async def release_stock(
    payload: StockReleaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """Unlocks and restores reserved stock for an abandoned cart or cancelled checkout."""
    service = InventoryService(db)
    return await service.release_stock(payload.reference_id)


@router.post("/adjust", response_model=InventoryBatchResponse)
async def adjust_stock(
    payload: InventoryAdjustRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_role(UserRole.VENDOR_OWNER.value, UserRole.VENDOR_STAFF.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Records stock damage, spoilage waste, or manual inventory cycle count adjustment."""
    service = InventoryService(db)
    return await service.adjust_stock(payload)
