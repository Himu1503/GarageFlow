import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from database import get_db
from models.customer import Customer
from schemas.customer import CreateCustomer, GetCustomer
from security import hash_password, require_roles
from models.user import User
from services.cache import delete_key, get_json, set_json

router = APIRouter(prefix="/api/v1/customer", tags=["customer"])
CACHE_KEY_CUSTOMER_LIST = "gf:v1:customer:list"


@router.get("", response_model=list[GetCustomer])
async def getCustomer(
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    cached = get_json(CACHE_KEY_CUSTOMER_LIST)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    customer_entries = db.query(Customer).all()
    serialized = [GetCustomer.model_validate(item).model_dump(mode="json") for item in customer_entries]
    set_json(CACHE_KEY_CUSTOMER_LIST, serialized)
    response.headers["X-Cache"] = "MISS"
    return serialized


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
    delete_key(CACHE_KEY_CUSTOMER_LIST)
    return customer_entry


@router.put("/{customer_id}", response_model=GetCustomer)
async def updateCustomer(
    customer_id: uuid.UUID,
    customer: CreateCustomer,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    customer_entry = db.get(Customer, customer_id)
    if customer_entry is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_entry.name = customer.name
    customer_entry.phone = customer.phone
    customer_entry.email = customer.email
    customer_entry.password_hash = hash_password(customer.password)
    db.commit()
    db.refresh(customer_entry)
    delete_key(CACHE_KEY_CUSTOMER_LIST)
    return customer_entry


@router.delete("/{customer_id}")
async def deleteCustomer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    customer_entry = db.get(Customer, customer_id)
    if customer_entry is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer_entry)
    db.commit()
    delete_key(CACHE_KEY_CUSTOMER_LIST)
    return {"detail": "Customer deleted"}
