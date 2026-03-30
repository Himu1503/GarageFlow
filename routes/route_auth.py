from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from database import get_db
from models.customer import Customer
from models.garage import Garage
from models.user import User
from schemas.auth import (
    CustomerResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterCustomer,
    RegisterUser,
    TokenResponse,
    UserResponse,
)
from security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
VALID_ROLES = {"ADMIN", "MANAGER", "STAFF"}


def _build_token_response(subject: str, role: str, principal_type: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(subject=subject, role=role, principal_type=principal_type),
        refresh_token=create_refresh_token(subject=subject, role=role, principal_type=principal_type),
    )


@router.post("/register", response_model=UserResponse)
async def registerUser(payload: RegisterUser, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already exists")

    garage = db.get(Garage, payload.garage_id)
    if garage is None:
        raise HTTPException(status_code=400, detail="garage_id does not exist")

    role = payload.role.upper()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=role,
        garage_id=payload.garage_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def loginUser(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _build_token_response(subject=str(user.id), role=user.role, principal_type="USER")


@router.post("/customer/register", response_model=CustomerResponse)
async def registerCustomer(payload: RegisterCustomer, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(Customer.email == payload.email).first()
    if existing_customer is not None:
        raise HTTPException(status_code=400, detail="Email already exists")

    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/customer/login", response_model=TokenResponse)
async def loginCustomer(payload: LoginRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.email == payload.email).first()
    if customer is None or not customer.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify_password(payload.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _build_token_response(subject=str(customer.id), role="CUSTOMER", principal_type="CUSTOMER")


@router.post("/refresh", response_model=TokenResponse)
async def refreshTokens(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_payload = decode_token(payload.refresh_token)
    token_use = str(token_payload.get("token_use", "")).lower()
    if token_use != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    subject = token_payload.get("sub")
    role = str(token_payload.get("role", "")).upper()
    principal_type = str(token_payload.get("type", "USER")).upper()
    if not subject or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    try:
        principal_id = uuid.UUID(str(subject))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    if principal_type == "CUSTOMER":
        customer = db.get(Customer, principal_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return _build_token_response(subject=str(customer.id), role="CUSTOMER", principal_type="CUSTOMER")

    user = db.get(User, principal_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return _build_token_response(subject=str(user.id), role=user.role, principal_type="USER")
