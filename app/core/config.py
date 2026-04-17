from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    DEFAULT_ADMIN_LOGIN: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin"
    DEFAULT_ADMIN_FULL_NAME: str = "Admin Admin Admin"
    DEFAULT_ADMIN_EMAIL: str = "admin@admin.ru"
    DEFAULT_ADMIN_ROLE: str = "management"

    MINIO_ENDPOINT: str = "http://minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "equipment-photos"
    MINIO_SECURE: bool = False
    MINIO_EXTERNAL_ENDPOINT: str = "http://localhost:9000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

