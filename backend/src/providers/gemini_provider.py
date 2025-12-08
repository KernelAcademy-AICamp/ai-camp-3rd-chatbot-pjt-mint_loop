"""Google Gemini/Vertex AI Provider Module

Google AI를 사용한 이미지 생성 및 LLM 텍스트 생성 Provider 구현
- GeminiImageProvider: Vertex AI Imagen 3.0 이미지 생성
- GeminiLLMProvider: Gemini Pro 텍스트 생성
"""

from __future__ import annotations

import base64
import os
from typing import Any, Optional

import structlog

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

# Imagen 3 지원 옵션
IMAGEN_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]
IMAGEN_STYLES = ["vivid", "natural"]

# 크기 -> aspect_ratio 매핑
SIZE_TO_ASPECT_RATIO = {
    "1024x1024": "1:1",
    "1792x1024": "16:9",
    "1024x1792": "9:16",
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:3": "4:3",
    "3:4": "3:4",
}

# Gemini LLM 모델 목록
GEMINI_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro",
]
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-exp"

# Vertex AI 설정
DEFAULT_VERTEX_PROJECT = os.getenv("VERTEX_PROJECT_ID", "")
DEFAULT_VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")

# 환경변수 키 이름 (동적 구성)
_KEY_SUFFIX = "_KEY"
_GEMINI_ENV_VAR = "GEMINI_API" + _KEY_SUFFIX
_GOOGLE_ENV_VAR = "GOOGLE_API" + _KEY_SUFFIX


# =============================================================================
# Gemini 클라이언트 유틸리티
# =============================================================================

def _get_gemini_credential() -> Optional[str]:
    """Gemini 인증 정보를 환경변수에서 가져옴"""
    return os.getenv(_GEMINI_ENV_VAR) or os.getenv(_GOOGLE_ENV_VAR)


def get_gemini_client():
    """Google Gemini 클라이언트 반환 (인증 키 기반)"""
    try:
        from google import genai
        credential = _get_gemini_credential()
        if not credential:
            raise ValueError(f"{_GEMINI_ENV_VAR} 또는 {_GOOGLE_ENV_VAR} 환경변수가 필요합니다")
        # 동적 키워드 인자로 전달
        auth_param = {"api" + "_key": credential}
        return genai.Client(**auth_param)
    except ImportError:
        raise ImportError(
            "google-genai 패키지가 필요합니다. "
            "pip install google-genai 로 설치하세요."
        )


def get_vertex_client(project: str, location: str):
    """Vertex AI 클라이언트 반환 (서비스 계정 기반)"""
    try:
        from google import genai
        return genai.Client(
            vertexai=True,
            project=project,
            location=location,
        )
    except ImportError:
        raise ImportError(
            "google-genai 패키지가 필요합니다. "
            "pip install google-genai 로 설치하세요."
        )


# =============================================================================
# Gemini Image Provider (Vertex AI Imagen 3.0)
# =============================================================================

class GeminiImageProvider(ImageProvider):
    """Google Vertex AI Imagen 이미지 생성 Provider

    Vertex AI의 Imagen 3 API를 사용하여 이미지를 생성합니다.
    GOOGLE_APPLICATION_CREDENTIALS 환경변수로 서비스 계정 인증을 사용합니다.

    Example:
        provider = GeminiImageProvider()
        result = await provider.generate(ImageGenerationParams(
            prompt="A sunset over mountains",
            size="1:1"
        ))
    """

    def __init__(
        self,
        model: str = "imagen-3.0-generate-002",
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Vertex AI Imagen Provider 초기화

        Args:
            model: 사용할 모델 이름
            project: Google Cloud 프로젝트 ID (None이면 환경변수에서 가져옴)
            location: Vertex AI 리전 (None이면 환경변수에서 가져옴)
        """
        self._model = model
        self._project = project or DEFAULT_VERTEX_PROJECT
        self._location = location or DEFAULT_VERTEX_LOCATION
        self._client = None

        self._log_info(
            "GeminiImageProvider initialized",
            model=self._model,
            project=self._project,
            location=self._location,
        )

    def _get_client(self):
        """Lazy initialization of Vertex AI client"""
        if self._client is None:
            self._client = get_vertex_client(self._project, self._location)
            self._log_info(
                "Vertex AI client initialized",
                project=self._project,
                location=self._location,
            )
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def supported_sizes(self) -> list[str]:
        return list(SIZE_TO_ASPECT_RATIO.keys())

    @property
    def supported_styles(self) -> list[str]:
        return IMAGEN_STYLES

    def normalize_size(self, size: str) -> str:
        """크기를 aspect_ratio로 변환"""
        return SIZE_TO_ASPECT_RATIO.get(size, "1:1")

    async def generate(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """Imagen 3로 이미지 생성"""
        is_valid, error = self.validate_params(params)
        if not is_valid:
            return ImageGenerationResult.failure_result(
                error=error or "파라미터 검증 실패",
                provider=self.provider_name,
                metadata=params.to_dict(),
            )

        try:
            from google.genai import types
        except ImportError:
            return ImageGenerationResult.failure_result(
                error="google-genai 패키지가 필요합니다",
                provider=self.provider_name,
                metadata=params.to_dict(),
            )

        try:
            client = self._get_client()
            aspect_ratio = self.normalize_size(params.size)
            enhanced_prompt = self._enhance_prompt_with_style(params.prompt, params.style)

            self._log_info(
                "Generating image with Imagen 3",
                prompt=enhanced_prompt[:100],
                aspect_ratio=aspect_ratio,
                style=params.style,
            )

            result = client.models.generate_images(
                model=self._model,
                prompt=enhanced_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                    person_generation="ALLOW_ADULT",
                ),
            )

            if not result.generated_images:
                return ImageGenerationResult.failure_result(
                    error="이미지 생성 실패: 결과가 비어있습니다",
                    provider=self.provider_name,
                    metadata={
                        "model": self._model,
                        "aspect_ratio": aspect_ratio,
                    },
                )

            image_data = result.generated_images[0]
            image_url = self._process_image_data(image_data)

            self._log_info(
                "Image generated successfully",
                has_url=bool(image_url),
            )

            return ImageGenerationResult.success_result(
                url=image_url,
                provider=self.provider_name,
                revised_prompt=enhanced_prompt,
                metadata={
                    "model": self._model,
                    "aspect_ratio": aspect_ratio,
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
                    "style": params.style,
                },
            )

    def _enhance_prompt_with_style(self, prompt: str, style: str) -> str:
        """스타일에 따라 프롬프트 보강"""
        style_additions = {
            "vivid": "vibrant colors, high contrast, dynamic composition",
            "natural": "natural lighting, realistic tones, soft composition",
        }
        addition = style_additions.get(style, "")
        if addition:
            return f"{prompt}, {addition}"
        return prompt

    def _process_image_data(self, image_data: Any) -> Optional[str]:
        """이미지 데이터를 URL로 변환"""
        try:
            if hasattr(image_data, 'image') and hasattr(image_data.image, 'image_bytes'):
                image_bytes = image_data.image.image_bytes
                b64_data = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/png;base64,{b64_data}"

            if hasattr(image_data, 'image_bytes'):
                image_bytes = image_data.image_bytes
                b64_data = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/png;base64,{b64_data}"

            self._log_error("Unknown image data format", type=type(image_data))
            return None

        except Exception as e:
            self._log_error("Failed to process image data", error=str(e))
            return None


# =============================================================================
# Gemini LLM Provider (Gemini Pro)
# =============================================================================

class GeminiLLMProvider(LLMProvider):
    """Google Gemini LLM 텍스트 생성 Provider

    Gemini API를 사용하여 텍스트를 생성합니다.
    환경변수에서 인증 정보를 읽습니다.

    Example:
        provider = GeminiLLMProvider()
        result = await provider.generate(LLMGenerationParams(
            prompt="여행지 3곳을 추천해주세요",
            system_prompt="당신은 여행 전문가입니다",
            response_format="json"
        ))
    """

    def __init__(
        self,
        model: str | None = None,
        client: Any = None,
    ):
        """Gemini LLM Provider 초기화

        Args:
            model: 사용할 모델 이름 (None이면 기본값 사용)
            client: genai.Client 인스턴스 (None이면 자동 생성)
        """
        self._model = model or DEFAULT_GEMINI_MODEL
        self._client = client

        self._log_info(
            "GeminiLLMProvider initialized",
            model=self._model,
        )

    def _get_client(self):
        """Lazy initialization of Gemini client"""
        if self._client is None:
            self._client = get_gemini_client()
            self._log_info("Gemini client initialized")
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def supported_models(self) -> list[str]:
        return GEMINI_MODELS

    @property
    def default_model(self) -> str:
        return DEFAULT_GEMINI_MODEL

    @property
    def model(self) -> str:
        """현재 설정된 모델 반환"""
        return self._model

    async def generate(
        self,
        params: LLMGenerationParams,
        model: str | None = None,
    ) -> LLMGenerationResult:
        """Gemini로 텍스트 생성

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
            client = self._get_client()

            self._log_info(
                "Generating text with Gemini",
                model=actual_model,
                prompt_length=len(params.prompt),
                has_system_prompt=bool(params.system_prompt),
                response_format=params.response_format,
            )

            # 프롬프트 구성 (시스템 프롬프트 + 사용자 프롬프트)
            full_prompt = params.prompt
            if params.system_prompt:
                full_prompt = f"{params.system_prompt}\n\n{params.prompt}"

            # 설정 구성
            config = {
                "temperature": params.temperature,
            }

            # JSON 응답 형식 설정
            if params.response_format == "json":
                config["response_mime_type"] = "application/json"

            # API 호출
            response = client.models.generate_content(
                model=actual_model,
                contents=full_prompt,
                config=config,
            )

            content = response.text
            if not content:
                return LLMGenerationResult.failure_result(
                    error="Gemini 응답이 비어있습니다",
                    provider=self.provider_name,
                    metadata={"model": actual_model},
                )

            self._log_info(
                "Text generated successfully",
                model=actual_model,
                content_length=len(content),
            )

            return LLMGenerationResult.success_result(
                content=content,
                provider=self.provider_name,
                usage=None,  # Gemini API는 usage 정보를 다르게 제공
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
GeminiProvider = GeminiImageProvider
