from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.garage import Garage
from models.user import User
from schemas.auth import LoginRequest, RegisterUser, TokenResponse, UserResponse
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
VALID_ROLES = {"ADMIN", "MANAGER", "STAFF"}


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

    token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(access_token=token)
