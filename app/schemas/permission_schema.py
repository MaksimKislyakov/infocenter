from pydantic import BaseModel, Field
from uuid import UUID
from app.core.enums import OrgLevel, Block, Action


class PermissionGrantSchema(BaseModel):
    """Схема для выдачи права (одна галочка в админке)"""
    unit_id: UUID
    block: Block
    action: Action

class UnitBriefSchema(BaseModel):
    id: UUID
    name: str
    level_type: OrgLevel 
    class Config:
        from_attributes = True

class PermissionResponseSchema(BaseModel):
    """Ответ: право пользователя"""
    id: UUID
    unit: UnitBriefSchema
    # unit_id: UUID
    # unit_name: str
    # unit_level: OrgLevel
    block: Block
    action: Action

    class Config:
        from_attributes = True


class UserPermissionsRequestSchema(BaseModel):
    """Запрос на массовую выдачу прав при создании/редактировании пользователя"""
    permissions: list[PermissionGrantSchema] = Field(default_factory=list)