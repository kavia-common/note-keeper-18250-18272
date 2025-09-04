# note-keeper-18250-18272

Backend service: FastAPI Notes API

How to run locally:
- Create a virtual environment and install requirements from notes_backend/requirements.txt
- Copy notes_backend/.env.example to notes_backend/.env and update secrets
- Start the server:
  uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --app-dir notes_backend

API Overview:
- POST /auth/register -> Register a new user
- POST /auth/login -> Login and receive a bearer token
- CRUD under /notes requires Authorization: Bearer <token>
- GET / -> Health check

OpenAPI docs available at /docs when running.