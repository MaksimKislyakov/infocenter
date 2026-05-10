import uuid
from sqlalchemy import Column, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.session import Base
from app.core.enums import Block


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    columns = Column(JSON, nullable=False)
    rows = Column(JSON, nullable=False)

    block = Column(SQLEnum(Block), nullable=False)
    unit_id = Column(PG_UUID(as_uuid=True), ForeignKey("units.id"), nullable=False)
    unit = relationship("Unit", backref="diagrams")