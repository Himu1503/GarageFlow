import base64
import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from celery_app import celery_app
from database import get_db
from models.invoice import Invoice
from models.user import User
from security import require_roles
from tasks.invoice_tasks import generate_invoice_pdf

router = APIRouter(prefix="/api/v1/invoice", tags=["invoice"])


@router.post("/{invoice_id}/pdf")
async def queueInvoicePdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    task = generate_invoice_pdf.delay(str(invoice_id))
    return {
        "task_id": task.id,
        "status": task.status,
        "status_url": f"/api/v1/invoice/pdf/tasks/{task.id}",
        "download_url": f"/api/v1/invoice/pdf/tasks/{task.id}/download",
    }


@router.get("/pdf/tasks/{task_id}")
async def getInvoicePdfTask(
    task_id: str,
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.failed():
        return {"task_id": task_id, "status": task_result.status, "error": str(task_result.result)}
    return {"task_id": task_id, "status": task_result.status}


@router.get("/pdf/tasks/{task_id}/download")
async def downloadInvoicePdfTask(
    task_id: str,
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.status != "SUCCESS":
        raise HTTPException(status_code=409, detail=f"Task not ready. Current status: {task_result.status}")

    result = task_result.result
    if not isinstance(result, dict) or "pdf_base64" not in result:
        raise HTTPException(status_code=500, detail="Invalid task result")

    pdf_bytes = base64.b64decode(result["pdf_base64"].encode())
    filename = result.get("filename", "invoice.pdf")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
