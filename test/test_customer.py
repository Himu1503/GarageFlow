import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
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


def test_get_customer(client, mock_db, admin_user):
    customer_id = uuid.uuid4()
    mock_db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=customer_id,
            name="Alice",
            phone="9998887777",
            email="alice@example.com",
        )
    ]

    response = client.get("/api/v1/customer")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(customer_id),
            "name": "Alice",
            "phone": "9998887777",
            "email": "alice@example.com",
        }
    ]


def test_create_customer(client, mock_db, admin_user):
    customer_id = uuid.uuid4()

    def set_id(instance):
        instance.id = customer_id

    mock_db.refresh.side_effect = set_id

    response = client.post(
        "/api/v1/customer",
        json={
            "name": "Alice",
            "phone": "9998887777",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(customer_id),
        "name": "Alice",
        "phone": "9998887777",
        "email": "alice@example.com",
    }


def test_create_customer_forbidden_for_staff(client, mock_db):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        response = client.post(
            "/api/v1/customer",
            json={
                "name": "Alice",
                "phone": "9998887777",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient role"}
