import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "STAFF"
    garage_id: uuid.UUID


class GetUser(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    garage_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
