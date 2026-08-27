"""Pydantic schemas for Notification payloads and state updates."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NotificationCreate(BaseModel):
    user_id: str
    title: str = Field(..., min_length=2, max_length=150)
    body: str = Field(..., min_length=2)
    channel: str = Field(default="IN_APP", description="IN_APP, EMAIL, SMS, PUSH")
    type: str = Field(default="GENERAL")
    data_payload: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    channel: str
    type: str
    data_payload: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
