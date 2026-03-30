import uuid
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Garage(Base):
    __tablename__ = "garages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)

    users = relationship("User", back_populates="garage")
    bookings = relationship("Booking", back_populates="garage")
    jobs = relationship("Job", back_populates="garage")