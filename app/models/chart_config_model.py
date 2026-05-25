import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChartConfig(Base):
    __tablename__ = "chart_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("diagrams.id"), nullable=False)
    title = Column(String, nullable=False)
    chart_type = Column(String, nullable=False)
    mapping = Column(JSONB, nullable=False)
    ui_config = Column(JSONB, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    dataset = relationship("Diagram", backref="chart_configs")
