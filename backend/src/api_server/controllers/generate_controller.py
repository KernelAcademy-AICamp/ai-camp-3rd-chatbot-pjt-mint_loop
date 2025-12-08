"""Image generation endpoint."""
import structlog
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import GenerateRequest, GenerateResponse
from ..services import TranslationService, PromptBuilder
from ..utils.errors import convert_to_user_error
from ...providers import get_provider, ImageGenerationParams
from ...providers.gemini_provider import GeminiLLMProvider

router = APIRouter(tags=["generate"])
logger = structlog.get_logger(__name__)
settings = get_settings()

# Service instances
_llm_provider = GeminiLLMProvider(model=settings.CHAT_MODEL)
_translation = TranslationService(_llm_provider)
_prompt_builder = PromptBuilder()


@router.post("/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest):
    """Generate image from request."""
    try:
        logger.info(
            "Generate request",
            destination=request.destination,
            concept=request.concept,
        )

        # Collect fields for translation
        fields = _collect_translatable_fields(request)
        translated = await _translation.translate_fields(fields)

        # Build prompt
        prompt = _prompt_builder.build(request, translated)
        logger.info("Built prompt", length=len(prompt))

        # Generate image
        provider = get_provider("gemini", model=settings.IMAGE_MODEL)
        params = ImageGenerationParams(
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            style="natural"
        )

        result = await provider.generate(params)

        if result.success:
            return GenerateResponse(
                status="success",
                imageUrl=result.url,
                optimizedPrompt=prompt,
                extractedKeywords=_extract_keywords(request),
                poseUsed=request.additionalPrompt or "auto-generated",
                metadata={
                    "concept": request.concept,
                    "filmStock": request.filmStock,
                    "destination": request.destination,
                    "provider": result.provider,
                    "model": settings.IMAGE_MODEL,
                }
            )

        return GenerateResponse(
            status="error",
            error=convert_to_user_error(result.error or "Unknown error")
        )

    except Exception as e:
        logger.error("Generate error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


def _collect_translatable_fields(request: GenerateRequest) -> dict[str, str]:
    """Collect fields that may need translation."""
    fields = {}

    if request.destination:
        fields['destination'] = request.destination
    if request.additionalPrompt:
        fields['additionalPrompt'] = request.additionalPrompt
    if request.outfitStyle:
        fields['outfitStyle'] = request.outfitStyle

    ctx = request.chatContext
    if ctx:
        if ctx.city:
            fields['city'] = ctx.city
        if ctx.spotName:
            fields['spotName'] = ctx.spotName
        if ctx.mainAction:
            fields['mainAction'] = ctx.mainAction
        if ctx.outfitStyle:
            fields['chatOutfitStyle'] = ctx.outfitStyle
        if ctx.posePreference:
            fields['posePreference'] = ctx.posePreference

    return fields


def _extract_keywords(request: GenerateRequest) -> list[str]:
    """Extract keywords from request."""
    keywords = [
        request.destination,
        request.concept,
        request.filmType,
        request.filmStock,
    ]
    if request.additionalPrompt:
        keywords.extend(request.additionalPrompt.split()[:5])

    return [k for k in keywords if k]
