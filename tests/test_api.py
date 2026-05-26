import os
os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient

from app.main import app

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

    # Получаем текущего пользователя и его id
    me_response = client.get("/users/me", headers=auth_headers)
    assert me_response.status_code == 200
    user_id = me_response.json()["id"]

    units_response = client.get("/units/", headers=auth_headers)
    assert units_response.status_code == 200
    units = units_response.json()
    enterprise = next((unit for unit in units if unit["level_type"] == "enterprise"), None)
    assert enterprise is not None, "Не найдено подразделение уровня enterprise для создания Цеха"

    # Создаём новый юнит Цех-2
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

    grant_response = client.post(
        f"/permissions/users/{user_id}",
        headers=auth_headers,
        json={
            "permissions": [
                {
                    "unit_id": unit_id,
                    "block": "safety",
                    "action": "manage",
                }
            ]
        },
    )
    assert grant_response.status_code == 200
    granted_permissions = grant_response.json()
    assert any(p["block"] == "safety" and p["action"] == "manage" for p in granted_permissions)

    # Создаём диаграмму в блоке safety для Цех-2
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

    # Создаём минимальную конфигурацию графика для диаграммы
    chart_response = client.post(
        "/charts/",
        headers=auth_headers,
        json={
            "title": "Test Chart",
            "chartType": "bar",
            "datasetId": diagram["id"],
            "mapping": {"metric": "metric"},
            "uiConfig": {"legend": True},
        },
    )
    assert chart_response.status_code == 201
    chart = chart_response.json()
    assert chart["datasetId"] == diagram["id"]
    assert chart["title"] == "Test Chart"
