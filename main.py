from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from fastapi import Depends
from schemas.garage import CreateGarage, GetGarage
import models
from models.garage import Garage

from routes import route_garage
app = FastAPI()
app.include_router(route_garage.router)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def HealthCheck():
    return {"message" : "Hello World"}


