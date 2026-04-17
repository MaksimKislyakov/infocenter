import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate


class TestUserService:
    @patch('app.services.user.UserRepository')
    def test_create_user_success(self, mock_repo_class, mock_db_session, user_create_data):
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = Mock(login="testuser")
        mock_repo_class.return_value = mock_repo

        service = UserService(mock_db_session)

        # Act
        result = service.create_user(user_create_data)

        # Assert
        mock_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_repo.create.assert_called_once()
        assert result.login == "testuser"

    @patch('app.services.user.UserRepository')
    def test_create_user_email_exists(self, mock_repo_class, mock_db_session, user_create_data):
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = Mock()  # Email exists
        mock_repo_class.return_value = mock_repo

        service = UserService(mock_db_session)

        # Act & Assert
        with pytest.raises(Exception):  # Should raise exception for duplicate email
            service.create_user(user_create_data)

    @patch('app.services.user.UserRepository')
    def test_get_by_email(self, mock_repo_class, mock_db_session):
        # Arrange
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = mock_user
        mock_repo_class.return_value = mock_repo

        service = UserService(mock_db_session)

        # Act
        result = service.get_by_email("test@example.com")

        # Assert
        mock_repo.get_by_email.assert_called_once_with("test@example.com")
        assert result == mock_user
