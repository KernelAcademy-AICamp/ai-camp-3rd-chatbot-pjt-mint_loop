"""API Controllers."""
from .health_controller import router as health_router
from .generate_controller import router as generate_router
from .chat_controller import router as chat_router
from .recommendation_controller import router as recommendation_router

__all__ = [
    "health_router",
    "generate_router",
    "chat_router",
    "recommendation_router",
]
