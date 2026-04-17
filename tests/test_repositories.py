import pytest
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.repositories.user_repositoriy import UserRepository
from app.services.auth_service import get_password_hash


class TestUserRepository:
    def test_get_by_login_found(self, db_session: Session, mock_user: User):
        # Arrange
        db_session.add(mock_user)
        db_session.commit()
        repo = UserRepository(db_session)

        # Act
        result = repo.get_by_login("testuser")

        # Assert
        assert result is not None
        assert result.login == "testuser"
        assert result.email == "test@example.com"

    def test_get_by_login_not_found(self, db_session: Session):
        # Arrange
        repo = UserRepository(db_session)

        # Act
        result = repo.get_by_login("nonexistent")

        # Assert
        assert result is None

    def test_create_user(self, db_session: Session, user_create_data: UserCreate):
        # Arrange
        repo = UserRepository(db_session)
        password_hash = get_password_hash("password123")

        # Act
        user = repo.create(user_create_data, password_hash)

        # Assert
        assert user.login == "testuser"
        assert user.full_name == "Test User"
        assert user.role == "inspector"
        assert user.email == "test@example.com"
        assert user.password_hash == password_hash
        assert user.is_active is True

    def test_update_refresh_token(self, db_session: Session, mock_user: User):
        # Arrange
        db_session.add(mock_user)
        db_session.commit()
        repo = UserRepository(db_session)
        new_refresh_token = "new_refresh_token"

        # Act
        updated_user = repo.update_refresh_token(mock_user, new_refresh_token)

        # Assert
        assert updated_user.refresh_token == new_refresh_token
