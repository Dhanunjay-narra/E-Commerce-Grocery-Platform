"""Shipping and Delivery Slot database repository layer."""
from datetime import datetime, timezone, date, timedelta
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.shipping.models import DeliveryZone, DeliverySlot, Shipment
from app.modules.shipping.schemas import DeliveryZoneCreate, DeliverySlotCreate


class ShippingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_zone(self, payload: DeliveryZoneCreate) -> DeliveryZone:
        zone = DeliveryZone(
            name=payload.name,
            code=payload.code.upper().strip(),
            city=payload.city,
            state=payload.state,
            center_latitude=payload.center_latitude,
            center_longitude=payload.center_longitude,
            radius_km=payload.radius_km,
            base_fee=payload.base_fee,
        )
        self.db.add(zone)
        await self.db.flush()
        return zone

    async def list_zones(self) -> List[DeliveryZone]:
        query = select(DeliveryZone).where(and_(DeliveryZone.is_active == True, DeliveryZone.is_deleted == False))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_zone_by_id(self, zone_id: str) -> Optional[DeliveryZone]:
        query = select(DeliveryZone).where(and_(DeliveryZone.id == zone_id, DeliveryZone.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_slot(self, payload: DeliverySlotCreate) -> DeliverySlot:
        slot = DeliverySlot(
            zone_id=payload.zone_id,
            slot_date=payload.slot_date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            slot_type=payload.slot_type,
            max_capacity=payload.max_capacity,
            current_bookings=0,
        )
        self.db.add(slot)
        await self.db.flush()
        return slot

    async def get_slot_by_id(self, slot_id: str) -> Optional[DeliverySlot]:
        query = select(DeliverySlot).where(DeliverySlot.id == slot_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_available_slots(self, zone_id: str, target_date: date) -> List[DeliverySlot]:
        query = select(DeliverySlot).where(
            and_(
                DeliverySlot.zone_id == zone_id,
                DeliverySlot.slot_date == target_date,
                DeliverySlot.is_active == True,
            )
        ).order_by(DeliverySlot.start_time.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def increment_slot_booking(self, slot: DeliverySlot) -> None:
        slot.current_bookings += 1
        await self.db.flush()

    async def decrement_slot_booking(self, slot: DeliverySlot) -> None:
        slot.current_bookings = max(0, slot.current_bookings - 1)
        await self.db.flush()

    async def create_shipment(
        self, order_id: str, zone_id: str, slot_id: Optional[str], delivery_otp: str, vendor_id: Optional[str] = None
    ) -> Shipment:
        import uuid
        tracking_num = f"TRK-{uuid.uuid4().hex[:10].upper()}"
        shipment = Shipment(
            order_id=order_id,
            vendor_id=vendor_id,
            zone_id=zone_id,
            slot_id=slot_id,
            tracking_number=tracking_num,
            status="PENDING",
            delivery_otp=delivery_otp,
        )
        self.db.add(shipment)
        await self.db.flush()
        return shipment

    async def get_shipment_by_order_id(self, order_id: str) -> Optional[Shipment]:
        query = select(Shipment).where(Shipment.order_id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_shipment_by_id(self, shipment_id: str) -> Optional[Shipment]:
        query = select(Shipment).where(Shipment.id == shipment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
