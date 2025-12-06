"""Google Vertex AI Imagen Image Provider

Google Vertex AI의 Imagen 3 모델을 사용한 이미지 생성 프로바이더 구현

References:
    - https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images
    - https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api
"""

from __future__ import annotations

import base64
import os
from typing import Any, Optional, List

import structlog

from .base import ImageGenerationParams, ImageGenerationResult, ImageProvider

logger = structlog.get_logger(__name__)

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

# Vertex AI 설정
DEFAULT_VERTEX_PROJECT = os.getenv("VERTEX_PROJECT_ID", "tripkit-480413")
DEFAULT_VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")


class GeminiProvider(ImageProvider):
    """Google Vertex AI Imagen 이미지 생성 프로바이더

    Vertex AI의 Imagen 3 API를 사용하여 이미지를 생성합니다.
    GOOGLE_APPLICATION_CREDENTIALS 환경변수로 서비스 계정 인증을 사용합니다.

    Attributes:
        model: 사용할 모델 이름 (기본: imagen-3.0-generate-002)
        project: Google Cloud 프로젝트 ID
        location: Vertex AI 리전

    Example:
        provider = GeminiProvider()
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
        """Vertex AI Imagen 프로바이더 초기화

        Args:
            model: 사용할 모델 이름
            project: Google Cloud 프로젝트 ID (None이면 환경변수에서 가져옴)
            location: Vertex AI 리전 (None이면 환경변수에서 가져옴)
        """
        self._model = model
        self._project = project or DEFAULT_VERTEX_PROJECT
        self._location = location or DEFAULT_VERTEX_LOCATION
        self._client = None

        logger.info(
            "GeminiProvider initialized",
            model=self._model,
            project=self._project,
            location=self._location,
        )

    def _get_client(self):
        """Lazy initialization of Vertex AI client

        GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되어 있어야 합니다.
        """
        if self._client is None:
            try:
                from google import genai

                # Vertex AI 모드로 클라이언트 초기화
                # GOOGLE_APPLICATION_CREDENTIALS 환경변수를 자동으로 사용
                self._client = genai.Client(
                    vertexai=True,
                    project=self._project,
                    location=self._location,
                )
                logger.info(
                    "Vertex AI client initialized",
                    project=self._project,
                    location=self._location,
                )
            except ImportError:
                raise ImportError(
                    "google-genai 패키지가 필요합니다. "
                    "pip install google-genai 로 설치하세요."
                )
            except Exception as e:
                logger.error("Failed to initialize Vertex AI client", error=str(e))
                raise
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def supported_sizes(self) -> list[str]:
        """DALL-E 호환 크기 + Gemini aspect ratio"""
        return list(SIZE_TO_ASPECT_RATIO.keys())

    @property
    def supported_styles(self) -> list[str]:
        return IMAGEN_STYLES

    def normalize_size(self, size: str) -> str:
        """크기를 aspect_ratio로 변환"""
        return SIZE_TO_ASPECT_RATIO.get(size, "1:1")

    async def generate(
        self, params: ImageGenerationParams
    ) -> ImageGenerationResult:
        """Imagen 3로 이미지 생성

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

            # 스타일을 프롬프트에 추가
            enhanced_prompt = self._enhance_prompt_with_style(
                params.prompt, params.style
            )

            logger.info(
                "Generating image with Imagen 3",
                prompt=enhanced_prompt[:100],
                aspect_ratio=aspect_ratio,
                style=params.style,
            )

            # Imagen 3 API 호출
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

            # 이미지 데이터 처리
            image_data = result.generated_images[0]
            image_url = self._process_image_data(image_data)

            logger.info(
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
            logger.error("Image generation failed", error=str(e))
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
        """이미지 데이터를 URL로 변환

        Gemini는 이미지를 바이트 데이터로 반환하므로
        base64 data URL로 변환
        """
        try:
            # image_data.image.image_bytes 속성 확인
            if hasattr(image_data, 'image') and hasattr(image_data.image, 'image_bytes'):
                image_bytes = image_data.image.image_bytes
                b64_data = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/png;base64,{b64_data}"

            # 직접 바이트 데이터인 경우
            if hasattr(image_data, 'image_bytes'):
                image_bytes = image_data.image_bytes
                b64_data = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/png;base64,{b64_data}"

            logger.warning("Unknown image data format", type=type(image_data))
            return None

        except Exception as e:
            logger.error("Failed to process image data", error=str(e))
            return None
