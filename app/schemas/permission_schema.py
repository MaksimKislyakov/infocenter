from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from app.core.enums import OrgLevel, Block, Action


class PermissionGrantSchema(BaseModel):
    """Схема для выдачи права (одна галочка в админке)"""

    unit_id: UUID = Field(..., description="ID подразделения")
    block: Block = Field(
        ...,
        description="Блок: safety (Безопасность), quality (Качество), production (Производство), economy (Затраты), culture (Культура), all (Все)",
    )
    action: Action = Field(
        ...,
        description="Действие: view (Просмотр), manage (Управление)",
    )


class UnitBriefSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID подразделения")
    name: str = Field(..., description="Название подразделения")
    level_type: OrgLevel = Field(
        ..., description="Уровень: enterprise (Предприятие), shop (Цех), area (Участок)"
    )

    # class Config:
    #     from_attributes = True


class PermissionResponseSchema(BaseModel):
    """Ответ: право пользователя"""
    model_config = ConfigDict(from_attributes=True) 
    
    id: UUID = Field(..., description="ID записи прав")
    unit: UnitBriefSchema = Field(..., description="Подразделение")
    block: Block = Field(
        ...,
        description="Блок: safety (Безопасность), quality (Качество), production (Производство), economy (Затраты), culture (Культура), all (Все)",
    )
    action: Action = Field(
        ...,
        description="Действие: view (Просмотр), manage (Управление)",
    )

    # class Config:
    #     from_attributes = True


class UserPermissionsRequestSchema(BaseModel):
    """Запрос на массовую выдачу прав при создании/редактировании пользователя"""

    permissions: list[PermissionGrantSchema] = Field(default_factory=list)
