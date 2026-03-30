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
def staff_user():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="STAFF")
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_get_invoice_pdf(client, mock_db, staff_user, monkeypatch: pytest.MonkeyPatch):
    invoice_id = uuid.uuid4()
    invoice = SimpleNamespace(id=invoice_id)
    mock_db.query.return_value.filter.return_value.first.return_value = invoice

    class QueuedTask:
        id = "task-123"
        status = "PENDING"

    monkeypatch.setattr("routes.route_invoice.generate_invoice_pdf.delay", lambda _: QueuedTask())
    response = client.post(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 200
    assert response.json() == {
        "task_id": "task-123",
        "status": "PENDING",
        "status_url": "/api/v1/invoice/pdf/tasks/task-123",
        "download_url": "/api/v1/invoice/pdf/tasks/task-123/download",
    }


def test_get_invoice_pdf_not_found(client, mock_db, staff_user):
    invoice_id = uuid.uuid4()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.post(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}


def test_get_invoice_pdf_unauthorized(client, mock_db):
    invoice_id = uuid.uuid4()

    response = client.post(f"/api/v1/invoice/{invoice_id}/pdf")

    assert response.status_code == 401


def test_get_invoice_pdf_task_status(client, staff_user, monkeypatch: pytest.MonkeyPatch):
    class FakeAsyncResult:
        status = "SUCCESS"

        def failed(self):
            return False

    monkeypatch.setattr("routes.route_invoice.AsyncResult", lambda *_args, **_kwargs: FakeAsyncResult())

    response = client.get("/api/v1/invoice/pdf/tasks/task-123")

    assert response.status_code == 200
    assert response.json() == {"task_id": "task-123", "status": "SUCCESS"}


def test_download_invoice_pdf_task(client, staff_user, monkeypatch: pytest.MonkeyPatch):
    class FakeAsyncResult:
        status = "SUCCESS"
        result = {
            "filename": "invoice-123.pdf",
            "pdf_base64": "JVBERi0xLjQgdGVzdA==",
        }

    monkeypatch.setattr("routes.route_invoice.AsyncResult", lambda *_args, **_kwargs: FakeAsyncResult())

    response = client.get("/api/v1/invoice/pdf/tasks/task-123/download")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == 'attachment; filename="invoice-123.pdf"'
    assert response.content.startswith(b"%PDF-1.4")
