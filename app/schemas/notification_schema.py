from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    diagram_updated = "diagram_updated"


class NotificationPayload(BaseModel):
    type: NotificationType = Field(..., description="Тип уведомления")
    recipient_id: str = Field(..., description="ID получателя уведомления")
    actor_id: str = Field(..., description="ID пользователя, сделавшего изменение")
    diagram_id: str = Field(..., description="ID диаграммы, которая была изменена")
    message: str = Field(..., description="Человеко-читаемое сообщение")
    data: dict | None = Field(None, description="Дополнительные данные уведомления")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Время создания уведомления")


class NotificationResponse(NotificationPayload):
    id: str = Field(..., description="ID уведомления")
    delivered_at: datetime | None = Field(
        None, description="Время, когда уведомление было доставлено через WebSocket"
    )
