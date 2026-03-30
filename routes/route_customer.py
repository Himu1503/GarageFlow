from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.customer import Customer
from schemas.customer import CreateCustomer, GetCustomer
from security import hash_password, require_roles
from models.user import User

router = APIRouter(prefix="/api/v1/customer", tags=["customer"])


@router.get("", response_model=list[GetCustomer])
async def getCustomer(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    customer_entries = db.query(Customer).all()
    return customer_entries


@router.post("", response_model=GetCustomer)
async def createCustomer(
    customer: CreateCustomer,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    customer_entry = Customer(
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        password_hash=hash_password(customer.password),
    )
    db.add(customer_entry)
    db.commit()
    db.refresh(customer_entry)
    return customer_entry
