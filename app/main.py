from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

from app.api.routes.auth import router as auth_router
from app.core.config import get_settings
from app.db.session import Base, engine, SessionLocal
from app.services.auth_service import get_password_hash
from app.services.minio_service import MinioService
from app.models.user_model import User

settings = get_settings()
admin_engine = create_engine(f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres", future=True)
with admin_engine.connect() as conn:
    result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db_name"), {"db_name": settings.DB_NAME})
    if not result.fetchone():
        conn.execute(text(f"CREATE DATABASE \"{settings.DB_NAME}\""))
        conn.commit()
        print(f"Database {settings.DB_NAME} created.")
    else:
        print(f"Database {settings.DB_NAME} already exists.")
admin_engine.dispose()

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

settings = get_settings()


def create_default_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.login == settings.DEFAULT_ADMIN_LOGIN).first()
        if not admin:
            admin = User(
                login=settings.DEFAULT_ADMIN_LOGIN,
                full_name=settings.DEFAULT_ADMIN_FULL_NAME,
                role=settings.DEFAULT_ADMIN_ROLE,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("Default admin user created")
        else:
            print("Default admin user already exists")
    finally:
        db.close()


def initialize_minio():
    try:
        minio_service = MinioService()
        print("MinIO bucket initialized")
    except Exception as e:
        print(f"MinIO initialization failed: {e}")


create_default_admin()
initialize_minio()

app = FastAPI(title='Check Backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get('/')
def root():
    return {'message': 'Hello FastAPI + PostgreSQL'}


@app.get('/health')
def health():
    return {'status': 'ok'}

