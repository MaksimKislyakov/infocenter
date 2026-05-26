from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ChartBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., description="Название графика")
    chart_type: str = Field(
        ..., alias="chartType", description="Тип графика: bar, pie, line, scatter"
    )
    diagram_id: UUID = Field(..., alias="diagramId", description="ID диаграммы")
    mapping: dict[str, Any] = Field(..., description="Маппинг данных для графика")
    ui_config: dict[str, Any] = Field(
        ..., alias="uiConfig", description="UI-настройки графика"
    )
    order: int | None = Field(None, description="Позиция графика в списке")


class ChartCreate(ChartBase):
    pass


class ChartUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = Field(None, description="Название графика")
    chart_type: str | None = Field(None, alias="chartType", description="Тип графика")
    diagram_id: UUID | None = Field(None, alias="diagramId", description="ID диаграммы")
    mapping: dict[str, Any] | None = Field(None, description="Маппинг данных")
    ui_config: dict[str, Any] | None = Field(
        None, alias="uiConfig", description="UI-настройки графика"
    )
    order: int | None = Field(None, description="Позиция графика в списке")


class ChartResponse(ChartBase):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
