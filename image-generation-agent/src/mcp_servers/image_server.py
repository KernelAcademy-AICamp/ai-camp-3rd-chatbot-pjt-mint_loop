"""Image Generation MCP Server - DALL-E 3 기반 이미지 생성"""
import os
from typing import Any, Literal

import structlog
from fastmcp import FastMCP
from openai import AsyncOpenAI

logger = structlog.get_logger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP("ImageGenerationMCP")

# OpenAI 클라이언트 초기화
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@mcp.tool()
async def generate_image(
    prompt: str,
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
    quality: Literal["standard", "hd"] = "standard",
    style: Literal["vivid", "natural"] = "vivid"
) -> dict[str, Any]:
    """DALL-E 3를 사용하여 이미지 생성

    Args:
        prompt: 이미지 생성 프롬프트
        size: 이미지 크기 (1024x1024, 1792x1024, 1024x1792)
        quality: 이미지 품질 (standard, hd)
        style: 이미지 스타일 (vivid, natural)

    Returns:
        dict: 생성된 이미지 정보
            - url: 이미지 URL
            - revised_prompt: DALL-E가 수정한 프롬프트
            - metadata: 이미지 메타데이터
    """
    try:
        logger.info(f"Generating image with prompt: {prompt[:100]}...")
        logger.info(f"Settings - size: {size}, quality: {quality}, style: {style}")

        # DALL-E 3 API 호출
        response = await openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )

        image_data = response.data[0]

        result = {
            "url": image_data.url,
            "revised_prompt": image_data.revised_prompt,
            "metadata": {
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "style": style,
                "original_prompt": prompt
            }
        }

        logger.info(f"Image generated successfully: {result['url']}")
        return result

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {
            "url": None,
            "error": str(e),
            "metadata": {
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "style": style
            }
        }


@mcp.tool()
async def optimize_prompt_for_image(
    base_prompt: str,
    keywords: list[str],
    style_preferences: dict | None = None
) -> dict[str, Any]:
    """이미지 생성을 위한 프롬프트 최적화

    Args:
        base_prompt: 기본 프롬프트
        keywords: 추출된 키워드
        style_preferences: 스타일 선호도 (선택사항)

    Returns:
        dict: 최적화된 프롬프트
            - optimized_prompt: 최적화된 프롬프트
            - enhancements: 추가된 개선사항
    """
    try:
        # 키워드 통합
        keywords_str = ", ".join(keywords)

        # 스타일 설정 적용
        style_additions = []
        if style_preferences:
            if "art_style" in style_preferences:
                style_additions.append(f"{style_preferences['art_style']} style")
            if "mood" in style_preferences:
                style_additions.append(f"{style_preferences['mood']} mood")
            if "lighting" in style_preferences:
                style_additions.append(f"{style_preferences['lighting']} lighting")

        # 최적화된 프롬프트 구성
        components = [base_prompt, keywords_str] + style_additions
        optimized_prompt = ", ".join(filter(None, components))

        # 품질 향상 접미사 추가
        quality_suffix = "high quality, detailed, professional"
        final_prompt = f"{optimized_prompt}, {quality_suffix}"

        logger.info(f"Optimized prompt: {final_prompt}")

        return {
            "optimized_prompt": final_prompt,
            "enhancements": {
                "keywords_added": len(keywords),
                "style_additions": style_additions,
                "quality_enhancements": quality_suffix
            }
        }

    except Exception as e:
        logger.error(f"Prompt optimization failed: {e}")
        return {
            "optimized_prompt": base_prompt,
            "error": str(e)
        }


if __name__ == "__main__":
    # MCP 서버 실행
    mcp.run(transport="streamable_http", port=8051)
