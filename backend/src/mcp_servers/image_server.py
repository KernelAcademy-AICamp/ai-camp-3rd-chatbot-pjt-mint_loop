"""Image Generation MCP Server - Multi-Provider 이미지 생성

OpenAI DALL-E 3, Google Gemini Imagen 등 다양한 프로바이더 지원
"""

from __future__ import annotations

import os
from typing import Any, Literal, Optional

from pathlib import Path
from dotenv import load_dotenv

# .env 파일을 현재 디렉토리 및 상위 디렉토리에서 검색
def find_and_load_dotenv():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).resolve().parent
    for _ in range(5):  # Check up to 5 parent directories
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True
        current = current.parent
    # Fallback to default behavior
    load_dotenv()
    return False

find_and_load_dotenv()

import structlog
from fastmcp import FastMCP

from ..providers import get_provider, ImageGenerationParams, list_providers

logger = structlog.get_logger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP("ImageGenerationMCP")


@mcp.tool()
async def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: Literal["standard", "hd"] = "standard",
    style: Literal["vivid", "natural"] = "vivid",
    provider: Optional[str] = None,
) -> dict:
    """다양한 프로바이더를 사용하여 이미지 생성

    Args:
        prompt: 이미지 생성 프롬프트
        size: 이미지 크기 (OpenAI: 1024x1024 등, Gemini: 1:1 등)
        quality: 이미지 품질 (standard, hd)
        style: 이미지 스타일 (vivid, natural)
        provider: 사용할 프로바이더 (openai, gemini, None=환경변수)

    Returns:
        dict: 생성된 이미지 정보
            - url: 이미지 URL
            - revised_prompt: 수정된 프롬프트
            - metadata: 이미지 메타데이터
    """
    try:
        # 프로바이더 가져오기
        image_provider = get_provider(provider)

        logger.info(
            "Generating image",
            provider=image_provider.provider_name,
            prompt=prompt[:100],
            size=size,
            quality=quality,
            style=style,
        )

        # 파라미터 생성
        params = ImageGenerationParams(
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
        )

        # 이미지 생성
        result = await image_provider.generate(params)

        if result.success:
            logger.info(
                "Image generated successfully",
                provider=result.provider,
                url=result.url[:50] if result.url else None,
            )
        else:
            logger.error(
                "Image generation failed",
                provider=result.provider,
                error=result.error,
            )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {
            "url": None,
            "error": str(e),
            "metadata": {
                "size": size,
                "quality": quality,
                "style": style,
            }
        }


@mcp.tool()
async def list_available_providers() -> dict:
    """사용 가능한 이미지 생성 프로바이더 목록

    Returns:
        dict: 프로바이더 정보
            - providers: 사용 가능한 프로바이더 목록
            - default: 기본 프로바이더
    """
    providers = list_providers()
    default = os.getenv("IMAGE_PROVIDER", "openai")

    return {
        "providers": providers,
        "default": default,
        "provider_info": {
            "openai": {
                "name": "OpenAI DALL-E 3",
                "supported_sizes": ["1024x1024", "1792x1024", "1024x1792"],
                "supported_styles": ["vivid", "natural"],
            },
            "gemini": {
                "name": "Google Imagen 3",
                "supported_sizes": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                "supported_styles": ["vivid", "natural"],
            },
        }
    }


@mcp.tool()
async def optimize_prompt_for_image(
    base_prompt: str,
    keywords: list,
    style_preferences: Optional[dict] = None
) -> dict:
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
    # MCP 서버 실행 (0.0.0.0으로 바인딩하여 Docker 네트워크에서 접근 가능)
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8051)
