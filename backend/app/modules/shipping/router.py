"""Delivery Zones, Slot Selection, and Proof-of-Delivery API endpoints."""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.shipping.schemas import (
    DeliveryZoneCreate,
    DeliveryZoneResponse,
    DeliverySlotResponse,
    ShipmentResponse,
    DeliveryOTPVerifyRequest,
)
from app.modules.shipping.service import ShippingService

router = APIRouter(prefix="/shipping", tags=["Shipping"])


@router.get("/zones", response_model=List[DeliveryZoneResponse])
async def list_delivery_zones(
    db: AsyncSession = Depends(get_db),
):
    """Lists all active delivery zones and coverage areas."""
    service = ShippingService(db)
    return await service.list_zones()


@router.post("/zones", response_model=DeliveryZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_zone(
    payload: DeliveryZoneCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to create a delivery geo-zone."""
    service = ShippingService(db)
    return await service.create_zone(payload)


@router.get("/slots/available", response_model=List[DeliverySlotResponse])
async def get_available_slots(
    zone_id: str = Query(...),
    slot_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves real-time slot availability for checkout delivery selection."""
    target_d = slot_date or date.today()
    service = ShippingService(db)
    return await service.get_or_generate_slots(zone_id, target_d)


@router.post("/shipments/{shipment_id}/verify-pod", response_model=ShipmentResponse)
async def verify_proof_of_delivery(
    shipment_id: str,
    payload: DeliveryOTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verifies customer 4-digit OTP at doorstep to finalize delivery."""
    service = ShippingService(db)
    return await service.verify_delivery_otp(shipment_id, payload.otp)
