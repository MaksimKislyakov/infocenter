from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import Role


class UserBase(BaseModel):
    login: str
    full_name: str
    role: Role
    job_title: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    login: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    job_title: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
