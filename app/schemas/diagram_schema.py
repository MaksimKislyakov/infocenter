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
    diagramm_id: str


class DatasetUpdate(DatasetBase):
    diagramm_id: str | None = None


class DatasetResponse(DatasetBase):
    id: UUID
    diagramm_id: str

    class Config:
        from_attributes = True