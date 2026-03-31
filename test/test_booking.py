import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models.customer import Customer
from models.garage import Garage
from models.vehicle import Vehicle
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


def test_get_booking(client, mock_db, admin_user):
    booking_id = uuid.uuid4()
    garage_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    vehicle_id = uuid.uuid4()
    booking_day = date(2026, 3, 30)

    mock_db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=booking_id,
            garage_id=garage_id,
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            service_type="General Service",
            booking_date=booking_day,
            time_slot="10:00 AM",
            status="PENDING",
            notes="Check brakes",
        )
    ]

    response = client.get("/api/v1/booking")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(booking_id),
            "garage_id": str(garage_id),
            "customer_id": str(customer_id),
            "vehicle_id": str(vehicle_id),
            "service_type": "General Service",
            "booking_date": "2026-03-30",
            "time_slot": "10:00 AM",
            "status": "PENDING",
            "notes": "Check brakes",
        }
    ]


def test_create_booking(client, mock_db, admin_user):
    booking_id = uuid.uuid4()
    garage_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    vehicle_id = uuid.uuid4()

    def set_id(instance):
        instance.id = booking_id

    mock_db.refresh.side_effect = set_id
    mock_db.get.side_effect = lambda model, item_id: (
        SimpleNamespace(id=garage_id)
        if model is Garage and item_id == garage_id
        else SimpleNamespace(id=customer_id)
        if model is Customer and item_id == customer_id
        else SimpleNamespace(id=vehicle_id, customer_id=customer_id)
        if model is Vehicle and item_id == vehicle_id
        else None
    )

    response = client.post(
        "/api/v1/booking",
        json={
            "garage_id": str(garage_id),
            "customer_id": str(customer_id),
            "vehicle_id": str(vehicle_id),
            "service_type": "General Service",
            "booking_date": "2026-03-30",
            "time_slot": "10:00 AM",
            "status": "PENDING",
            "notes": "Check brakes",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(booking_id),
        "garage_id": str(garage_id),
        "customer_id": str(customer_id),
        "vehicle_id": str(vehicle_id),
        "service_type": "General Service",
        "booking_date": "2026-03-30",
        "time_slot": "10:00 AM",
        "status": "PENDING",
        "notes": "Check brakes",
    }


def test_create_booking_invalid_vehicle_id(client, mock_db, admin_user):
    garage_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    vehicle_id = uuid.uuid4()

    mock_db.get.side_effect = lambda model, item_id: (
        SimpleNamespace(id=garage_id)
        if model is Garage and item_id == garage_id
        else SimpleNamespace(id=customer_id)
        if model is Customer and item_id == customer_id
        else None
    )

    response = client.post(
        "/api/v1/booking",
        json={
            "garage_id": str(garage_id),
            "customer_id": str(customer_id),
            "vehicle_id": str(vehicle_id),
            "service_type": "General Service",
            "booking_date": "2026-03-30",
            "time_slot": "10:00 AM",
            "status": "PENDING",
            "notes": "Check brakes",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "vehicle_id does not exist"}


def test_create_booking_forbidden_for_staff(client, mock_db):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        response = client.post(
            "/api/v1/booking",
            json={
                "garage_id": str(uuid.uuid4()),
                "customer_id": str(uuid.uuid4()),
                "vehicle_id": str(uuid.uuid4()),
                "service_type": "General Service",
                "booking_date": "2026-03-30",
                "time_slot": "10:00 AM",
                "status": "PENDING",
                "notes": "Check brakes",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient role"}


def test_update_booking(client, mock_db, admin_user):
    booking_id = uuid.uuid4()
    garage_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    vehicle_id = uuid.uuid4()
    booking_day = date(2026, 4, 1)
    booking = SimpleNamespace(
        id=booking_id,
        garage_id=garage_id,
        customer_id=customer_id,
        vehicle_id=vehicle_id,
        service_type="Old Service",
        booking_date=booking_day,
        time_slot="09:00 AM",
        status="PENDING",
        notes="Old note",
    )

    mock_db.get.side_effect = lambda model, item_id: (
        booking
        if model.__name__ == "Booking" and item_id == booking_id
        else SimpleNamespace(id=garage_id)
        if model.__name__ == "Garage" and item_id == garage_id
        else SimpleNamespace(id=customer_id)
        if model.__name__ == "Customer" and item_id == customer_id
        else SimpleNamespace(id=vehicle_id, customer_id=customer_id)
        if model.__name__ == "Vehicle" and item_id == vehicle_id
        else None
    )

    response = client.put(
        f"/api/v1/booking/{booking_id}",
        json={
            "garage_id": str(garage_id),
            "customer_id": str(customer_id),
            "vehicle_id": str(vehicle_id),
            "service_type": "General Service",
            "booking_date": "2026-04-01",
            "time_slot": "10:00 AM",
            "status": "CONFIRMED",
            "notes": "Updated note",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(booking_id),
        "garage_id": str(garage_id),
        "customer_id": str(customer_id),
        "vehicle_id": str(vehicle_id),
        "service_type": "General Service",
        "booking_date": "2026-04-01",
        "time_slot": "10:00 AM",
        "status": "CONFIRMED",
        "notes": "Updated note",
    }


def test_delete_booking(client, mock_db, admin_user):
    booking_id = uuid.uuid4()
    mock_db.get.return_value = SimpleNamespace(id=booking_id)

    response = client.delete(f"/api/v1/booking/{booking_id}")

    assert response.status_code == 200
    assert response.json() == {"detail": "Booking deleted"}
