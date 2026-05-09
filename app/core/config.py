from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int  
    DB_NAME: str

    BACKEND_HOST: str
    BACKEND_PORT: int = 8000

    DEFAULT_ADMIN_LOGIN: str
    DEFAULT_ADMIN_PASSWORD: str
    DEFAULT_ADMIN_FULL_NAME: str
    DEFAULT_ADMIN_EMAIL: str
    DEFAULT_ADMIN_ROLE: str

    MINIO_ENDPOINT: str = "http://minio:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_SECURE: bool
    MINIO_EXTERNAL_ENDPOINT: str

    # Для pydantic-settings v2+ рекомендуется использовать model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ВАЖНО: Добавляем свойство DATABASE_URL, так как ваш env.py его требует!
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()