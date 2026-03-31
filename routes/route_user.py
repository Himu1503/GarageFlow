from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from database import get_db
from models.garage import Garage
from models.user import User
from schemas.user import CreateUser, GetUser
from security import hash_password, require_roles

router = APIRouter(prefix="/api/v1/user", tags=["user"])
VALID_ROLES = {"ADMIN", "MANAGER", "STAFF"}


@router.get("", response_model=list[GetUser])
async def getUser(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
):
    user_entries = db.query(User).all()
    return user_entries


@router.post("", response_model=GetUser)
async def createUser(
    user: CreateUser,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already exists")

    garage = db.get(Garage, user.garage_id)
    if garage is None:
        raise HTTPException(status_code=400, detail="garage_id does not exist")

    role = user.role.upper()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_entry = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=role,
        garage_id=user.garage_id,
    )
    db.add(user_entry)
    db.commit()
    db.refresh(user_entry)
    return user_entry


@router.put("/{user_id}", response_model=GetUser)
async def updateUser(
    user_id: uuid.UUID,
    user: CreateUser,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
):
    user_entry = db.get(User, user_id)
    if user_entry is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user is not None and existing_user.id != user_id:
        raise HTTPException(status_code=400, detail="Email already exists")

    garage = db.get(Garage, user.garage_id)
    if garage is None:
        raise HTTPException(status_code=400, detail="garage_id does not exist")

    role = user.role.upper()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_entry.name = user.name
    user_entry.email = user.email
    user_entry.password_hash = hash_password(user.password)
    user_entry.role = role
    user_entry.garage_id = user.garage_id
    db.commit()
    db.refresh(user_entry)
    return user_entry


@router.delete("/{user_id}")
async def deleteUser(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
):
    user_entry = db.get(User, user_id)
    if user_entry is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user_entry)
    db.commit()
    return {"detail": "User deleted"}
