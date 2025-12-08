"""OpenAI Provider Module

OpenAI API를 사용한 이미지 생성 및 LLM 텍스트 생성 Provider 구현
- OpenAIImageProvider: DALL-E 3 이미지 생성
- OpenAILLMProvider: GPT-4 텍스트 생성
"""

from __future__ import annotations

from typing import Literal, Optional

import structlog
from openai import AsyncOpenAI

from .base import (
    ImageProvider,
    ImageGenerationParams,
    ImageGenerationResult,
    LLMProvider,
    LLMGenerationParams,
    LLMGenerationResult,
)

logger = structlog.get_logger(__name__)

# =============================================================================
# 상수 정의
# =============================================================================

# DALL-E 3 지원 옵션
DALLE3_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
DALLE3_QUALITIES = ["standard", "hd"]
DALLE3_STYLES = ["vivid", "natural"]

# GPT 모델 목록
GPT_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]
DEFAULT_GPT_MODEL = "gpt-4o"


# =============================================================================
# OpenAI 클라이언트 싱글톤
# =============================================================================

_openai_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """OpenAI 클라이언트 싱글톤 반환

    환경변수 OPENAI_xxx에서 자동으로 인증 정보를 읽습니다.
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI()
    return _openai_client


# =============================================================================
# OpenAI Image Provider (DALL-E 3)
# =============================================================================

class OpenAIImageProvider(ImageProvider):
    """OpenAI DALL-E 3 이미지 생성 Provider

    DALL-E 3 API를 사용하여 이미지를 생성합니다.
    클라이언트는 환경변수에서 자동으로 인증 정보를 읽습니다.

    Example:
        provider = OpenAIImageProvider()
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
        """OpenAI Image Provider 초기화

        Args:
            client: AsyncOpenAI 클라이언트 (None이면 싱글톤 사용)
            model: 사용할 모델 이름
        """
        self._client = client or get_openai_client()
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

    def validate_params(self, params: ImageGenerationParams) -> tuple[bool, Optional[str]]:
        """DALL-E 3 전용 파라미터 검증"""
        is_valid, error = super().validate_params(params)
        if not is_valid:
            return is_valid, error

        if params.quality not in DALLE3_QUALITIES:
            return False, f"지원하지 않는 품질: {params.quality}. 지원: {DALLE3_QUALITIES}"

        return True, None

    async def generate(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """DALL-E 3로 이미지 생성"""
        is_valid, error = self.validate_params(params)
        if not is_valid:
            return ImageGenerationResult.failure_result(
                error=error or "파라미터 검증 실패",
                provider=self.provider_name,
                metadata=params.to_dict(),
            )

        try:
            self._log_info(
                "Generating image with DALL-E 3",
                prompt=params.prompt[:100],
                size=params.size,
                quality=params.quality,
                style=params.style,
            )

            response = await self._client.images.generate(
                model=self._model,
                prompt=params.prompt,
                size=self._cast_size(params.size),
                quality=self._cast_quality(params.quality),
                style=self._cast_style(params.style),
                n=1,
            )

            image_data = response.data[0]

            self._log_info(
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
            self._log_error("Image generation failed", error=str(e))
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

    def _cast_size(self, size: str) -> Literal["1024x1024", "1792x1024", "1024x1792"]:
        if size not in DALLE3_SIZES:
            return "1024x1024"
        return size  # type: ignore

    def _cast_quality(self, quality: str) -> Literal["standard", "hd"]:
        if quality not in DALLE3_QUALITIES:
            return "standard"
        return quality  # type: ignore

    def _cast_style(self, style: str) -> Literal["vivid", "natural"]:
        if style not in DALLE3_STYLES:
            return "vivid"
        return style  # type: ignore


# =============================================================================
# OpenAI LLM Provider (GPT-4)
# =============================================================================

class OpenAILLMProvider(LLMProvider):
    """OpenAI GPT LLM 텍스트 생성 Provider

    GPT-4/GPT-3.5 API를 사용하여 텍스트를 생성합니다.
    클라이언트는 환경변수에서 자동으로 인증 정보를 읽습니다.

    Example:
        provider = OpenAILLMProvider()
        result = await provider.generate(LLMGenerationParams(
            prompt="여행지 3곳을 추천해주세요",
            system_prompt="당신은 여행 전문가입니다",
            response_format="json"
        ))
    """

    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        model: str | None = None,
    ):
        """OpenAI LLM Provider 초기화

        Args:
            client: AsyncOpenAI 클라이언트 (None이면 싱글톤 사용)
            model: 사용할 모델 이름 (None이면 기본값 gpt-4o)
        """
        self._client = client or get_openai_client()
        self._model = model or DEFAULT_GPT_MODEL

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        return GPT_MODELS

    @property
    def default_model(self) -> str:
        return DEFAULT_GPT_MODEL

    @property
    def model(self) -> str:
        """현재 설정된 모델 반환"""
        return self._model

    async def generate(
        self,
        params: LLMGenerationParams,
        model: str | None = None,
    ) -> LLMGenerationResult:
        """GPT로 텍스트 생성

        Args:
            params: LLM 생성 파라미터
            model: 이 요청에서 사용할 모델 (선택, 인스턴스 기본값 오버라이드)

        Returns:
            LLMGenerationResult: 생성 결과
        """
        is_valid, error = self.validate_params(params)
        if not is_valid:
            return LLMGenerationResult.failure_result(
                error=error or "파라미터 검증 실패",
                provider=self.provider_name,
                metadata=params.to_dict(),
            )

        actual_model = model or self._model

        try:
            self._log_info(
                "Generating text with GPT",
                model=actual_model,
                prompt_length=len(params.prompt),
                has_system_prompt=bool(params.system_prompt),
                response_format=params.response_format,
            )

            # 메시지 구성
            messages = []
            if params.system_prompt:
                messages.append({"role": "system", "content": params.system_prompt})
            messages.append({"role": "user", "content": params.prompt})

            # API 호출 파라미터
            api_params = {
                "model": actual_model,
                "messages": messages,
                "temperature": params.temperature,
            }

            if params.max_tokens:
                api_params["max_tokens"] = params.max_tokens

            # JSON 응답 형식 설정
            if params.response_format == "json":
                api_params["response_format"] = {"type": "json_object"}

            # API 호출
            response = await self._client.chat.completions.create(**api_params)

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None

            self._log_info(
                "Text generated successfully",
                model=actual_model,
                content_length=len(content) if content else 0,
                total_tokens=usage.get("total_tokens") if usage else None,
            )

            return LLMGenerationResult.success_result(
                content=content,
                provider=self.provider_name,
                usage=usage,
                metadata={
                    "model": actual_model,
                    "temperature": params.temperature,
                    "response_format": params.response_format,
                },
            )

        except Exception as e:
            self._log_error("Text generation failed", error=str(e), model=actual_model)
            return LLMGenerationResult.failure_result(
                error=str(e),
                provider=self.provider_name,
                metadata={
                    "model": actual_model,
                    "temperature": params.temperature,
                },
            )


# =============================================================================
# 하위 호환성을 위한 별칭
# =============================================================================

# 기존 코드 호환성
OpenAIProvider = OpenAIImageProvider
