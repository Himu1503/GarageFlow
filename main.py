from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from sqlalchemy import text
import models

from routes import route_booking
from routes import route_auth
from routes import route_customer
from routes import route_garage
from routes import route_invoice
from routes import route_user
from routes import route_vehicle

@asynccontextmanager
async def lifespan(_: FastAPI):
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS password_hash VARCHAR")
        )
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

cors_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
)
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(route_auth.router)
app.include_router(route_garage.router)
app.include_router(route_booking.router)
app.include_router(route_customer.router)
app.include_router(route_vehicle.router)
app.include_router(route_user.router)
app.include_router(route_invoice.router)
@app.get("/")
async def HealthCheck():
    return {"message" : "Hello World"}
