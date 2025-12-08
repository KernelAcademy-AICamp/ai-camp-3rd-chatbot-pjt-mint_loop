"""Recommendation endpoints."""
import structlog
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import RecommendationRequest, RecommendationResponse
from ...agents import RecommendationAgent

router = APIRouter(tags=["recommendations"])
logger = structlog.get_logger(__name__)
settings = get_settings()

# Agent instance
_recommendation_agent = RecommendationAgent(model=settings.TEXT_MODEL)


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
