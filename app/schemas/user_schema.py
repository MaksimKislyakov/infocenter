from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.core.enums import Role


class UserBase(BaseModel):
    login: str
    full_name: str
    role: Role
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    login: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: UUID

    class Config:
        orm_mode = True
