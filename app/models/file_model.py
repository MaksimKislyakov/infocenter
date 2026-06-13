import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    file_name = Column(String(length=255), nullable=False, index=True)
    minio_object_name = Column(String(length=500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)  # в байтах
    content_type = Column(String(length=255), nullable=False, default="application/octet-stream")
    minio_url = Column(String(length=1000), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Отношение с пользователем
    user = relationship("User", foreign_keys=[uploaded_by])
