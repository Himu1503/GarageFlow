import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import get_db
from main import app


@pytest.fixture
def client():
    startup_handlers = list(app.router.on_startup)
    app.router.on_startup.clear()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.router.on_startup[:] = startup_handlers


@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield db
    finally:
        app.dependency_overrides.clear()


def test_get_garage(client, mock_db):
    garage_id = uuid.uuid4()
    mock_db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=garage_id,
            name="Test Garage",
            email="test@example.com",
            address="123 Main St",
            phone="1234567890",
        )
    ]

    response = client.get("/api/v1/garage")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(garage_id),
            "email": "test@example.com",
            "address": "123 Main St",
            "phone": "1234567890",
        }
    ]


def test_create_garage(client, mock_db):
    garage_id = uuid.uuid4()

    def set_id(instance):
        instance.id = garage_id

    mock_db.refresh.side_effect = set_id

    response = client.post(
        "/api/v1/garage",
        json={
            "name": "Test Garage",
            "email": "test@example.com",
            "address": "123 Main St",
            "phone": "1234567890",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(garage_id),
        "email": "test@example.com",
        "address": "123 Main St",
        "phone": "1234567890",
    }