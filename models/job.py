import uuid
from sqlalchemy import String, ForeignKey, Text, DECIMAL, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    garage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("garages.id"))
    assigned_to: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)

    status: Mapped[str] = mapped_column(String, default="PENDING")
    description: Mapped[str] = mapped_column(Text)

    estimated_cost: Mapped[float] = mapped_column(DECIMAL)
    actual_cost: Mapped[float] = mapped_column(DECIMAL)

    started_at: Mapped[str] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[str] = mapped_column(DateTime, nullable=True)

    booking = relationship("Booking", back_populates="job")
    garage = relationship("Garage", back_populates="jobs")
    assigned_user = relationship("User", back_populates="jobs")
    invoice = relationship("Invoice", back_populates="job", uselist=False)