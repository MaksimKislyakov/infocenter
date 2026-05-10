from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base
from app.core.enums import Block, Action


class UserUnitPermission(Base):
    __tablename__ = "user_unit_permissions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    unit_id = Column(PG_UUID(as_uuid=True), ForeignKey("units.id"), nullable=False)
    block = Column(SQLEnum(Block), nullable=False)
    action = Column(SQLEnum(Action), nullable=False)

    # Уникальность: один пользователь не может иметь дублирующее право
    __table_args__ = (
        UniqueConstraint("user_id", "unit_id", "block", "action", name="uq_user_unit_perm"),
    )

    user = relationship("User", back_populates="permissions")
    unit = relationship("Unit", back_populates="permissions")