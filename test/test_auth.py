import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models.garage import Garage
from security import hash_password


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Base.metadata, "create_all", lambda *args, **kwargs: None)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield db
    finally:
        app.dependency_overrides.clear()


def test_register_user(client, mock_db):
    garage_id = uuid.uuid4()
    user_id = uuid.uuid4()

    def set_user_id(instance):
        instance.id = user_id

    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.get.side_effect = lambda model, item_id: (
        SimpleNamespace(id=garage_id) if model is Garage and item_id == garage_id else None
    )
    mock_db.refresh.side_effect = set_user_id

    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "secret123",
            "role": "ADMIN",
            "garage_id": str(garage_id),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user_id),
        "name": "Admin",
        "email": "admin@example.com",
        "role": "ADMIN",
        "garage_id": str(garage_id),
    }


def test_login_user(client, mock_db):
    user_id = uuid.uuid4()
    garage_id = uuid.uuid4()
    user = SimpleNamespace(
        id=user_id,
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("secret123"),
        role="ADMIN",
        garage_id=garage_id,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = user

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)
    assert response.json()["access_token"]
