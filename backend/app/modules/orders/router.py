"""Order Lifecycle Management, Checkout, Picking Station, and Invoice API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import get_current_user, require_role
from app.modules.users.models import User
from app.modules.orders.schemas import (
    OrderCheckoutRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderItemPickRequest,
    OrderStateTransitionRequest,
    OrderCancelRequest,
    InvoiceResponse,
)
from app.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderResponse])
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists order history for the authenticated customer."""
    service = OrderService(db)
    return await service.list_user_orders(current_user.id)


@router.post("/checkout", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
async def checkout_order(
    payload: OrderCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes customer checkout: locks FEFO stock, books slot, creates shipment, and initiates payment."""
    service = OrderService(db)
    return await service.checkout(current_user.id, payload)


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order_tracking(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full order fulfillment timeline, shipment tracking, and line items."""
    service = OrderService(db)
    return await service.get_by_id(order_id)


@router.post("/{order_id}/pick-item", response_model=OrderDetailResponse)
async def record_item_picking(
    order_id: str,
    payload: OrderItemPickRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fulfillment packing station: logs actual scale weight measured by picker."""
    service = OrderService(db)
    return await service.pick_item(order_id, payload, actor_id=current_user.id)


@router.post("/{order_id}/transition-status", response_model=OrderDetailResponse)
async def transition_order_status(
    order_id: str,
    payload: OrderStateTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Advances order status through the finite state machine (e.g. PROCESSING -> PICKING -> PACKED)."""
    service = OrderService(db)
    return await service.transition_order_status(order_id, payload, actor_id=current_user.id)


@router.post("/{order_id}/cancel", response_model=OrderDetailResponse)
async def cancel_order(
    order_id: str,
    payload: OrderCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancels order before dispatch, releases stock reservations, and issues refunds."""
    service = OrderService(db)
    return await service.cancel_order(order_id, current_user.id, payload)


@router.get("/{order_id}/invoice", response_model=InvoiceResponse)
async def get_tax_invoice(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generates official grocery tax invoice data with line item weight adjustments."""
    service = OrderService(db)
    return await service.generate_invoice_data(order_id)
