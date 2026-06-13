from uuid import UUID
from sqlalchemy.orm import Session

from app.services.minio_service import MinioService
from app.repositories.file_repository import FileRepository
from app.models.file_model import File
from app.core.exceptions import AppError


class FileService:
    def __init__(self, db: Session, minio_service: MinioService):
        self.db = db
        self.repository = FileRepository(db)
        self.minio_service = minio_service

    def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str,
        user_id: UUID,
    ) -> File:
        """
        Загрузить файл в MinIO и сохранить информацию в БД
        """
        try:
            # Загружаем в MinIO и получаем URL
            minio_url = self.minio_service.upload_file(
                file_data=file_data,
                file_name=file_name,
                content_type=content_type,
            )

            # Извлекаем имя объекта из URL
            # URL формата: http://minio:9000/bucket-name/uuid_filename
            minio_object_name = minio_url.split("/")[-1]

            # Сохраняем информацию о файле в БД
            file = self.repository.create(
                file_name=file_name,
                minio_object_name=minio_object_name,
                file_size=len(file_data),
                content_type=content_type,
                minio_url=minio_url,
                uploaded_by=user_id,
            )

            return file
        except Exception as e:
            raise AppError(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )

    def get_file(self, file_id: UUID) -> File:
        """Получить информацию о файле по ID"""
        file = self.repository.get_by_id(file_id)
        if not file:
            raise AppError(
                status_code=404,
                detail="File not found"
            )
        return file

    def download_file(self, file_id: UUID) -> tuple[bytes, str, str]:
        """
        Скачать файл
        Возвращает: (file_data, file_name, content_type)
        """
        file = self.get_file(file_id)
        try:
            file_data = self.minio_service.download_file(file.minio_object_name)
            return file_data, file.file_name, file.content_type
        except Exception as e:
            raise AppError(
                status_code=500,
                detail=f"Failed to download file: {str(e)}"
            )

    def delete_file(self, file_id: UUID, user_id: UUID) -> bool:
        """
        Удалить файл (может удалять только владелец или админ)
        """
        file = self.get_file(file_id)

        # Проверка прав доступа
        if file.uploaded_by != user_id:
            from app.models.user_model import User
            from app.core.enums import Role
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or user.role != Role.ADMIN:
                raise AppError(
                    status_code=403,
                    detail="You can only delete your own files"
                )

        try:
            # Удаляем из MinIO
            self.minio_service.delete_file(file.minio_object_name)
            # Мягко удаляем из БД
            self.repository.soft_delete(file_id)
            return True
        except Exception as e:
            raise AppError(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )

    def list_all_files(self, skip: int = 0, limit: int = 100) -> list[File]:
        """Получить список всех файлов"""
        return self.repository.list_all(skip=skip, limit=limit)

    def list_user_files(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[File]:
        """Получить файлы конкретного пользователя"""
        return self.repository.list_by_user(user_id, skip=skip, limit=limit)

    def get_file_stats(self) -> dict:
        """Получить статистику по файлам"""
        return {
            "total_files": self.repository.count_all(),
        }

    def get_user_file_stats(self, user_id: UUID) -> dict:
        """Получить статистику по файлам пользователя"""
        return {
            "user_files": self.repository.count_by_user(user_id),
        }
