import pytest
from unittest.mock import Mock, patch

from app.api.deps import get_current_user, get_current_active_user


class TestDependencies:
    @patch('app.api.deps.decode_access_token')
    @patch('app.api.deps.UserRepository')
    def test_get_current_user_success(self, mock_repo_class, mock_decode, mock_db_session):
        # Arrange
        mock_decode.return_value = {"sub": "testuser"}

        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.get_by_login.return_value = mock_user
        mock_repo_class.return_value = mock_repo

        # Act
        result = get_current_user("valid_token", mock_db_session)

        # Assert
        assert result == mock_user

    @patch('app.api.deps.decode_access_token')
    def test_get_current_user_invalid_token(self, mock_decode, mock_db_session):
        # Arrange
        mock_decode.return_value = {}

        # Act & Assert
        with pytest.raises(Exception):  # Should raise HTTPException
            get_current_user("invalid_token", mock_db_session)

    @patch('app.api.deps.get_current_user')
    def test_get_current_active_user_active(self, mock_get_current_user):
        # Arrange
        mock_user = Mock()
        mock_user.is_active = True
        mock_get_current_user.return_value = mock_user

        # Act
        result = get_current_active_user(mock_user)

        # Assert
        assert result == mock_user

    @patch('app.api.deps.get_current_user')
    def test_get_current_active_user_inactive(self, mock_get_current_user):
        # Arrange
        mock_user = Mock()
        mock_user.is_active = False
        mock_get_current_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(Exception):  # Should raise HTTPException
            get_current_active_user(mock_user)
