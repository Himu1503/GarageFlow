from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from schemas.garage import CreateGarage, GetGarage
from models.garage import Garage

router = APIRouter(prefix="/api/v1/garage", tags=["garage"])


@router.get("", response_model = list[GetGarage])
async def getGarage(db:Session = Depends(get_db)):
    garage_entries = db.query(Garage).all()
    return garage_entries

@router.post("", response_model = GetGarage)
async def createGarage(garage: CreateGarage, db:Session = Depends(get_db)):
    garage_entries = Garage(**garage.model_dump())
    db.add(garage_entries)
    db.commit()
    db.refresh(garage_entries)
    return garage_entries