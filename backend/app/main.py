# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.db.session import engine
from app.api.v1.api import api_router
from app.websockets.endpoints import router as ws_router
# from app.models.user import User, Role
import app.models
from app.models.permission import Permission, RolePermission
from app.core.seed_db import seed_permissions, seed_admin_role, seed_default_admin_user

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)



app = FastAPI(
    title="RPi IoT Gateway",
    description="FastAPI + RF24 + React IoT System",
    version="1.0.0"
)

# 1. Setup CORS so your React app (usually on port 5173) can talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific IP of your Pi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Include REST API routes
app.include_router(api_router, prefix="/api/v1")

# 3. Include WebSocket routes
app.include_router(ws_router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Raspberry Pi IoT Gateway is running"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_permissions()
    seed_admin_role()
    seed_default_admin_user()