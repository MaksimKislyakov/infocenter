from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileBase(BaseModel):
    file_name: str = Field(..., description="Имя файла")
    content_type: str = Field(..., description="Тип контента (MIME type)")


class FileCreate(BaseModel):
    """Схема для создания файла при загрузке"""
    file_name: str = Field(..., description="Имя файла")


class FileRead(BaseModel):
    """Схема для вывода информации о файле"""
    id: UUID = Field(..., description="ID файла")
    file_name: str = Field(..., description="Имя файла")
    file_size: int = Field(..., description="Размер файла в байтах")
    content_type: str = Field(..., description="Тип контента")
    minio_url: str = Field(..., description="URL доступа к файлу в MinIO")
    uploaded_by: UUID = Field(..., description="ID пользователя, загрузившего файл")
    created_at: datetime = Field(..., description="Дата загрузки")

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    """Схема для вывода списка файлов"""
    id: UUID
    file_name: str
    file_size: int
    content_type: str
    created_at: datetime
    uploaded_by: UUID

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Схема для ответа при успешной загрузке"""
    id: UUID
    file_name: str
    minio_url: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
