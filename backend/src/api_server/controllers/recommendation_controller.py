"""Recommendation endpoints."""
import asyncio
import json
import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..config import get_settings
from ..models import RecommendationRequest, RecommendationResponse
from ...agents import RecommendationAgent

router = APIRouter(tags=["recommendations"])
logger = structlog.get_logger(__name__)
settings = get_settings()

# Agent instance
_recommendation_agent = RecommendationAgent(
    model=settings.RECOMMENDATION_MODEL,
    provider_type=settings.RECOMMENDATION_PROVIDER
)


@router.post("/recommendations/destinations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get destination recommendations."""
    try:
        logger.info(
            "Recommendations request",
            mood=request.preferences.mood,
            concept=request.concept
        )

        input_data = {
            "preferences": {
                "mood": request.preferences.mood,
                "aesthetic": request.preferences.aesthetic,
                "duration": request.preferences.duration,
                "interests": request.preferences.interests,
            },
            "concept": request.concept,
            "travel_scene": request.travelScene,
            "travel_destination": request.travelDestination,
        }

        result = await _recommendation_agent.recommend(input_data)

        logger.info("Recommendations generated", count=len(result['destinations']))

        return RecommendationResponse(
            status=result["status"],
            destinations=result["destinations"],
            userProfile=result.get("user_profile"),
            isFallback=result.get("is_fallback", False),
        )

    except Exception as e:
        logger.error("Recommendations error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/destinations/stream")
async def stream_recommendations(request: RecommendationRequest):
    """Stream destination recommendations via SSE with 2-phase delivery.

    Phase 1: LLM 응답 후 즉시 초기 3개 여행지 전송 (빠른 응답)
    Phase 2: Google Places API enrichment 후 enriched 버전 3개 추가 전송

    클라이언트는 총 6개의 destination을 받게 됩니다.
    """

    async def generate():
        try:
            logger.info(
                "Streaming recommendations request (2-phase)",
                mood=request.preferences.mood,
                concept=request.concept
            )

            input_data = {
                "preferences": {
                    "mood": request.preferences.mood,
                    "aesthetic": request.preferences.aesthetic,
                    "duration": request.preferences.duration,
                    "interests": request.preferences.interests,
                },
                "concept": request.concept,
                "travel_scene": request.travelScene,
                "travel_destination": request.travelDestination,
                "image_generation_context": {
                    "destination": request.imageGenerationContext.destination if request.imageGenerationContext else None,
                    "additionalPrompt": request.imageGenerationContext.additionalPrompt if request.imageGenerationContext else None,
                    "filmStock": request.imageGenerationContext.filmStock if request.imageGenerationContext else None,
                    "outfitStyle": request.imageGenerationContext.outfitStyle if request.imageGenerationContext else None,
                } if request.imageGenerationContext else None,
            }

            # 2단계 스트리밍 사용
            async for event in _recommendation_agent.recommend_stream(input_data):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                # 즉시 flush를 위해 event loop에 제어권 양보
                await asyncio.sleep(0)

        except Exception as e:
            logger.error("Streaming recommendations error", error=str(e))
            error_data = {
                "type": "error",
                "error": str(e),
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
