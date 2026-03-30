import uuid
from sqlalchemy import String, ForeignKey, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    garage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("garages.id"))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"))
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id"))

    service_type: Mapped[str] = mapped_column(String)
    booking_date: Mapped[str] = mapped_column(Date)
    time_slot: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String, default="PENDING")
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    garage = relationship("Garage", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")
    job = relationship("Job", back_populates="booking", uselist=False)