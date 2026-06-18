import pytest
from fastapi.testclient import TestClient
from app.db.database import get_session


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password", "full_name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "test2@example.com", "password": "password"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "test2@example.com", "password": "password"}
    )
    assert response.status_code == 400

def test_login_user(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "password"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_me(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "password"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "me@example.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

def test_update_me(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "update@example.com", "password": "password"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "update@example.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"diet_baseline": "vegan", "household_size": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["diet_baseline"] == "vegan"
    assert data["household_size"] == 2



def test_log_activity(client: TestClient, auth_token: str):
    import app.db.seed_emission_factors as seeder
    seeder.seed_factors()
    
    response = client.post(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "category": "Transport",
            "subtype": "Car, petrol (avg)",
            "quantity": 10,
            "unit": "km",
            "activity_date": "2026-06-17T10:00:00Z"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["co2e_kg"] == 1.7  # 10 * 0.17

def test_list_activities(client: TestClient, auth_token: str):
    import app.db.seed_emission_factors as seeder
    seeder.seed_factors()
    client.post(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "category": "Transport",
            "subtype": "Car, petrol (avg)",
            "quantity": 10,
            "unit": "km",
            "activity_date": "2026-06-17T10:00:00Z"
        }
    )
    response = client.get(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_delete_activity(client: TestClient, auth_token: str):
    import app.db.seed_emission_factors as seeder
    seeder.seed_factors()

    client.post(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "category": "Transport",
            "subtype": "Car, petrol (avg)",
            "quantity": 10,
            "unit": "km",
            "activity_date": "2026-06-17T10:00:00Z"
        }
    )
    response = client.get(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    activity_id = response.json()[0]["id"]
    
    del_res = client.delete(
        f"/activities/{activity_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert del_res.status_code == 204
    
    response2 = client.get(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert len(response2.json()) == 0

def test_footprint_summary(client: TestClient, auth_token: str):
    client.post(
        "/activities",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "category": "Transport",
            "subtype": "Car, petrol (avg)",
            "quantity": 10,
            "unit": "km",
            "activity_date": "2026-06-17T10:00:00Z"
        }
    )
    response = client.get(
        "/footprint/summary?period=week",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_co2e_kg" in data
    assert "category_breakdown" in data
    assert data["category_breakdown"]["Transport"] > 0

def test_insights(client: TestClient, auth_token: str):
    response = client.get(
        "/insights",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

