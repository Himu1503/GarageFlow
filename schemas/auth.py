import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    garage_id: uuid.UUID
    role: str = "STAFF"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    garage_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
