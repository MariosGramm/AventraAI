from app.api.routes import login
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login")