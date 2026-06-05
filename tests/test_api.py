import os

os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.repositories.notification_repository import NotificationRepository

client = TestClient(app)


def test_admin_can_create_diagram_with_chart_config():
    # Авторизация admin/admin
    login_response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Получаем информацию о текущем пользователе (admin) и его id
    me_response = client.get("/users/me", headers=auth_headers)
    assert me_response.status_code == 200
    user_id = me_response.json()["id"]

    # Получаем список юнитов и ищем корневой уровень enterprise
    units_response = client.get("/units/", headers=auth_headers)
    assert units_response.status_code == 200
    units = units_response.json()
    enterprise = next(
        (unit for unit in units if unit["level_type"] == "enterprise"), None
    )
    assert (
        enterprise is not None
    ), "Не найдено подразделение уровня enterprise для создания Цеха"

    # Создаём новый юнит (Цех-2) под найденным enterprise
    create_unit_response = client.post(
        "/units/",
        headers=auth_headers,
        params={
            "name": "Цех-2",
            "level_type": "shop",
            "parent_id": enterprise["id"],
        },
    )
    assert create_unit_response.status_code == 201
    unit_id = create_unit_response.json()["id"]

    # Создаём диаграмму в блоке safety для созданного юнита
    diagram_response = client.post(
        "/diagrams/",
        headers=auth_headers,
        json={
            "block": "safety",
            "unit_id": unit_id,
            "columns": [{"name": "metric", "type": "string"}],
            "rows": [{"metric": "ok"}],
        },
    )
    assert diagram_response.status_code == 201
    diagram = diagram_response.json()
    assert diagram["unit_id"] == unit_id
    assert diagram["block"] == "safety"

    # Создаём минимальную конфигурацию графика для созданной диаграммы
    chart_response = client.post(
        "/charts/",
        headers=auth_headers,
        json={
            "title": "Test Chart",
            "chartType": "bar",
            "diagramId": diagram["id"],
            "mapping": {"metric": "metric"},
            "uiConfig": {"legend": True},
        },
    )
    assert chart_response.status_code == 201
    chart = chart_response.json()
    assert chart["diagramId"] == diagram["id"]
    assert chart["title"] == "Test Chart"


def test_user_cannot_create_diagram_and_chart_without_permissions_then_can_after_grant():
    # Авторизуемся как админ для подготовки окружения (создание юнита и диаграммы)
    login_response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin"},
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    units_response = client.get("/units/", headers=admin_headers)
    assert units_response.status_code == 200
    units = units_response.json()
    enterprise = next(
        (unit for unit in units if unit["level_type"] == "enterprise"), None
    )
    assert enterprise is not None

    # Админ создаёт новый юнит (Цех-3)
    create_unit_response = client.post(
        "/units/",
        headers=admin_headers,
        params={
            "name": "Цех-3",
            "level_type": "shop",
            "parent_id": enterprise["id"],
        },
    )
    assert create_unit_response.status_code == 201
    unit_id = create_unit_response.json()["id"]

    # Админ создаёт диаграмму в блоке safety для Цех-3
    diagram_response = client.post(
        "/diagrams/",
        headers=admin_headers,
        json={
            "block": "safety",
            "unit_id": unit_id,
            "columns": [{"name": "metric", "type": "string"}],
            "rows": [{"metric": "ok"}],
        },
    )
    assert diagram_response.status_code == 201
    diagram = diagram_response.json()

    # Авторизуемся как обычный пользователь testuser
    login_user = client.post(
        "/auth/login",
        json={"login": "testuser", "password": "password"},
    )
    assert login_user.status_code == 200
    user_token = login_user.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Попытка обычного пользователя создать диаграмму — ожидаем 403 (нет прав)
    user_diag_resp = client.post(
        "/diagrams/",
        headers=user_headers,
        json={
            "block": "safety",
            "unit_id": unit_id,
            "columns": [{"name": "metric", "type": "string"}],
            "rows": [{"metric": "ok"}],
        },
    )
    assert user_diag_resp.status_code == 403

    # Попытка обычного пользователя создать конфиг графика для существующей диаграммы — ожидаем 403
    user_chart_resp = client.post(
        "/charts/",
        headers=user_headers,
        json={
            "title": "User Chart",
            "chartType": "bar",
            "diagramId": diagram["id"],
            "mapping": {"metric": "metric"},
            "uiConfig": {"legend": True},
        },
    )
    assert user_chart_resp.status_code == 403

    # Админ находит testuser в списке пользователей для выдачи прав
    me_admin = client.get("/users/me", headers=admin_headers)
    assert me_admin.status_code == 200
    users_list = client.get("/users/", headers=admin_headers)
    assert users_list.status_code == 200
    testuser = next((u for u in users_list.json() if u["login"] == "testuser"), None)
    assert testuser is not None

    # Админ выдаёт testuser право manage в блоке safety для созданного юнита
    grant_response = client.post(
        f"/permissions/users/{testuser['id']}",
        headers=admin_headers,
        json={
            "permissions": [
                {"unit_id": unit_id, "block": "safety", "action": "manage"}
            ]
        },
    )
    assert grant_response.status_code == 200

    # После выдачи прав — user может создать диаграмму
    user_diag_resp2 = client.post(
        "/diagrams/",
        headers=user_headers,
        json={
            "block": "safety",
            "unit_id": unit_id,
            "columns": [{"name": "metric", "type": "string"}],
            "rows": [{"metric": "ok"}],
        },
    )
    assert user_diag_resp2.status_code == 201

    # И может создать конфиг графика для диаграммы
    user_chart_resp2 = client.post(
        "/charts/",
        headers=user_headers,
        json={
            "title": "User Chart",
            "chartType": "bar",
            "diagramId": diagram["id"],
            "mapping": {"metric": "metric"},
            "uiConfig": {"legend": True},
        },
    )
    assert user_chart_resp2.status_code == 201


def test_admin_can_add_user_permissions():
    login_response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin"},
    )
    assert login_response.status_code == 200
    admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    create_user_response = client.post(
        "/users/",
        headers=admin_headers,
        json={
            "login": "permission_test_user",
            "password": "password",
            "full_name": "Permission Test",
            "role": "user",
        },
    )
    assert create_user_response.status_code == 200
    user_id = create_user_response.json()["id"]

    units_response = client.get("/units/", headers=admin_headers)
    assert units_response.status_code == 200
    units = units_response.json()
    enterprise = next((unit for unit in units if unit["level_type"] == "enterprise"), None)
    assert enterprise is not None

    create_unit_response = client.post(
        "/units/",
        headers=admin_headers,
        params={
            "name": "Цех-AddPerm",
            "level_type": "shop",
            "parent_id": enterprise["id"],
        },
    )
    assert create_unit_response.status_code == 201
    unit_id = create_unit_response.json()["id"]

    # Сначала даём два права
    grant_response = client.post(
        f"/permissions/users/{user_id}",
        headers=admin_headers,
        json={
            "permissions": [
                {"unit_id": unit_id, "block": "safety", "action": "view"},
                {"unit_id": unit_id, "block": "quality", "action": "manage"},
            ]
        },
    )
    assert grant_response.status_code == 200
    assert len(grant_response.json()) == 2

    # Добавляем третье право, не удаляя предыдущие
    add_response = client.post(
        f"/permissions/users/{user_id}",
        headers=admin_headers,
        json={
            "permissions": [
                {"unit_id": unit_id, "block": "culture", "action": "manage"}
            ]
        },
    )
    assert add_response.status_code == 200
    assert len(add_response.json()) == 3

    current_perms = client.get(f"/permissions/users/{user_id}", headers=admin_headers)
    assert current_perms.status_code == 200
    perms = current_perms.json()
    assert len(perms) == 3
    assert any(p["block"] == "safety" and p["action"] == "view" for p in perms)
    assert any(p["block"] == "quality" and p["action"] == "manage" for p in perms)
    assert any(p["block"] == "culture" and p["action"] == "manage" for p in perms)
    # Авторизуемся как admin для подготовки уведомления
    login_response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin"},
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    me_response = client.get("/users/me", headers=admin_headers)
    assert me_response.status_code == 200
    admin_id = me_response.json()["id"]

    # Создаём диаграмму, чтобы был валидный diagram_id для уведомления
    units_response = client.get("/units/", headers=admin_headers)
    assert units_response.status_code == 200
    units = units_response.json()
    enterprise = next((unit for unit in units if unit["level_type"] == "enterprise"), None)
    assert enterprise is not None

    create_unit_response = client.post(
        "/units/",
        headers=admin_headers,
        params={
            "name": "Цех-Notification-History",
            "level_type": "shop",
            "parent_id": enterprise["id"],
        },
    )
    assert create_unit_response.status_code == 201
    unit_id = create_unit_response.json()["id"]

    diagram_response = client.post(
        "/diagrams/",
        headers=admin_headers,
        json={
            "block": "safety",
            "unit_id": unit_id,
            "columns": [{"name": "metric", "type": "string"}],
            "rows": [{"metric": "ok"}],
        },
    )
    assert diagram_response.status_code == 201
    diagram_id = diagram_response.json()["id"]

    # Авторизуемся как обычный пользователь testuser
    login_user = client.post(
        "/auth/login",
        json={"login": "testuser", "password": "password"},
    )
    assert login_user.status_code == 200
    user_token = login_user.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    user_me_resp = client.get("/users/me", headers=user_headers)
    assert user_me_resp.status_code == 200
    user_id = user_me_resp.json()["id"]

    # Создаём уведомление вручную в базе для текущего пользователя
    db = SessionLocal()
    try:
        repo = NotificationRepository(db)
        repo.create_notification(
            recipient_id=user_id,
            actor_id=admin_id,
            diagram_id=diagram_id,
            message="История уведомлений тест",
            data={"diagram_id": diagram_id},
        )
    finally:
        db.close()

    history_response = client.get("/notifications", headers=user_headers)
    assert history_response.status_code == 200
    notifications = history_response.json()
    assert any(
        item["message"] == "История уведомлений тест" for item in notifications
    )
