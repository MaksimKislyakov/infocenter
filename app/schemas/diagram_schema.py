from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID

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
    id: UUID


class DatasetUpdate(DatasetBase):
    id: UUID | None = None


class DatasetResponse(DatasetBase):
    id: UUID

    class Config:
        from_attributes = True