"""Shipping and Intelligent Delivery Slot scheduling service."""
from datetime import datetime, timezone, date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, DeliverySlotUnavailableError, ValidationError
from app.modules.shipping.models import DeliveryZone, DeliverySlot, Shipment
from app.modules.shipping.schemas import (
    DeliveryZoneCreate,
    DeliveryZoneResponse,
    DeliverySlotCreate,
    DeliverySlotResponse,
    ShipmentResponse,
    DeliveryOTPVerifyRequest,
)
from app.modules.shipping.repository import ShippingRepository


class ShippingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShippingRepository(db)

    async def list_zones(self) -> List[DeliveryZoneResponse]:
        zones = await self.repo.list_zones()
        return [DeliveryZoneResponse.model_validate(z) for z in zones]

    async def create_zone(self, payload: DeliveryZoneCreate) -> DeliveryZoneResponse:
        zone = await self.repo.create_zone(payload)
        return DeliveryZoneResponse.model_validate(zone)

    async def get_or_generate_slots(self, zone_id: str, target_date: date) -> List[DeliverySlotResponse]:
        """Delivery Slot Engine: auto-populates daily standard windows (08-10, 10-12, 12-14, 14-16, 16-18, 18-20, 20-22)."""
        slots = await self.repo.list_available_slots(zone_id, target_date)
        if not slots:
            windows = [
                ("08:00", "10:00", "STANDARD_2HOUR", 30),
                ("10:00", "12:00", "STANDARD_2HOUR", 30),
                ("12:00", "14:00", "STANDARD_2HOUR", 25),
                ("14:00", "16:00", "STANDARD_2HOUR", 25),
                ("16:00", "18:00", "STANDARD_2HOUR", 35),
                ("18:00", "20:00", "STANDARD_2HOUR", 40),
                ("20:00", "22:00", "STANDARD_2HOUR", 30),
            ]
            for start, end, stype, cap in windows:
                await self.repo.create_slot(
                    DeliverySlotCreate(
                        zone_id=zone_id,
                        slot_date=target_date,
                        start_time=start,
                        end_time=end,
                        slot_type=stype,
                        max_capacity=cap,
                    )
                )
            slots = await self.repo.list_available_slots(zone_id, target_date)

        return [
            DeliverySlotResponse(
                id=s.id,
                zone_id=s.zone_id,
                slot_date=s.slot_date,
                start_time=s.start_time,
                end_time=s.end_time,
                slot_type=s.slot_type,
                max_capacity=s.max_capacity,
                current_bookings=s.current_bookings,
                is_available=(s.current_bookings < s.max_capacity),
            )
            for s in slots
        ]

    async def book_slot(self, slot_id: str) -> DeliverySlot:
        slot = await self.repo.get_slot_by_id(slot_id)
        if not slot:
            raise EntityNotFoundError("Delivery slot not found.")

        if slot.current_bookings >= slot.max_capacity:
            raise DeliverySlotUnavailableError("The selected delivery slot is at maximum capacity.")

        await self.repo.increment_slot_booking(slot)
        return slot

    async def verify_delivery_otp(self, shipment_id: str, otp_code: str) -> ShipmentResponse:
        shipment = await self.repo.get_shipment_by_id(shipment_id)
        if not shipment:
            raise EntityNotFoundError("Shipment not found.")

        if shipment.delivery_otp != otp_code.strip():
            raise ValidationError("Invalid delivery verification OTP. Proof-of-delivery failed.")

        shipment.status = "DELIVERED"
        shipment.delivered_at = datetime.now(timezone.utc)
        await self.db.flush()

        return ShipmentResponse.model_validate(shipment)
