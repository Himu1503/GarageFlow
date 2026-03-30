from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from fastapi import Depends
from schemas.garage import CreateGarage, GetGarage
import models
from models.garage import Garage

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def HealthCheck():
    return {"message" : "Hello World"}


@app.get("/garage", response_model=list[GetGarage])
async def getGarage(db:Session = Depends(get_db)):
    garage_entries = db.query(Garage).all()
    return garage_entries

@app.post("/garage", response_model=GetGarage)
async def createGarage(garage: CreateGarage, db:Session = Depends(get_db)):
    garage_entries = Garage(**garage.model_dump())
    db.add(garage_entries)
    db.commit()
    db.refresh(garage_entries)
    return garage_entries


