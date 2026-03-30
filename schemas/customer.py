import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateCustomer(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = Field(default=None)
    password: str


class GetCustomer(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    email: EmailStr | None

    model_config = ConfigDict(from_attributes=True)
