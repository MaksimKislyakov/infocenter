import pytest
from unittest.mock import Mock

from app.models.user_model import User
from app.schemas.user_schema import UserCreate


@pytest.fixture
def mock_user():
    return User(
        id="test-uuid",
        login="testuser",
        full_name="Test User",
        role="inspector",
        email="test@example.com",
        password_hash="hashed_password",
        refresh_token="refresh_token",
        is_active=True,
    )


@pytest.fixture
def user_create_data():
    return UserCreate(
        login="testuser",
        full_name="Test User",
        role="inspector",
        email="test@example.com",
        password="password123",
        is_active=True,
    )


@pytest.fixture
def mock_db_session():
    return Mock()
