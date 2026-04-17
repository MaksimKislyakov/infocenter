import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base
from app.core.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        DB_USER="test",
        DB_PASSWORD="test",
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test_db",
        SECRET_KEY="test-secret-key",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
        REFRESH_TOKEN_EXPIRE_DAYS=7,
        BACKEND_HOST="0.0.0.0",
        BACKEND_PORT=8000,
        DEFAULT_ADMIN_LOGIN="admin",
        DEFAULT_ADMIN_PASSWORD="admin",
        DEFAULT_ADMIN_FULL_NAME="Admin Admin Admin",
        DEFAULT_ADMIN_EMAIL="admin@admin.ru",
        DEFAULT_ADMIN_ROLE="management",
    )


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
