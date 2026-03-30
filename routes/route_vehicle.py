from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from models.customer import Customer
from models.user import User
from models.vehicle import Vehicle
from schemas.vehicle import CreateVehicle, GetVehicle
from security import require_roles

router = APIRouter(prefix="/api/v1/vehicle", tags=["vehicle"])

@router.get("", response_model=list[GetVehicle])
async def getVehicle(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    vehicle_entries = db.query(Vehicle).all()
    return vehicle_entries

@router.post("", response_model=GetVehicle)
async def createVehicle(
    vehicle: CreateVehicle,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    customer = db.get(Customer, vehicle.customer_id)
    if customer is None:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    vehicle_entry = Vehicle(**vehicle.model_dump())
    db.add(vehicle_entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="invalid vehicle data")
    db.refresh(vehicle_entry)
    return vehicle_entry