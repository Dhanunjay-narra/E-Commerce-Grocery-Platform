"""Customer and Merchant In-App Notification API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.authentication.permissions import get_current_user
from app.modules.users.models import User
from app.modules.notifications.schemas import NotificationResponse
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def list_my_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves customer notifications (order updates, price alerts, replenishment reminders)."""
    service = NotificationService(db)
    return await service.list_for_user(current_user.id, unread_only=unread_only)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marks a single notification as read."""
    service = NotificationService(db)
    return await service.mark_as_read(notification_id, current_user.id)


@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marks all customer notifications as read in bulk."""
    service = NotificationService(db)
    return await service.mark_all_as_read(current_user.id)
