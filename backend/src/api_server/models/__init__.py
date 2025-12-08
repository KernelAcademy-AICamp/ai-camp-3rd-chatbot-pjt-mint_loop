"""Data models for API server."""
from .requests import (
    ChatContext,
    GenerateRequest,
    UserPreferences,
    RecommendationRequest,
    ChatMessage,
    RejectedItems,
    ChatRequest,
)
from .responses import (
    GenerateResponse,
    Activity,
    Destination,
    RecommendationResponse,
    ChatResponse,
)

__all__ = [
    # Requests
    "ChatContext",
    "GenerateRequest",
    "UserPreferences",
    "RecommendationRequest",
    "ChatMessage",
    "RejectedItems",
    "ChatRequest",
    # Responses
    "GenerateResponse",
    "Activity",
    "Destination",
    "RecommendationResponse",
    "ChatResponse",
]
