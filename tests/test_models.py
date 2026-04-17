import pytest
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.user_model import User
from app.models.round import Round, RoundStatus
from app.db.session import Base


class TestModels:
    def test_user_model_creation(self):
        # Arrange & Act
        user = User(
            login="testuser",
            full_name="Test User",
            role="inspector",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True,
        )

        # Assert
        assert user.login == "testuser"
        assert user.full_name == "Test User"
        assert user.role == "inspector"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True
        assert user.refresh_token is None

    def test_user_table_name(self):
        # Assert
        assert User.__tablename__ == "users"

    def test_user_columns(self):
        # Check that all expected columns exist
        columns = [col.name for col in User.__table__.columns]
        expected_columns = [
            "id", "login", "full_name", "role", "email",
            "password_hash", "refresh_token", "is_active"
        ]

        for col in expected_columns:
            assert col in columns

    def test_round_model_creation(self):
        import uuid
        from datetime import datetime

        master_id = uuid.uuid4()
        inspector_id = uuid.uuid4()
        equipment_ids = ["eq1", "eq2"]

        round_obj = Round(
            master_id=master_id,
            inspector_id=inspector_id,
            equipment_ids=equipment_ids,
            status=RoundStatus.PENDING
        )

        assert round_obj.master_id == master_id
        assert round_obj.inspector_id == inspector_id
        assert round_obj.equipment_ids == equipment_ids
        assert round_obj.status == RoundStatus.PENDING

    def test_round_table_name(self):
        assert Round.__tablename__ == "rounds"

    def test_round_columns(self):
        columns = [col.name for col in Round.__table__.columns]
        expected_columns = [
            "id", "master_id", "inspector_id", "equipment_ids", "status", "created_at", "updated_at"
        ]

        for col in expected_columns:
            assert col in columns
