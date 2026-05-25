import uuid
from datetime import datetime
from sqlalchemy import Column, JSON, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class DiagramAudit(Base):
    __tablename__ = "diagram_audit"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagram_id = Column(PG_UUID(as_uuid=True), ForeignKey("diagrams.id"), nullable=False)
    updated_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    operation = Column(Integer, nullable=False)  # 0: create, 1: update, 2: delete
    old_values = Column(JSON, nullable=True)  # Previous values before update
    new_values = Column(JSON, nullable=True)  # New values after update

    diagram = relationship("Diagram", backref="audit_logs")
    user = relationship("User", backref="diagram_changes")
