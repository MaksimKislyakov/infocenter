from sqlalchemy.orm import Session

from app.repositories.user_repositoriy import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.auth_service import get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_user(self, user_create: UserCreate):
        if self.repo.get_by_login(user_create.login) is not None:
            raise ValueError("Login already registered")
        if user_create.email and self.repo.get_by_email(user_create.email) is not None:
            raise ValueError("Email already registered")
        password_hash = get_password_hash(user_create.password)
        return self.repo.create(user_create, password_hash)

    def get_by_login(self, login: str):
        return self.repo.get_by_login(login)

    def get_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def get_by_id(self, user_id: str):
        return self.repo.get_by_id(user_id)

    def list_users(self):
        return self.repo.list()

    def update_user(self, user_id: str, user_update: UserUpdate):
        user = self.get_by_id(user_id)
        if user is None:
            return None
        if user_update.login and user_update.login != user.login:
            existing = self.repo.get_by_login(user_update.login)
            if existing is not None and existing.id != user.id:
                raise ValueError("Login already registered")
        if user_update.email and user_update.email != user.email:
            existing = self.repo.get_by_email(user_update.email)
            if existing is not None and existing.id != user.id:
                raise ValueError("Email already registered")
        password_hash = get_password_hash(user_update.password) if user_update.password else None
        return self.repo.update(user, user_update, password_hash)

    def delete_user(self, user_id: str):
        user = self.get_by_id(user_id)
        if user is None:
            return None
        self.repo.delete(user)
        return user
