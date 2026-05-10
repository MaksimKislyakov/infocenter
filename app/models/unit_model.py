from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base
from app.core.enums import OrgLevel


class Unit(Base):
    __tablename__ = "units"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    level_type = Column(SQLEnum(OrgLevel), nullable=False)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("units.id"), nullable=True)

    parent = relationship("Unit", remote_side=[id], backref="children")
    permissions = relationship("UserUnitPermission", back_populates="unit", cascade="all, delete-orphan")