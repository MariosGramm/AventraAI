from app.api.routes import auth, chat, login, payments, travel, users
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login")
api_router.include_router(travel.router, prefix="/travel")
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(payments.router, prefix="/payments")