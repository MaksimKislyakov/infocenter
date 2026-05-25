from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

from app.core.enums import Block


class ColumnSchema(BaseModel):
    name: str
    type: Literal["string", "number", "date", "boolean"]


class DatasetBase(BaseModel):
    block: Block
    unit_id: UUID
    columns: list[ColumnSchema]
    rows: list[dict]


class DatasetCreate(DatasetBase):
    id: UUID | None = None


class DatasetUpdate(DatasetBase):
    id: UUID | None = None


class DatasetResponse(DatasetBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiagramAuditResponse(BaseModel):
    id: UUID
    diagram_id: UUID
    updated_by: UUID
    updated_at: datetime
    operation: int  # 0: create, 1: update, 2: delete
    old_values: dict | None = None
    new_values: dict | None = None

    class Config:
        from_attributes = True