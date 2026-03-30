import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models.garage import Garage
from security import get_current_user


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


@pytest.fixture
def admin_user():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="ADMIN")
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_get_user(client, mock_db, admin_user):
    user_id = uuid.uuid4()
    garage_id = uuid.uuid4()
    mock_db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=user_id,
            name="Staff",
            email="staff@example.com",
            role="STAFF",
            garage_id=garage_id,
        )
    ]

    response = client.get("/api/v1/user")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(user_id),
            "name": "Staff",
            "email": "staff@example.com",
            "role": "STAFF",
            "garage_id": str(garage_id),
        }
    ]


def test_create_user(client, mock_db, admin_user):
    user_id = uuid.uuid4()
    garage_id = uuid.uuid4()

    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.get.side_effect = lambda model, item_id: (
        SimpleNamespace(id=garage_id) if model is Garage and item_id == garage_id else None
    )

    def set_user_id(instance):
        instance.id = user_id

    mock_db.refresh.side_effect = set_user_id

    response = client.post(
        "/api/v1/user",
        json={
            "name": "Staff",
            "email": "staff@example.com",
            "password": "secret123",
            "role": "STAFF",
            "garage_id": str(garage_id),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user_id),
        "name": "Staff",
        "email": "staff@example.com",
        "role": "STAFF",
        "garage_id": str(garage_id),
    }


def test_get_user_forbidden_for_staff(client, mock_db):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        response = client.get("/api/v1/user")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient role"}
