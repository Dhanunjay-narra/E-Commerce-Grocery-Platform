"""FEFO Inventory database repository layer."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.inventory.models import Warehouse, InventoryBatch, StockReservation, InventoryTransaction
from app.modules.inventory.schemas import InventoryBatchCreate, InventoryBatchUpdate, WarehouseCreate
from app.modules.products.models import Product


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_warehouse(self, payload: WarehouseCreate) -> Warehouse:
        wh = Warehouse(
            name=payload.name,
            code=payload.code.upper().strip(),
            type=payload.type,
            address=payload.address,
            city=payload.city,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        self.db.add(wh)
        await self.db.flush()
        return wh

    async def list_warehouses(self) -> List[Warehouse]:
        query = select(Warehouse).where(and_(Warehouse.is_active == True, Warehouse.is_deleted == False))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_batch(self, payload: InventoryBatchCreate) -> InventoryBatch:
        batch = InventoryBatch(
            batch_number=payload.batch_number.strip(),
            product_id=payload.product_id,
            vendor_id=payload.vendor_id,
            warehouse_id=payload.warehouse_id,
            manufacturing_date=payload.manufacturing_date,
            expiry_date=payload.expiry_date,
            procurement_cost=payload.procurement_cost,
            initial_qty=payload.initial_qty,
            available_qty=payload.initial_qty,
            reserved_qty=0.0,
            damaged_qty=0.0,
            status="ACTIVE",
        )
        self.db.add(batch)
        await self.db.flush()

        # Record initial receipt transaction
        txn = InventoryTransaction(
            product_id=batch.product_id,
            batch_id=batch.id,
            transaction_type="RECEIPT",
            quantity=batch.initial_qty,
            reason="Initial Batch Receipt",
        )
        self.db.add(txn)
        await self.db.flush()
        return batch

    async def get_batch_by_id(self, batch_id: str) -> Optional[InventoryBatch]:
        query = select(InventoryBatch).where(and_(InventoryBatch.id == batch_id, InventoryBatch.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_batches(
        self, product_id: Optional[str] = None, vendor_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[InventoryBatch]:
        conditions = [InventoryBatch.is_deleted == False]
        if product_id:
            conditions.append(InventoryBatch.product_id == product_id)
        if vendor_id:
            conditions.append(InventoryBatch.vendor_id == vendor_id)
        if status:
            conditions.append(InventoryBatch.status == status)

        query = select(InventoryBatch).where(and_(*conditions)).order_by(InventoryBatch.expiry_date.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_fefo_batches_for_product(
        self, product_id: str, vendor_id: Optional[str] = None
    ) -> List[InventoryBatch]:
        """Returns non-expired, available batches strictly ordered by expiry_date ASC (FEFO)."""
        now = datetime.now(timezone.utc)
        conditions = [
            InventoryBatch.product_id == product_id,
            InventoryBatch.is_deleted == False,
            InventoryBatch.status == "ACTIVE",
            InventoryBatch.available_qty > 0,
            InventoryBatch.expiry_date > now,
        ]
        if vendor_id:
            conditions.append(InventoryBatch.vendor_id == vendor_id)

        query = select(InventoryBatch).where(and_(*conditions)).order_by(InventoryBatch.expiry_date.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_reservation(
        self, reference_id: str, product_id: str, batch_id: str, qty: float, ttl_seconds: int = 600
    ) -> StockReservation:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        reservation = StockReservation(
            reference_id=reference_id,
            product_id=product_id,
            batch_id=batch_id,
            reserved_qty=qty,
            expires_at=expires_at,
        )
        self.db.add(reservation)
        await self.db.flush()
        return reservation

    async def get_active_reservations_for_ref(self, reference_id: str) -> List[StockReservation]:
        query = select(StockReservation).where(
            and_(
                StockReservation.reference_id == reference_id,
                StockReservation.is_released == False,
                StockReservation.is_committed == False,
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def release_reservations(self, reference_id: str) -> List[StockReservation]:
        reservations = await self.get_active_reservations_for_ref(reference_id)
        for res in reservations:
            res.is_released = True
            batch = await self.get_batch_by_id(res.batch_id)
            if batch:
                batch.available_qty += res.reserved_qty
                batch.reserved_qty = max(0.0, batch.reserved_qty - res.reserved_qty)

                txn = InventoryTransaction(
                    product_id=res.product_id,
                    batch_id=res.batch_id,
                    transaction_type="RELEASE",
                    quantity=res.reserved_qty,
                    reason=f"Reservation timeout/release for ref {reference_id}",
                    reference_id=reference_id,
                )
                self.db.add(txn)
        await self.db.flush()
        return reservations

    async def commit_reservations(self, reference_id: str) -> List[StockReservation]:
        reservations = await self.get_active_reservations_for_ref(reference_id)
        for res in reservations:
            res.is_committed = True
            batch = await self.get_batch_by_id(res.batch_id)
            if batch:
                batch.reserved_qty = max(0.0, batch.reserved_qty - res.reserved_qty)
                if batch.available_qty <= 0 and batch.reserved_qty <= 0:
                    batch.status = "DEPLETED"

                txn = InventoryTransaction(
                    product_id=res.product_id,
                    batch_id=res.batch_id,
                    transaction_type="SALE",
                    quantity=-res.reserved_qty,
                    reason=f"Sale committed for ref {reference_id}",
                    reference_id=reference_id,
                )
                self.db.add(txn)
        await self.db.flush()
        return reservations

    async def record_adjustment(
        self, batch: InventoryBatch, delta: float, reason: str, reference_id: Optional[str] = None
    ) -> None:
        batch.available_qty += delta
        if delta < 0 and reason in ["DAMAGE", "EXPIRED_WASTE"]:
            batch.damaged_qty += abs(delta)

        if batch.available_qty <= 0:
            batch.status = "DEPLETED"

        txn = InventoryTransaction(
            product_id=batch.product_id,
            batch_id=batch.id,
            transaction_type=reason,
            quantity=delta,
            reason=f"Manual/System adjustment: {reason}",
            reference_id=reference_id,
        )
        self.db.add(txn)
        await self.db.flush()
