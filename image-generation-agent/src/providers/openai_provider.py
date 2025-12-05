"""OpenAI DALL-E 3 Image Provider

OpenAI의 DALL-E 3 모델을 사용한 이미지 생성 프로바이더 구현
"""

from __future__ import annotations

from typing import Literal, Optional, List

import structlog
from openai import AsyncOpenAI

from .base import ImageGenerationParams, ImageGenerationResult, ImageProvider

logger = structlog.get_logger(__name__)

# DALL-E 3 지원 옵션
DALLE3_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
DALLE3_QUALITIES = ["standard", "hd"]
DALLE3_STYLES = ["vivid", "natural"]


class OpenAIProvider(ImageProvider):
    """OpenAI DALL-E 3 이미지 생성 프로바이더

    DALL-E 3 API를 사용하여 이미지를 생성합니다.
    클라이언트는 환경변수 OPENAI_xxx에서 자동으로 인증 정보를 읽습니다.

    Attributes:
        client: AsyncOpenAI 클라이언트
        model: 사용할 모델 이름 (기본: dall-e-3)

    Example:
        provider = OpenAIProvider()
        result = await provider.generate(ImageGenerationParams(
            prompt="A sunset over mountains",
            size="1024x1024"
        ))
    """

    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        model: str = "dall-e-3",
    ):
        """OpenAI 프로바이더 초기화

        Args:
            client: AsyncOpenAI 클라이언트 (None이면 환경변수에서 자동 생성)
            model: 사용할 모델 이름
        """
        # AsyncOpenAI()는 환경변수에서 자동으로 인증정보를 읽음
        self._client = client or AsyncOpenAI()
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_sizes(self) -> list[str]:
        return DALLE3_SIZES

    @property
    def supported_styles(self) -> list[str]:
        return DALLE3_STYLES

    @property
    def supported_qualities(self) -> list[str]:
        return DALLE3_QUALITIES

    def validate_params(
        self, params: ImageGenerationParams
    ) -> tuple:
        """DALL-E 3 전용 파라미터 검증"""
        # 기본 검증
        is_valid, error = super().validate_params(params)
        if not is_valid:
            return is_valid, error

        # 품질 검증
        if params.quality not in DALLE3_QUALITIES:
            return False, f"지원하지 않는 품질: {params.quality}. 지원: {DALLE3_QUALITIES}"

        return True, None

    async def generate(
        self, params: ImageGenerationParams
    ) -> ImageGenerationResult:
        """DALL-E 3로 이미지 생성

        Args:
            params: 이미지 생성 파라미터

        Returns:
            ImageGenerationResult: 생성 결과
        """
        # 파라미터 검증
        is_valid, error = self.validate_params(params)
        if not is_valid:
            return ImageGenerationResult.failure_result(
                error=error or "파라미터 검증 실패",
                provider=self.provider_name,
                metadata=params.to_dict(),
            )

        try:
            logger.info(
                "Generating image with DALL-E 3",
                prompt=params.prompt[:100],
                size=params.size,
                quality=params.quality,
                style=params.style,
            )

            # DALL-E 3 API 호출
            response = await self._client.images.generate(
                model=self._model,
                prompt=params.prompt,
                size=self._cast_size(params.size),
                quality=self._cast_quality(params.quality),
                style=self._cast_style(params.style),
                n=1,
            )

            image_data = response.data[0]

            logger.info(
                "Image generated successfully",
                url=image_data.url[:50] if image_data.url else None,
            )

            return ImageGenerationResult.success_result(
                url=image_data.url,
                provider=self.provider_name,
                revised_prompt=image_data.revised_prompt,
                metadata={
                    "model": self._model,
                    "size": params.size,
                    "quality": params.quality,
                    "style": params.style,
                    "original_prompt": params.prompt,
                },
            )

        except Exception as e:
            logger.error("Image generation failed", error=str(e))
            return ImageGenerationResult.failure_result(
                error=str(e),
                provider=self.provider_name,
                metadata={
                    "model": self._model,
                    "size": params.size,
                    "quality": params.quality,
                    "style": params.style,
                },
            )

    def _cast_size(
        self, size: str
    ) -> Literal["1024x1024", "1792x1024", "1024x1792"]:
        """크기를 DALL-E 3 타입으로 캐스트"""
        if size not in DALLE3_SIZES:
            return "1024x1024"
        return size  # type: ignore

    def _cast_quality(self, quality: str) -> Literal["standard", "hd"]:
        """품질을 DALL-E 3 타입으로 캐스트"""
        if quality not in DALLE3_QUALITIES:
            return "standard"
        return quality  # type: ignore

    def _cast_style(self, style: str) -> Literal["vivid", "natural"]:
        """스타일을 DALL-E 3 타입으로 캐스트"""
        if style not in DALLE3_STYLES:
            return "vivid"
        return style  # type: ignore
