import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CreateGarage(BaseModel):
    name : str
    email: EmailStr | None = Field(default=None)
    address: str
    phone: str

class GetGarage(BaseModel):
    id: uuid.UUID
    email: EmailStr
    address: str
    phone: str
    model_config = ConfigDict(from_attributes=True)
