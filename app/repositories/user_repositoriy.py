from typing import Optional
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_login(self, login: str) -> User | None:
        return self.db.query(User).filter(User.login == login).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def list(self) -> list[User]:
        return self.db.query(User).all()

    def create(self, user_create: UserCreate, password_hash: str) -> User:
        user = User(
            login=user_create.login,
            full_name=user_create.full_name,
            role=user_create.role,
            email=user_create.email,
            password_hash=password_hash,
            is_active=user_create.is_active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, user_update: UserUpdate, password_hash: Optional[str] = None) -> User:
        if user_update.login is not None:
            user.login = user_update.login
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.role is not None:
            user.role = user_update.role
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        if password_hash is not None:
            user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def update_refresh_token(self, user: User, refresh_token: str):
        user.refresh_token = refresh_token
        self.db.commit()
        self.db.refresh(user)
        return user
