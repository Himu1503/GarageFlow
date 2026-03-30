import io
import uuid
from html import escape

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from xhtml2pdf import pisa

from database import get_db
from models.invoice import Invoice
from models.user import User
from security import require_roles

router = APIRouter(prefix="/api/v1/invoice", tags=["invoice"])


def _invoice_html(invoice: Invoice) -> str:
    rows = []
    for item in invoice.items:
        rows.append(
            "<tr>"
            f"<td>{escape(item.description)}</td>"
            f"<td>{item.quantity}</td>"
            f"<td>{item.unit_price}</td>"
            f"<td>{item.total_price}</td>"
            "</tr>"
        )

    rows_html = "".join(rows)
    return f"""
    <html>
      <body>
        <h1>Invoice</h1>
        <p><strong>Invoice ID:</strong> {invoice.id}</p>
        <p><strong>Job ID:</strong> {invoice.job_id}</p>
        <p><strong>Status:</strong> {escape(invoice.payment_status)}</p>
        <p><strong>Issued At:</strong> {invoice.issued_at}</p>
        <h2>Items</h2>
        <table border="1" cellpadding="4" cellspacing="0">
          <tr>
            <th>Description</th>
            <th>Quantity</th>
            <th>Unit Price</th>
            <th>Total Price</th>
          </tr>
          {rows_html}
        </table>
        <h2>Summary</h2>
        <p><strong>Tax:</strong> {invoice.tax}</p>
        <p><strong>Discount:</strong> {invoice.discount}</p>
        <p><strong>Total Amount:</strong> {invoice.total_amount}</p>
      </body>
    </html>
    """


@router.get("/{invoice_id}/pdf")
async def getInvoicePdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(_invoice_html(invoice), dest=pdf_buffer)
    if result.err:
        raise HTTPException(status_code=500, detail="Failed to generate invoice PDF")

    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="invoice-{invoice.id}.pdf"'},
    )
