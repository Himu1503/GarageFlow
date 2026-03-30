import uuid
from sqlalchemy import ForeignKey, DECIMAL, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))

    total_amount: Mapped[float] = mapped_column(DECIMAL)
    tax: Mapped[float] = mapped_column(DECIMAL)
    discount: Mapped[float] = mapped_column(DECIMAL)

    payment_status: Mapped[str] = mapped_column(String, default="UNPAID")

    issued_at: Mapped[str] = mapped_column(DateTime)
    paid_at: Mapped[str] = mapped_column(DateTime, nullable=True)

    job = relationship("Job", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice")