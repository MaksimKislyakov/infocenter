import pytest
from unittest.mock import Mock, patch

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user_model import User


class TestAuthService:
    def test_verify_password_correct(self):
        # Arrange
        password = "testpassword"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect(self):
        # Arrange
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_get_password_hash(self):
        # Arrange
        password = "testpassword"

        # Act
        hashed = get_password_hash(password)

        # Assert
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)

    @patch('app.services.auth.UserRepository')
    def test_authenticate_user_success(self, mock_repo_class, mock_db_session):
        # Arrange
        mock_user = Mock()
        mock_user.password_hash = get_password_hash("password")
        mock_repo = Mock()
        mock_repo.get_by_login.return_value = mock_user
        mock_repo_class.return_value = mock_repo

        # Act
        result = authenticate_user(mock_db_session, "testuser", "password")

        # Assert
        assert result == mock_user
        mock_repo.get_by_login.assert_called_once_with("testuser")

    @patch('app.services.auth.UserRepository')
    def test_authenticate_user_wrong_password(self, mock_repo_class, mock_db_session):
        # Arrange
        mock_user = Mock()
        mock_user.password_hash = get_password_hash("password")
        mock_repo = Mock()
        mock_repo.get_by_login.return_value = mock_user
        mock_repo_class.return_value = mock_repo

        # Act
        result = authenticate_user(mock_db_session, "testuser", "wrongpassword")

        # Assert
        assert result is None

    @patch('app.services.auth.UserRepository')
    def test_authenticate_user_user_not_found(self, mock_repo_class, mock_db_session):
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_login.return_value = None
        mock_repo_class.return_value = mock_repo

        # Act
        result = authenticate_user(mock_db_session, "nonexistent", "password")

        # Assert
        assert result is None

    @patch('app.services.auth.get_settings')
    def test_create_access_token(self, mock_get_settings):
        # Arrange
        mock_settings = Mock()
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
        mock_settings.SECRET_KEY = "test-secret"
        mock_settings.ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings

        data = {"sub": "testuser"}

        # Act
        token = create_access_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        decoded = decode_access_token(token)
        assert decoded["sub"] == "testuser"

    @patch('app.services.auth.get_settings')
    def test_create_refresh_token(self, mock_get_settings):
        # Arrange
        mock_settings = Mock()
        mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_settings.SECRET_KEY = "test-secret"
        mock_settings.ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings

        data = {"sub": "testuser"}

        # Act
        token = create_refresh_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        decoded = decode_refresh_token(token)
        assert decoded["sub"] == "testuser"
