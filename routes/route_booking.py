from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.booking import Booking
from models.customer import Customer
from models.garage import Garage
from models.user import User
from models.vehicle import Vehicle
from schemas.booking import CreateBooking, GetBooking
from security import require_roles

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


@router.get("", response_model=list[GetBooking])
async def getBooking(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER", "STAFF")),
):
    booking_entries = db.query(Booking).all()
    return booking_entries


@router.post("", response_model=GetBooking)
async def createBooking(
    booking: CreateBooking,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    garage = db.get(Garage, booking.garage_id)
    if garage is None:
        raise HTTPException(status_code=400, detail="garage_id does not exist")

    customer = db.get(Customer, booking.customer_id)
    if customer is None:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    vehicle = db.get(Vehicle, booking.vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=400, detail="vehicle_id does not exist")

    if vehicle.customer_id != booking.customer_id:
        raise HTTPException(status_code=400, detail="vehicle does not belong to customer_id")

    booking_entry = Booking(**booking.model_dump())
    db.add(booking_entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="invalid booking data")
    db.refresh(booking_entry)
    return booking_entry
