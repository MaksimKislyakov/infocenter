import uuid
from datetime import datetime
from sqlalchemy import Column, JSON, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLEnum
from app.db.session import Base
from app.schemas.notification_schema import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    diagram_id = Column(PG_UUID(as_uuid=True), ForeignKey("diagrams.id"), nullable=False)
    type = Column(SQLEnum(NotificationType, name="notification_type"), nullable=False)
    message = Column(String(length=1024), nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
