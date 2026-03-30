import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models.customer import Customer
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


def test_get_vehicle(client, mock_db, admin_user):
    vehicle_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    mock_db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=vehicle_id,
            customer_id=customer_id,
            registration_number="MH01AA1234",
        )
    ]

    response = client.get("/api/v1/vehicle")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(vehicle_id),
            "customer_id": str(customer_id),
            "registration_number": "MH01AA1234",
        }
    ]


def test_create_vehicle(client, mock_db, admin_user):
    vehicle_id = uuid.uuid4()
    customer_id = uuid.uuid4()

    def set_id(instance):
        instance.id = vehicle_id

    mock_db.refresh.side_effect = set_id
    mock_db.get.side_effect = lambda model, item_id: (
        SimpleNamespace(id=customer_id)
        if model is Customer and item_id == customer_id
        else None
    )

    response = client.post(
        "/api/v1/vehicle",
        json={
            "customer_id": str(customer_id),
            "registration_number": "MH01AA1234",
            "make": "BMW",
            "model": "X1",
            "year": 2020,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(vehicle_id),
        "customer_id": str(customer_id),
        "registration_number": "MH01AA1234",
    }


def test_create_vehicle_invalid_customer_id(client, mock_db, admin_user):
    customer_id = uuid.uuid4()
    mock_db.get.return_value = None

    response = client.post(
        "/api/v1/vehicle",
        json={
            "customer_id": str(customer_id),
            "registration_number": "MH01AA1234",
            "make": "BMW",
            "model": "X1",
            "year": 2020,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "customer_id does not exist"}


def test_create_vehicle_forbidden_for_staff(client, mock_db):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        response = client.post(
            "/api/v1/vehicle",
            json={
                "customer_id": str(uuid.uuid4()),
                "registration_number": "MH01AA1234",
                "make": "BMW",
                "model": "X1",
                "year": 2020,
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient role"}
