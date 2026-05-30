from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import Role


class UserBase(BaseModel):
    login: str = Field(..., description="Уникальный логин")
    full_name: str = Field(..., description="ФИО пользователя")
    role: Role = Field(
        ...,
        description="Роль: user (Пользователь), admin (Администратор)",
    )
    job_title: Optional[str] = Field(None, description="Должность")
    email: Optional[EmailStr] = Field(None, description="Email (уникален)")
    is_active: bool = Field(True, description="Активен ли пользователь")


class UserCreate(UserBase):
    password: Optional[str] = Field(
        None, 
        description="Пароль (опционально, если не указан, будет сгенерирован автоматически)"
    )


class UserUpdate(BaseModel):
    login: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    job_title: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class ChangePasswordSchema(BaseModel):
    """Схема для смены пароля пользователем"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., description="Новый пароль")


class UserRead(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
