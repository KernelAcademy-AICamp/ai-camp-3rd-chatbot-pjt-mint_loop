"""Request models for API endpoints."""
from typing import Optional
from pydantic import BaseModel


class ChatContext(BaseModel):
    """Context collected from chat conversation."""
    city: Optional[str] = None
    spotName: Optional[str] = None
    mainAction: Optional[str] = None
    outfitStyle: Optional[str] = None
    posePreference: Optional[str] = None
    filmType: Optional[str] = None
    cameraModel: Optional[str] = None


class GenerateRequest(BaseModel):
    """Image generation request."""
    destination: str
    concept: str
    filmStock: str
    filmType: str = ""
    filmStyleDescription: str = ""
    outfitStyle: str = ""
    additionalPrompt: str = ""
    chatContext: Optional[ChatContext] = None
    conversationSummary: Optional[str] = None


class UserPreferences(BaseModel):
    """User travel preferences."""
    mood: Optional[str] = None
    aesthetic: Optional[str] = None
    duration: Optional[str] = None
    interests: list[str] = []


class RecommendationRequest(BaseModel):
    """Destination recommendation request."""
    preferences: UserPreferences
    concept: Optional[str] = None
    travelScene: Optional[str] = None
    travelDestination: Optional[str] = None


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str
    content: str


class RejectedItems(BaseModel):
    """Items rejected by user during conversation."""
    cities: list[str] = []
    spots: list[str] = []
    actions: list[str] = []
    concepts: list[str] = []
    outfits: list[str] = []
    poses: list[str] = []
    films: list[str] = []
    cameras: list[str] = []


class ChatRequest(BaseModel):
    """Chat conversation request."""
    message: str
    conversationHistory: list[ChatMessage] = []
    currentStep: str = "greeting"
    collectedData: Optional[dict] = None
    rejectedItems: Optional[RejectedItems] = None
