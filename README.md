# GarageFlow API

GarageFlow is a FastAPI backend for managing garage operations: users, customers, vehicles, bookings, and auth.

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- JWT auth (`PyJWT`)
- Docker + Nginx reverse proxy
- Pytest

## Features

- JWT-based authentication (`register`, `login`)
- Role-based access control (`ADMIN`, `MANAGER`, `STAFF`)
- Protected routes for customer, user, booking, and vehicle operations
- Foreign-key validation for related entities
- CORS support via environment variable
- Reverse proxy support through Nginx

## Project Structure

- `main.py` - app setup, CORS, routers
- `models/` - SQLAlchemy models
- `schemas/` - Pydantic request/response schemas
- `routes/` - API route handlers
- `security.py` - password hashing, JWT, role dependencies
- `database.py` - DB engine/session config
- `test/` - API tests

## Local Development

1. Create `.env`:

   - `DATABASE_URL=postgresql+psycopg2://admin:admin@localhost:5432/garage_db`
   - `JWT_SECRET_KEY=<your-secret>`
   - `CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173`

2. Start Postgres (Docker):

   - `docker compose up -d postgres`

3. Run API:

   - `uv run fastapi dev`

4. Open docs:

   - `http://127.0.0.1:8000/docs`

## Docker + Reverse Proxy

Run full stack:

- `docker compose up --build`

Services:

- API behind Nginx: `http://localhost:8080`
- PostgreSQL: `localhost:5432`
- PgAdmin: `http://localhost:5050`

## Auth Flow

1. `POST /api/v1/auth/register` to create a user
2. `POST /api/v1/auth/login` to get bearer token
3. Send token in header:
   - `Authorization: Bearer <access_token>`

## Main Routes

- `GET /` - health check
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET/POST /api/v1/user` (ADMIN only)
- `GET/POST /api/v1/customer` (GET: all roles, POST: ADMIN/MANAGER)
- `GET/POST /api/v1/garage`
- `GET/POST /api/v1/vehicle` (GET: all roles, POST: ADMIN/MANAGER)
- `GET/POST /api/v1/booking` (GET: all roles, POST: ADMIN/MANAGER)

## Run Tests

- `pytest -q`
