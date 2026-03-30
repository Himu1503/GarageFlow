import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class CreateBooking(BaseModel):
    garage_id: uuid.UUID
    customer_id: uuid.UUID
    vehicle_id: uuid.UUID
    service_type: str
    booking_date: date
    time_slot: str
    status: str = "PENDING"
    notes: str | None = None


class GetBooking(BaseModel):
    id: uuid.UUID
    garage_id: uuid.UUID
    customer_id: uuid.UUID
    vehicle_id: uuid.UUID
    service_type: str
    booking_date: date
    time_slot: str
    status: str
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
