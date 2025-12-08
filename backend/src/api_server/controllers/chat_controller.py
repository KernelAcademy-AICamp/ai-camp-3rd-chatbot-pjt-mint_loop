"""Chat endpoint."""
import structlog
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import ChatRequest, ChatResponse
from ..services import ChatService
from ...providers.gemini_provider import GeminiLLMProvider

router = APIRouter(tags=["chat"])
logger = structlog.get_logger(__name__)
settings = get_settings()

# Service instance
_llm_provider = GeminiLLMProvider(model=settings.CHAT_MODEL)
_chat_service = ChatService(_llm_provider)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message."""
    try:
        logger.info(
            "Chat request",
            message=request.message[:50],
            step=request.currentStep
        )

        response = await _chat_service.process(request)

        logger.info("Chat response", next_step=response.nextStep)
        return response

    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
