"""
API routes module
"""
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.chat import router as chat_router

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Include agents routes
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])

# Include chat routes
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
