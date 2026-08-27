"""FEFO Inventory allocation engine, reservations, and stock management service."""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, InsufficientInventoryError, ValidationError
from app.core.redis import cache
from app.modules.inventory.models import InventoryBatch, Warehouse
from app.modules.inventory.schemas import (
    InventoryBatchCreate,
    InventoryBatchUpdate,
    InventoryBatchResponse,
    WarehouseCreate,
    WarehouseResponse,
    FEFOAllocationRequest,
    FEFOAllocationResponse,
    FEFOAllocationItem,
    StockReservationRequest,
    StockReservationResponse,
    InventoryAdjustRequest,
)
from app.modules.inventory.repository import InventoryRepository
from app.modules.products.repository import ProductRepository


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InventoryRepository(db)
        self.prod_repo = ProductRepository(db)

    async def create_warehouse(self, payload: WarehouseCreate) -> WarehouseResponse:
        wh = await self.repo.create_warehouse(payload)
        return WarehouseResponse.model_validate(wh)

    async def list_warehouses(self) -> List[WarehouseResponse]:
        warehouses = await self.repo.list_warehouses()
        return [WarehouseResponse.model_validate(w) for w in warehouses]

    async def create_batch(self, payload: InventoryBatchCreate) -> InventoryBatchResponse:
        product = await self.prod_repo.get_by_id(payload.product_id)
        if not product:
            raise EntityNotFoundError("Product associated with this inventory batch does not exist.")

        batch = await self.repo.create_batch(payload)
        return InventoryBatchResponse.model_validate(batch)

    async def list_batches(
        self, product_id: Optional[str] = None, vendor_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[InventoryBatchResponse]:
        batches = await self.repo.list_batches(product_id=product_id, vendor_id=vendor_id, status=status)
        return [InventoryBatchResponse.model_validate(b) for b in batches]

    async def preview_fefo_allocation(self, payload: FEFOAllocationRequest) -> FEFOAllocationResponse:
        """Preview FEFO batch allocation without mutating database state."""
        batches = await self.repo.get_fefo_batches_for_product(payload.product_id, payload.vendor_id)
        
        remaining_to_allocate = payload.requested_qty
        allocations: List[FEFOAllocationItem] = []

        for b in batches:
            if remaining_to_allocate <= 0:
                break

            alloc_qty = min(b.available_qty, remaining_to_allocate)
            allocations.append(
                FEFOAllocationItem(
                    batch_id=b.id,
                    batch_number=b.batch_number,
                    expiry_date=b.expiry_date,
                    allocated_qty=alloc_qty,
                    procurement_cost=b.procurement_cost,
                )
            )
            remaining_to_allocate -= alloc_qty

        total_allocated = round(payload.requested_qty - remaining_to_allocate, 2)
        is_fully_allocated = remaining_to_allocate <= 0

        return FEFOAllocationResponse(
            product_id=payload.product_id,
            requested_qty=payload.requested_qty,
            total_allocated_qty=total_allocated,
            is_fully_allocated=is_fully_allocated,
            allocations=allocations,
        )

    async def reserve_stock(self, payload: StockReservationRequest) -> StockReservationResponse:
        """FEFO Stock Reservation: Locks stock across nearest-expiring batches."""
        # Use distributed cache lock per product during reservation to prevent race conditions
        lock_key = f"stock_lock:{payload.product_id}"
        await cache.acquire_lock(lock_key, ttl_seconds=5)

        try:
            fefo_plan = await self.preview_fefo_allocation(
                FEFOAllocationRequest(
                    product_id=payload.product_id,
                    requested_qty=payload.quantity,
                    vendor_id=payload.vendor_id,
                )
            )

            if not fefo_plan.is_fully_allocated:
                raise InsufficientInventoryError(
                    f"Insufficient stock for product. Requested {payload.quantity}, only {fefo_plan.total_allocated_qty} available across non-expired batches."
                )

            # Apply reservations
            saved_allocations: List[FEFOAllocationItem] = []
            for alloc in fefo_plan.allocations:
                batch = await self.repo.get_batch_by_id(alloc.batch_id)
                if batch:
                    batch.available_qty -= alloc.allocated_qty
                    batch.reserved_qty += alloc.allocated_qty

                    await self.repo.create_reservation(
                        reference_id=payload.reference_id,
                        product_id=payload.product_id,
                        batch_id=batch.id,
                        qty=alloc.allocated_qty,
                        ttl_seconds=payload.ttl_seconds,
                    )
                    saved_allocations.append(alloc)

            from datetime import timedelta
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=payload.ttl_seconds)

            return StockReservationResponse(
                reference_id=payload.reference_id,
                product_id=payload.product_id,
                reserved_qty=payload.quantity,
                expires_at=expires_at,
                is_successful=True,
                reservations=saved_allocations,
            )
        finally:
            await cache.release_lock(lock_key)

    async def release_stock(self, reference_id: str) -> dict:
        """Releases all temporary reserved stock back to available pool for a cart/order."""
        released = await self.repo.release_reservations(reference_id)
        return {
            "success": True,
            "message": f"Released {len(released)} stock reservations for reference {reference_id}.",
        }

    async def commit_stock(self, reference_id: str) -> dict:
        """Permanently debits stock upon verified order payment."""
        committed = await self.repo.commit_reservations(reference_id)
        return {
            "success": True,
            "message": f"Successfully finalized stock sale for {len(committed)} reservations.",
        }

    async def adjust_stock(self, payload: InventoryAdjustRequest) -> InventoryBatchResponse:
        batch = await self.repo.get_batch_by_id(payload.batch_id)
        if not batch:
            raise EntityNotFoundError("Inventory batch not found.")

        if payload.quantity_delta < 0 and abs(payload.quantity_delta) > batch.available_qty:
            raise ValidationError("Cannot reduce more quantity than currently available in batch.")

        await self.repo.record_adjustment(batch, payload.quantity_delta, payload.reason, payload.reference_id)
        return InventoryBatchResponse.model_validate(batch)
