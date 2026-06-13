from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.file_model import File


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        file_name: str,
        minio_object_name: str,
        file_size: int,
        content_type: str,
        minio_url: str,
        uploaded_by: UUID,
    ) -> File:
        """Создание новой записи о файле в БД"""
        file = File(
            file_name=file_name,
            minio_object_name=minio_object_name,
            file_size=file_size,
            content_type=content_type,
            minio_url=minio_url,
            uploaded_by=uploaded_by,
        )
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def get_by_id(self, file_id: UUID) -> File | None:
        """Получить файл по ID"""
        return self.db.query(File).filter(
            File.id == file_id,
            File.is_deleted == False
        ).first()

    def get_by_minio_object_name(self, object_name: str) -> File | None:
        """Получить файл по имени объекта в MinIO"""
        return self.db.query(File).filter(
            File.minio_object_name == object_name,
            File.is_deleted == False
        ).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[File]:
        """Получить список всех не удаленных файлов"""
        return self.db.query(File).filter(
            File.is_deleted == False
        ).order_by(desc(File.created_at)).offset(skip).limit(limit).all()

    def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[File]:
        """Получить список файлов, загруженных конкретным пользователем"""
        return self.db.query(File).filter(
            File.uploaded_by == user_id,
            File.is_deleted == False
        ).order_by(desc(File.created_at)).offset(skip).limit(limit).all()

    def soft_delete(self, file_id: UUID) -> bool:
        """Мягкое удаление файла (отметить как удаленный)"""
        file = self.get_by_id(file_id)
        if file:
            file.is_deleted = True
            self.db.commit()
            return True
        return False

    def count_all(self) -> int:
        """Получить общее количество файлов"""
        return self.db.query(File).filter(File.is_deleted == False).count()

    def count_by_user(self, user_id: UUID) -> int:
        """Получить количество файлов пользователя"""
        return self.db.query(File).filter(
            File.uploaded_by == user_id,
            File.is_deleted == False
        ).count()
