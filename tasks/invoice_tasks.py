import base64
import uuid

import models  # noqa: F401
from celery_app import celery_app
from database import SessionLocal
from models.invoice import Invoice
from services.invoice_pdf import render_invoice_pdf


@celery_app.task(name="tasks.generate_invoice_pdf")
def generate_invoice_pdf(invoice_id: str) -> dict:
    session = SessionLocal()
    try:
        parsed_id = uuid.UUID(invoice_id)
        invoice = session.query(Invoice).filter(Invoice.id == parsed_id).first()
        if invoice is None:
            raise ValueError("Invoice not found")

        pdf_bytes = render_invoice_pdf(invoice)
        return {
            "invoice_id": str(invoice.id),
            "filename": f"invoice-{invoice.id}.pdf",
            "pdf_base64": base64.b64encode(pdf_bytes).decode(),
        }
    finally:
        session.close()
