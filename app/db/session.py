from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Use an in-memory SQLite database during tests to avoid external Postgres dependency.
if settings.TESTING:
    SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
