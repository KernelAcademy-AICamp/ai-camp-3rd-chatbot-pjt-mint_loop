"""Provider Base Module

Strategy Pattern 기반의 Provider 추상화 레이어
- BaseProvider: 모든 Provider의 최상위 추상 클래스
- ImageProvider: 이미지 생성 Provider
- LLMProvider: 텍스트/LLM 생성 Provider
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ProviderType(str, Enum):
    """Provider 타입 열거형"""
    IMAGE = "image"
    LLM = "llm"


# =============================================================================
# 공통 데이터 클래스
# =============================================================================

@dataclass
class BaseParams:
    """모든 Provider 파라미터의 기본 클래스"""
    extra_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환"""
        result = {}
        for key, value in self.__dict__.items():
            if key == "extra_params":
                result.update(value)
            else:
                result[key] = value
        return result


@dataclass
class BaseResult:
    """모든 Provider 결과의 기본 클래스"""
    success: bool
    error: Optional[str]
    metadata: dict
    provider: str

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "success": self.success,
            "error": self.error,
            "metadata": {
                **self.metadata,
                "provider": self.provider,
            },
        }


# =============================================================================
# 이미지 생성 데이터 클래스
# =============================================================================

@dataclass
class ImageGenerationParams(BaseParams):
    """이미지 생성 파라미터

    Attributes:
        prompt: 이미지 생성 프롬프트
        size: 이미지 크기 (예: "1024x1024")
        quality: 이미지 품질 (예: "standard", "hd")
        style: 이미지 스타일 (예: "vivid", "natural")
    """
    prompt: str = ""
    size: str = "1024x1024"
    quality: str = "standard"
    style: str = "vivid"

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "size": self.size,
            "quality": self.quality,
            "style": self.style,
            **self.extra_params,
        }


@dataclass
class ImageGenerationResult(BaseResult):
    """이미지 생성 결과

    Attributes:
        url: 생성된 이미지 URL (실패 시 None)
        revised_prompt: 프로바이더가 수정한 프롬프트 (지원하는 경우)
    """
    url: Optional[str] = None
    revised_prompt: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "revised_prompt": self.revised_prompt,
            "error": self.error,
            "metadata": {
                **self.metadata,
                "provider": self.provider,
            },
        }

    @classmethod
    def success_result(
        cls,
        url: str,
        provider: str,
        revised_prompt: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ImageGenerationResult:
        """성공 결과 생성 헬퍼"""
        return cls(
            success=True,
            url=url,
            revised_prompt=revised_prompt,
            error=None,
            metadata=metadata or {},
            provider=provider,
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        provider: str,
        metadata: Optional[dict] = None,
    ) -> ImageGenerationResult:
        """실패 결과 생성 헬퍼"""
        return cls(
            success=False,
            url=None,
            revised_prompt=None,
            error=error,
            metadata=metadata or {},
            provider=provider,
        )


# =============================================================================
# LLM 텍스트 생성 데이터 클래스
# =============================================================================

@dataclass
class LLMGenerationParams(BaseParams):
    """LLM 텍스트 생성 파라미터

    Attributes:
        prompt: 사용자 프롬프트
        system_prompt: 시스템 프롬프트 (선택)
        temperature: 생성 온도 (0.0 ~ 2.0)
        max_tokens: 최대 토큰 수
        response_format: 응답 형식 ("text", "json")
    """
    prompt: str = ""
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    response_format: str = "text"

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
            **self.extra_params,
        }


@dataclass
class LLMGenerationResult(BaseResult):
    """LLM 텍스트 생성 결과

    Attributes:
        content: 생성된 텍스트 (실패 시 None)
        usage: 토큰 사용량 정보
    """
    content: Optional[str] = None
    usage: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "usage": self.usage,
            "error": self.error,
            "metadata": {
                **self.metadata,
                "provider": self.provider,
            },
        }

    @classmethod
    def success_result(
        cls,
        content: str,
        provider: str,
        usage: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> LLMGenerationResult:
        """성공 결과 생성 헬퍼"""
        return cls(
            success=True,
            content=content,
            usage=usage,
            error=None,
            metadata=metadata or {},
            provider=provider,
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        provider: str,
        metadata: Optional[dict] = None,
    ) -> LLMGenerationResult:
        """실패 결과 생성 헬퍼"""
        return cls(
            success=False,
            content=None,
            usage=None,
            error=error,
            metadata=metadata or {},
            provider=provider,
        )


# =============================================================================
# 추상 Provider 클래스
# =============================================================================

class BaseProvider(ABC):
    """모든 Provider의 최상위 추상 클래스

    Strategy Pattern의 Strategy 인터페이스 역할.
    모든 Provider가 공통으로 구현해야 하는 인터페이스 정의.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """프로바이더 식별자 반환

        Returns:
            str: 프로바이더 고유 이름 (예: "openai", "gemini")
        """
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """프로바이더 타입 반환

        Returns:
            ProviderType: IMAGE 또는 LLM
        """
        pass

    def _log_info(self, message: str, **kwargs) -> None:
        """로깅 헬퍼 (서브클래스에서 오버라이드 가능)"""
        import structlog
        logger = structlog.get_logger(self.__class__.__name__)
        logger.info(message, **kwargs)

    def _log_error(self, message: str, **kwargs) -> None:
        """에러 로깅 헬퍼"""
        import structlog
        logger = structlog.get_logger(self.__class__.__name__)
        logger.error(message, **kwargs)


class ImageProvider(BaseProvider):
    """이미지 생성 Provider 추상 클래스

    이미지 생성 프로바이더가 구현해야 하는 인터페이스 정의.

    Example:
        class MyImageProvider(ImageProvider):
            @property
            def provider_name(self) -> str:
                return "my_provider"

            async def generate(self, params: ImageGenerationParams) -> ImageGenerationResult:
                # 구현
                pass
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.IMAGE

    @property
    @abstractmethod
    def supported_sizes(self) -> list[str]:
        """지원하는 이미지 크기 목록 반환"""
        pass

    @property
    @abstractmethod
    def supported_styles(self) -> list[str]:
        """지원하는 스타일 목록 반환"""
        pass

    @abstractmethod
    async def generate(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """이미지 생성

        Args:
            params: 이미지 생성 파라미터

        Returns:
            ImageGenerationResult: 생성 결과
        """
        pass

    def validate_params(self, params: ImageGenerationParams) -> tuple[bool, Optional[str]]:
        """파라미터 유효성 검사"""
        if not params.prompt or not params.prompt.strip():
            return False, "프롬프트가 비어있습니다"

        if params.size not in self.supported_sizes:
            return False, f"지원하지 않는 크기: {params.size}. 지원: {self.supported_sizes}"

        if params.style not in self.supported_styles:
            return False, f"지원하지 않는 스타일: {params.style}. 지원: {self.supported_styles}"

        return True, None

    def normalize_size(self, size: str) -> str:
        """크기 정규화 (프로바이더별 형식으로 변환)"""
        return size


class LLMProvider(BaseProvider):
    """LLM 텍스트 생성 Provider 추상 클래스

    텍스트/LLM 생성 프로바이더가 구현해야 하는 인터페이스 정의.

    Example:
        class MyLLMProvider(LLMProvider):
            @property
            def provider_name(self) -> str:
                return "my_llm"

            async def generate(self, params: LLMGenerationParams) -> LLMGenerationResult:
                # 구현
                pass
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LLM

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """지원하는 모델 목록 반환"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """기본 모델 반환"""
        pass

    @abstractmethod
    async def generate(self, params: LLMGenerationParams) -> LLMGenerationResult:
        """텍스트 생성

        Args:
            params: LLM 생성 파라미터

        Returns:
            LLMGenerationResult: 생성 결과
        """
        pass

    def validate_params(self, params: LLMGenerationParams) -> tuple[bool, Optional[str]]:
        """파라미터 유효성 검사"""
        if not params.prompt or not params.prompt.strip():
            return False, "프롬프트가 비어있습니다"

        if params.temperature < 0.0 or params.temperature > 2.0:
            return False, f"온도는 0.0~2.0 사이여야 합니다: {params.temperature}"

        return True, None
