"""이미지 생성 Agent의 워크플로우 노드 구현"""
import structlog
from langchain_core.messages import HumanMessage, AIMessage

from .state import ImageGenerationState

logger = structlog.get_logger(__name__)


async def extract_keywords_node(
    state: ImageGenerationState,
    search_tools: list
) -> ImageGenerationState:
    """키워드 추출 노드

    Search MCP의 extract_keywords 도구를 사용하여
    사용자 프롬프트에서 핵심 키워드를 추출합니다.
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
        result = await extract_tool.ainvoke({"user_prompt": user_prompt})

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
    state: ImageGenerationState,
    image_tools: list
) -> ImageGenerationState:
    """프롬프트 최적화 노드

    Image Generation MCP의 optimize_prompt_for_image 도구를 사용하여
    이미지 생성을 위한 프롬프트를 최적화합니다.
    """
    try:
        logger.info("Optimizing prompt for image generation")

        user_prompt = state["user_prompt"]
        keywords = state["extracted_keywords"]

        # Image MCP 도구 찾기
        optimize_tool = next(
            (tool for tool in image_tools if tool.name == "optimize_prompt_for_image"),
            None
        )

        if not optimize_tool:
            raise ValueError("optimize_prompt_for_image tool not found")

        # 프롬프트 최적화 실행
        result = await optimize_tool.ainvoke({
            "base_prompt": user_prompt,
            "keywords": keywords
        })

        optimized_prompt = result.get("optimized_prompt", user_prompt)

        logger.info(f"Optimized prompt: {optimized_prompt[:100]}...")

        # 메시지 추가
        state["messages"].append(
            AIMessage(content=f"프롬프트 최적화 완료")
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
    image_tools: list
) -> ImageGenerationState:
    """이미지 생성 노드

    Image Generation MCP의 generate_image 도구를 사용하여
    최적화된 프롬프트로 이미지를 생성합니다.
    """
    try:
        logger.info("Generating image")

        optimized_prompt = state["optimized_prompt"]

        # Image MCP 도구 찾기
        generate_tool = next(
            (tool for tool in image_tools if tool.name == "generate_image"),
            None
        )

        if not generate_tool:
            raise ValueError("generate_image tool not found")

        # 이미지 생성 실행
        result = await generate_tool.ainvoke({
            "prompt": optimized_prompt,
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid"
        })

        image_url = result.get("url")
        metadata = result.get("metadata", {})

        if not image_url:
            raise ValueError(f"Image generation failed: {result.get('error')}")

        logger.info(f"Image generated successfully: {image_url}")

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
