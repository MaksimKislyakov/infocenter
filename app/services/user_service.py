import logging
from sqlalchemy.orm import Session

from app.repositories.user_repositoriy import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.auth_service import get_password_hash, generate_password, verify_password
from app.services.email.email_service import EmailService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.email_service = EmailService()

    def create_user(self, user_create: UserCreate):
        if self.repo.get_by_login(user_create.login) is not None:
            raise ValueError("Login already registered")
        if user_create.email and self.repo.get_by_email(user_create.email) is not None:
            raise ValueError("Email already registered")
        
        # Генерируем пароль, если он не был передан (только для явного указания)
        password = user_create.password or generate_password()
        password_hash = get_password_hash(password)
        
        user = self.repo.create(user_create, password_hash)
        
        # Отправляем пароль на почту если указана
        if user.email:
            email_sent = self.email_service.send_password_email(
                user.email, user.login, password
            )
            if email_sent:
                logger.info(f"Password sent to {user.email} for user {user.login}")
            else:
                logger.warning(f"Failed to send password email to {user.email}")
        
        return user

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
        # Игнорируем пароль при обновлении - только через reset/change endpoints
        return self.repo.update(user, user_update, password_hash=None)

    def reset_password(self, user_id: str) -> bool:
        """
        Сброс пароля (только админ).
        Генерирует новый пароль и отправляет его на почту пользователя.
        
        Returns:
            True если пароль успешно сброшен, False иначе
        """
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        if not user.email:
            logger.warning(f"Cannot reset password for user {user_id}: no email")
            return False
        
        # Генерируем новый пароль
        new_password = generate_password()
        password_hash = get_password_hash(new_password)
        
        # Обновляем в БД
        self.repo.update_password(user, password_hash)
        
        # Отправляем новый пароль на почту
        email_sent = self.email_service.send_password_email(
            user.email, user.login, new_password
        )
        
        if email_sent:
            logger.info(f"Password reset for user {user.login}, new password sent to {user.email}")
        else:
            logger.warning(f"Failed to send reset password email to {user.email}")
        
        return email_sent

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Смена пароля самим пользователем.
        Требует проверку текущего пароля.
        
        Returns:
            True если пароль успешно изменён, False иначе
        """
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        # Проверяем текущий пароль
        if not verify_password(current_password, user.password_hash):
            logger.warning(f"Wrong password for user {user_id}")
            return False
        
        # Обновляем пароль
        password_hash = get_password_hash(new_password)
        self.repo.update_password(user, password_hash)
        
        logger.info(f"Password changed for user {user.login}")
        return True

    def delete_user(self, user_id: str):
        user = self.get_by_id(user_id)
        if user is None:
            return None
        self.repo.delete(user)
        return user
