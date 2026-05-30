from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


class NotificationType(str, Enum):
    diagram_updated = "diagram_updated"


class NotificationPayload(BaseModel):
    type: NotificationType = Field(..., description="Тип уведомления")
    recipient_id: str = Field(..., description="ID получателя уведомления")
    actor_id: str = Field(..., description="ID пользователя, сделавшего изменение")
    diagram_id: str = Field(..., description="ID диаграммы, которая была изменена")
    message: str = Field(..., description="Человеко-читаемое сообщение")
    data: dict | None = Field(None, description="Дополнительные данные уведомления")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время создания уведомления")
