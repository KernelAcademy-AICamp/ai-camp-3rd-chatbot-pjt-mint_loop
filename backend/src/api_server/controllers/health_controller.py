"""Health check endpoints."""
from fastapi import APIRouter

from ..config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "service": "Trip Kit Image Generation API",
        "version": "2.2.0"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.IMAGE_PROVIDER,
        "models": {
            "text": settings.TEXT_MODEL,
            "chat": settings.CHAT_MODEL,
            "image": settings.IMAGE_MODEL,
        }
    }
