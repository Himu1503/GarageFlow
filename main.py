from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from fastapi import Depends
from schemas.garage import CreateGarage, GetGarage
import models
from models.garage import Garage

from routes import route_garage


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(route_garage.router)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def HealthCheck():
    return {"message" : "Hello World"}


