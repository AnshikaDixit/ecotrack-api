import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_create_goal(client: TestClient, auth_token: str):
    now = datetime.utcnow()
    end = now + timedelta(days=30)
    response = client.post(
        "/goals",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Reduce transport emissions",
            "target_reduction_percent": 10.0,
            "baseline_co2e_kg": 100.0,
            "period_start": now.isoformat(),
            "period_end": end.isoformat()
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Reduce transport emissions"
    assert data["status"] == "active"

def test_list_goals(client: TestClient, auth_token: str):
    now = datetime.utcnow()
    client.post(
        "/goals",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Reduce transport emissions",
            "target_reduction_percent": 10.0,
            "baseline_co2e_kg": 100.0,
            "period_start": now.isoformat(),
            "period_end": (now + timedelta(days=30)).isoformat()
        }
    )
    response = client.get(
        "/goals",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_goal(client: TestClient, auth_token: str):
    now = datetime.utcnow()
    client.post(
        "/goals",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Reduce transport emissions",
            "target_reduction_percent": 10.0,
            "baseline_co2e_kg": 100.0,
            "period_start": now.isoformat(),
            "period_end": (now + timedelta(days=30)).isoformat()
        }
    )
    
    # Get goal ID
    response = client.get(
        "/goals",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    goal_id = response.json()[0]["id"]
    
    update_response = client.patch(
        f"/goals/{goal_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "status": "completed"
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"
