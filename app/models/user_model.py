import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum

from app.core.enums import Role
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    login = Column(String(length=255), unique=True, nullable=False, index=True)
    full_name = Column(String(length=255), nullable=False)
    role = Column(Enum(Role), nullable=False)
    job_title = Column(String, nullable=True)
    email = Column(String(length=255), unique=True, nullable=True)
    password_hash = Column(String(length=255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)



