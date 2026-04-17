import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from io import BytesIO

from app.main import app
from app.models.user_model import User


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    # Mock JWT token for testing
    return {"Authorization": "Bearer mock_token"}


class TestAuthAPI:
    def test_login_success(self, client, db_session):
        # Arrange
        user = User(
            login="testuser",
            full_name="Test User",
            role="inspector",
            email="test@example.com",
            password_hash="$2b$12$test.hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        login_data = {"login": "testuser", "password": "password"}

        # Act
        response = client.post("/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_credentials(self, client):
        # Arrange
        login_data = {"login": "wronguser", "password": "wrongpass"}

        # Act
        response = client.post("/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "Incorrect login or password" in response.json()["detail"]

    @patch('app.api.auth.decode_refresh_token')
    @patch('app.api.auth.UserRepository')
    def test_refresh_token_success(self, mock_repo_class, mock_decode, client, db_session):
        # Arrange
        mock_decode.return_value = {"sub": "testuser"}

        mock_user = Mock()
        mock_user.refresh_token = "valid_refresh_token"
        mock_repo = Mock()
        mock_repo.get_by_login.return_value = mock_user
        mock_repo_class.return_value = mock_repo

        refresh_data = {"refresh_token": "valid_refresh_token"}

        # Act
        response = client.post("/auth/refresh", json=refresh_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client):
        # Arrange
        refresh_data = {"refresh_token": "invalid_token"}

        # Act
        response = client.post("/auth/refresh", json=refresh_data)

        # Assert
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestUsersAPI:
    @patch('app.api.users.get_db')
    @patch('app.api.users.require_admin')
    def test_create_user_success(self, mock_require_admin, mock_get_db, client, user_create_data, db_session):
        # Arrange
        mock_require_admin.return_value = Mock(role="admin")

        def get_db_override():
            yield db_session

        mock_get_db.side_effect = get_db_override

        # Act
        response = client.post("/users/", json=user_create_data.dict())

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "testuser"
        assert data["email"] == "test@example.com"

    @patch('app.api.users.get_db')
    @patch('app.api.users.require_admin')
    def test_create_user_duplicate_email(self, mock_require_admin, mock_get_db, client, user_create_data, db_session):
        # Arrange
        mock_require_admin.return_value = Mock(role="admin")

        def get_db_override():
            yield db_session

        mock_get_db.side_effect = get_db_override

        # Create first user
        client.post("/users/", json=user_create_data.dict())

        # Try to create duplicate
        # Act
        response = client.post("/users/", json=user_create_data.dict())

        # Assert
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @patch('app.api.users.get_current_active_user')
    def test_read_current_user(self, mock_get_current_user, client):
        # Arrange
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_user.email = "test@example.com"
        mock_get_current_user.return_value = mock_user

        # Act
        response = client.get("/users/me")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "testuser"
        assert data["email"] == "test@example.com"

    @patch('app.api.users.get_db')
    @patch('app.api.users.require_master_or_higher')
    def test_read_user_master_ok(self, mock_require_master, mock_get_db, client, db_session):
        # Arrange
        from app.models.user_model import User

        user = User(
            login="targetuser",
            full_name="Target User",
            role="inspector",
            email="target@example.com",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        def get_db_override():
            yield db_session

        mock_get_db.side_effect = get_db_override
        mock_require_master.return_value = Mock(role="master")

        # Act
        response = client.get(f"/users/{user.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "targetuser"
        assert data["email"] == "target@example.com"

    @patch('app.api.users.require_master_or_higher')
    def test_read_user_inspector_forbidden(self, mock_require_master, client):
        # Arrange
        mock_require_master.side_effect = HTTPException(status_code=403, detail="Insufficient privileges")

        # Act
        response = client.get("/users/00000000-0000-0000-0000-000000000000")

        # Assert
        assert response.status_code == 403

    @patch('app.api.users.get_db')
    @patch('app.api.users.require_admin')
    def test_update_user_as_admin(self, mock_require_admin, mock_get_db, client, db_session):
        # Arrange
        from app.models.user_model import User

        user = User(
            login="targetuser",
            full_name="Target User",
            role="inspector",
            email="target@example.com",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        def get_db_override():
            yield db_session

        mock_get_db.side_effect = get_db_override
        mock_require_admin.return_value = Mock(role="admin")

        update_data = {"full_name": "Updated User", "role": "master"}

        # Act
        response = client.put(f"/users/{user.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated User"
        assert data["role"] == "master"

    @patch('app.api.users.get_db')
    @patch('app.api.users.require_admin')
    def test_delete_user_as_admin(self, mock_require_admin, mock_get_db, client, db_session):
        # Arrange
        from app.models.user_model import User

        user = User(
            login="targetuser",
            full_name="Target User",
            role="inspector",
            email="target@example.com",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        def get_db_override():
            yield db_session

        mock_get_db.side_effect = get_db_override
        mock_require_admin.return_value = Mock(role="admin")

        # Act
        response = client.delete(f"/users/{user.id}")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"detail": "User deleted"}


class TestEquipmentAPI:
    @patch('app.api.equipment.get_current_active_user')
    def test_create_equipment_success(self, mock_get_current_user, client):
        mock_get_current_user.return_value = Mock()

        equipment_data = {
            "machine_number": "M-101",
            "description": "Компрессор в цехе 1",
            "normal_pressure": 10.5,
            "normal_temperature": 25.0,
            "normal_vibration": 0.1,
            "normal_fault": False,
            "normal_fault_comment": None,
            "normal_has_photo": True,
        }

        response = client.post("/equipment/", json=equipment_data)

        assert response.status_code == 200
        data = response.json()
        assert data["machine_number"] == "M-101"
        assert data["description"] == "Компрессор в цехе 1"
        assert data["normal_pressure"] == 10.5
        assert data["normal_temperature"] == 25.0
        assert data["normal_vibration"] == 0.1
        assert data["normal_fault"] is False
        assert data["normal_has_photo"] is True
        assert "id" in data

    @patch('app.api.equipment.get_current_active_user')
    def test_create_equipment_requires_machine_number(self, mock_get_current_user, client):
        mock_get_current_user.return_value = Mock()

        equipment_data = {
            "description": "Нет номера машины",
        }

        response = client.post("/equipment/", json=equipment_data)

        assert response.status_code == 422


    @patch('app.api.equipment.get_current_active_user')
    @patch('app.api.equipment.MinioService')
    def test_upload_photo_success(self, mock_minio_service, mock_get_current_user, client):
        mock_get_current_user.return_value = Mock()
        mock_minio = Mock()
        mock_minio.upload_file.return_value = "http://minio.example.com/photo.jpg"
        mock_minio_service.return_value = mock_minio

        # Create a test image file
        file_data = BytesIO(b"fake image data")
        file_data.seek(0)

        response = client.post(
            "/equipment/upload-photo",
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )

        assert response.status_code == 200
        data = response.json()
        assert "photo_url" in data
        assert data["photo_url"] == "http://minio.example.com/photo.jpg"


class TestHealthAPI:
    def test_health_check(self, client):
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
