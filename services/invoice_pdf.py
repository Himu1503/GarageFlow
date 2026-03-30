import io
from html import escape

from xhtml2pdf import pisa

from models.invoice import Invoice


def build_invoice_html(invoice: Invoice) -> str:
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


def render_invoice_pdf(invoice: Invoice) -> bytes:
    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(build_invoice_html(invoice), dest=pdf_buffer)
    if result.err:
        raise ValueError("Failed to generate invoice PDF")
    return pdf_buffer.getvalue()
