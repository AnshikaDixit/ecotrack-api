import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, pool
from app.main import app
from app.db.database import get_session
from app.core.rate_limit import limiter

limiter.enabled = False

sqlite_url = "sqlite:///:memory:"
engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool
)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

import app.db.database as db
import app.db.seed_emission_factors as seeder

db.engine = engine
seeder.engine = engine

@pytest.fixture(name="client")
def client_fixture():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="auth_token")
def fixture_auth_token(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": f"test_{id(client)}@example.com", "password": "password", "region": "IN"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": f"test_{id(client)}@example.com", "password": "password"}
    )
    return login_response.json()["access_token"]
