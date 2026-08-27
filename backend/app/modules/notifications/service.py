"""Multi-channel notification routing and state management service."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationCreate, NotificationResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: str, unread_only: bool = False) -> List[NotificationResponse]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        query = query.order_by(Notification.created_at.desc())

        result = await self.db.execute(query)
        notifications = list(result.scalars().all())
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def send_notification(self, payload: NotificationCreate) -> NotificationResponse:
        n = Notification(
            user_id=payload.user_id,
            title=payload.title,
            body=payload.body,
            channel=payload.channel,
            type=payload.type,
            data_payload=payload.data_payload,
            is_read=False,
        )
        self.db.add(n)
        await self.db.flush()
        return NotificationResponse.model_validate(n)

    async def mark_as_read(self, notification_id: str, user_id: str) -> NotificationResponse:
        query = select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
        result = await self.db.execute(query)
        n = result.scalar_one_or_none()
        if not n:
            raise EntityNotFoundError("Notification not found.")

        n.is_read = True
        n.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        return NotificationResponse.model_validate(n)

    async def mark_all_as_read(self, user_id: str) -> dict:
        now = datetime.now(timezone.utc)
        stmt = (
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
            .values(is_read=True, read_at=now)
        )
        result = await self.db.execute(stmt)
        return {"success": True, "updated_count": result.rowcount}
