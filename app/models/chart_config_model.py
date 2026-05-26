import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChartConfig(Base):
    __tablename__ = "chart_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    diagram_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("diagrams.id"), nullable=False
    )
    title = Column(String, nullable=False)
    chart_type = Column(String, nullable=False)
    mapping = Column(JSON, nullable=False)
    ui_config = Column(JSON, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    diagram = relationship("Diagram", backref="chart_configs")
