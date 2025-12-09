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
    """Stream destination recommendations one by one via SSE."""

    async def generate():
        try:
            logger.info(
                "Streaming recommendations request",
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
            destinations = result.get("destinations", [])

            logger.info("Streaming recommendations", count=len(destinations))

            # Stream each destination as SSE event - 각 yield 후 즉시 flush
            for i, destination in enumerate(destinations):
                event_data = {
                    "type": "destination",
                    "index": i,
                    "total": len(destinations),
                    "destination": destination,
                    "isFallback": result.get("is_fallback", False),
                }
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                # 즉시 flush를 위해 event loop에 제어권 양보
                await asyncio.sleep(0)

            # Send completion event
            complete_data = {
                "type": "complete",
                "total": len(destinations),
                "userProfile": result.get("user_profile"),
                "isFallback": result.get("is_fallback", False),
            }
            yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"
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
