from pydantic import BaseModel, ConfigDict
import uuid

class CreateVehicle(BaseModel):
    customer_id: uuid.UUID
    registration_number: str
    make: str
    model: str
    year: int

class GetVehicle(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    registration_number: str