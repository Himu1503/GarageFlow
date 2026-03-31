import uuid

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Response
from database import get_db
from schemas.garage import CreateGarage, GetGarage
from models.garage import Garage
from services.cache import delete_key, get_json, set_json

router = APIRouter(prefix="/api/v1/garage", tags=["garage"])
CACHE_KEY_GARAGE_LIST = "gf:v1:garage:list"


@router.get("", response_model = list[GetGarage])
async def getGarage(response: Response, db: Session = Depends(get_db)):
    cached = get_json(CACHE_KEY_GARAGE_LIST)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    garage_entries = db.query(Garage).all()
    serialized = [GetGarage.model_validate(item).model_dump(mode="json") for item in garage_entries]
    set_json(CACHE_KEY_GARAGE_LIST, serialized)
    response.headers["X-Cache"] = "MISS"
    return serialized

@router.post("", response_model = GetGarage)
async def createGarage(garage: CreateGarage, db:Session = Depends(get_db)):
    garage_entries = Garage(**garage.model_dump())
    db.add(garage_entries)
    db.commit()
    db.refresh(garage_entries)
    delete_key(CACHE_KEY_GARAGE_LIST)
    return garage_entries


@router.put("/{garage_id}", response_model=GetGarage)
async def updateGarage(garage_id: uuid.UUID, garage: CreateGarage, db: Session = Depends(get_db)):
    garage_entry = db.get(Garage, garage_id)
    if garage_entry is None:
        raise HTTPException(status_code=404, detail="Garage not found")

    garage_entry.name = garage.name
    garage_entry.email = garage.email
    garage_entry.address = garage.address
    garage_entry.phone = garage.phone
    db.commit()
    db.refresh(garage_entry)
    delete_key(CACHE_KEY_GARAGE_LIST)
    return garage_entry


@router.delete("/{garage_id}")
async def deleteGarage(garage_id: uuid.UUID, db: Session = Depends(get_db)):
    garage_entry = db.get(Garage, garage_id)
    if garage_entry is None:
        raise HTTPException(status_code=404, detail="Garage not found")

    db.delete(garage_entry)
    db.commit()
    delete_key(CACHE_KEY_GARAGE_LIST)
    return {"detail": "Garage deleted"}