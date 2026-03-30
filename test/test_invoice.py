import io
import uuid
from datetime import datetime
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
def staff_user():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_get_invoice_pdf(client, mock_db, staff_user, monkeypatch: pytest.MonkeyPatch):
    invoice_id = uuid.uuid4()
    invoice = SimpleNamespace(
        id=invoice_id,
        job_id=uuid.uuid4(),
        payment_status="UNPAID",
        issued_at=datetime(2026, 3, 30, 10, 0, 0),
        tax=10,
        discount=5,
        total_amount=105,
        items=[
            SimpleNamespace(description="Oil Change", quantity=1, unit_price=100, total_price=100),
        ],
    )
    mock_db.query.return_value.filter.return_value.first.return_value = invoice

    class Result:
        err = 0

    def fake_create_pdf(html: str, dest: io.BytesIO):
        dest.write(b"%PDF-1.4 test")
        return Result()

    monkeypatch.setattr("routes.route_invoice.pisa.CreatePDF", fake_create_pdf)

    response = client.get(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f'attachment; filename="invoice-{invoice_id}.pdf"'
    assert response.content.startswith(b"%PDF-1.4")


def test_get_invoice_pdf_not_found(client, mock_db, staff_user):
    invoice_id = uuid.uuid4()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.get(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}


def test_get_invoice_pdf_unauthorized(client, mock_db):
    invoice_id = uuid.uuid4()

    response = client.get(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 401
