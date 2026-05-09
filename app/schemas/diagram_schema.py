from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


class ColumnSchema(BaseModel):
    name: str
    type: Literal["string", "number", "date", "boolean"]


class DatasetBase(BaseModel):
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