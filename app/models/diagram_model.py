from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.session import Base
import uuid


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagramm_id = Column(String, unique=True, nullable=False, index=True)
    columns = Column(JSON, nullable=False)
    rows = Column(JSON, nullable=False)