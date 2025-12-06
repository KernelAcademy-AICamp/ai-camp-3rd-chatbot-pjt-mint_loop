"""이미지 생성 Agent의 워크플로우 노드 구현

Google Gemini Imagen 모델을 사용합니다.
기본 모델: imagen-3.0-generate-002 (nano-banana)
"""
import json
import structlog
from langchain_core.messages import HumanMessage, AIMessage

from .state import ImageGenerationState
from ...providers import get_provider, ImageGenerationParams


# 기본 이미지 생성 모델
DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-002"


def parse_tool_result(result):
    """MCP 도구 결과를 파싱합니다. 문자열이면 JSON으로 파싱합니다."""
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result}
    return result


logger = structlog.get_logger(__name__)


async def extract_keywords_node(
    state: ImageGenerationState,
    search_tools: list
) -> ImageGenerationState:
    """키워드 추출 노드

    Search MCP의 extract_keywords 도구를 사용하여
    사용자 프롬프트에서 핵심 키워드를 추출합니다.

    Note: Search MCP는 유지 (RAG 및 다른 에이전트에서 재사용 가능)
    """
    try:
        logger.info("Extracting keywords from user prompt")

        user_prompt = state["user_prompt"]

        # Search MCP 도구 찾기
        extract_tool = next(
            (tool for tool in search_tools if tool.name == "extract_keywords"),
            None
        )

        if not extract_tool:
            raise ValueError("extract_keywords tool not found")

        # 키워드 추출 실행
        raw_result = await extract_tool.ainvoke({"user_prompt": user_prompt})
        result = parse_tool_result(raw_result)

        keywords = result.get("keywords", [])
        confidence = result.get("confidence", 0.0)

        logger.info(f"Extracted {len(keywords)} keywords with confidence {confidence}")

        # 메시지 추가
        state["messages"].append(
            AIMessage(content=f"키워드 추출 완료: {', '.join(keywords)}")
        )

        return {
            **state,
            "extracted_keywords": keywords,
            "status": "extracting"
        }

    except Exception as e:
        logger.error(f"Keyword extraction node failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }


async def optimize_prompt_node(
    state: ImageGenerationState
) -> ImageGenerationState:
    """프롬프트 최적화 노드

    키워드와 스타일 정보를 결합하여 이미지 생성에 최적화된 프롬프트를 생성합니다.

    리팩토링: Image MCP 대신 직접 로직 구현
    """
    try:
        logger.info("Optimizing prompt for image generation")

        user_prompt = state["user_prompt"]
        keywords = state["extracted_keywords"]

        # 키워드 통합
        keywords_str = ", ".join(keywords) if keywords else ""

        # 품질 향상 접미사
        quality_suffix = "high quality, detailed, professional"

        # 최적화된 프롬프트 구성
        components = [user_prompt, keywords_str, quality_suffix]
        optimized_prompt = ", ".join(filter(None, components))

        logger.info(f"Optimized prompt: {optimized_prompt[:100]}...")

        # 메시지 추가
        state["messages"].append(
            AIMessage(content="프롬프트 최적화 완료")
        )

        return {
            **state,
            "optimized_prompt": optimized_prompt,
            "status": "generating"
        }

    except Exception as e:
        logger.error(f"Prompt optimization node failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }


async def generate_image_node(
    state: ImageGenerationState,
    provider_type: str | None = None,
    image_model: str | None = None
) -> ImageGenerationState:
    """이미지 생성 노드
    providers 모듈을 직접 사용하여 이미지를 생성합니다.

    Args:
        state: 현재 상태
        provider_type: 사용할 프로바이더 (None이면 환경변수에서 결정, 기본: gemini)
        image_model: 사용할 이미지 모델 (None이면 기본값 사용)
    """
    try:
        # 모델 결정: 인자 > state > 기본값
        actual_model = (
            image_model
            or state.get("image_model")
            or DEFAULT_IMAGE_MODEL
        )

        logger.info(f"Generating image with model: {actual_model}")

        optimized_prompt = state["optimized_prompt"]

        # Provider 가져오기 (팩토리 패턴 사용)
        # 모델을 kwargs로 전달하여 GeminiProvider가 해당 모델 사용
        provider = get_provider(provider_type or "gemini", model=actual_model)
        logger.info(f"Using provider: {provider.provider_name}, model: {actual_model}")

        # 이미지 생성 파라미터
        params = ImageGenerationParams(
            prompt=optimized_prompt,
            size="1024x1024",
            quality="standard",
            style="vivid"
        )

        # 이미지 생성 실행
        result = await provider.generate(params)

        if not result.success:
            raise ValueError(f"Image generation failed: {result.error}")

        image_url = result.url
        metadata = {
            "provider": result.provider,
            "model": actual_model,
            "revised_prompt": result.revised_prompt,
            **result.metadata
        }

        logger.info(f"Image generated successfully: {image_url[:50] if image_url else 'N/A'}...")

        # 메시지 추가
        state["messages"].append(
            AIMessage(
                content=f"이미지 생성 완료!\n이미지 URL: {image_url}"
            )
        )

        return {
            **state,
            "generated_image_url": image_url,
            "image_metadata": metadata,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Image generation node failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }
