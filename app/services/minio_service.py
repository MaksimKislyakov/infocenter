import uuid
from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()


class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint="minio:9000",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.external_client = Minio(
            endpoint="minio:9000",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.external_endpoint = settings.MINIO_EXTERNAL_ENDPOINT
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"MinIO bucket error: {e}")

    def upload_file(self, file_data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
        object_name = f"{uuid.uuid4()}_{file_name}"
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            
            external_endpoint = self.external_endpoint.rstrip('/')
            return f"{external_endpoint}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"MinIO upload error: {e}")

    def delete_file(self, object_name: str):
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"MinIO delete error: {e}")