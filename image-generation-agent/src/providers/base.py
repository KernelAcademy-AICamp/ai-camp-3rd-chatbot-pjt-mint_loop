"""Image Provider Base Module

이미지 생성 프로바이더를 위한 추상 기반 클래스와 데이터 모델 정의
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ImageGenerationParams:
    """이미지 생성 파라미터

    모든 프로바이더에서 공통으로 사용되는 파라미터 정의

    Attributes:
        prompt: 이미지 생성 프롬프트
        size: 이미지 크기 (예: "1024x1024")
        quality: 이미지 품질 (예: "standard", "hd")
        style: 이미지 스타일 (예: "vivid", "natural")
        extra_params: 프로바이더별 추가 파라미터
    """
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: str = "vivid"
    extra_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "prompt": self.prompt,
            "size": self.size,
            "quality": self.quality,
            "style": self.style,
            **self.extra_params,
        }


@dataclass
class ImageGenerationResult:
    """이미지 생성 결과

    모든 프로바이더에서 공통으로 반환하는 결과 형식

    Attributes:
        success: 성공 여부
        url: 생성된 이미지 URL (실패 시 None)
        revised_prompt: 프로바이더가 수정한 프롬프트 (지원하는 경우)
        error: 에러 메시지 (성공 시 None)
        metadata: 추가 메타데이터
        provider: 사용된 프로바이더 이름
    """
    success: bool
    url: Optional[str]
    revised_prompt: Optional[str]
    error: Optional[str]
    metadata: dict
    provider: str

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (MCP 응답 형식)"""
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


class ImageProvider(ABC):
    """이미지 생성 프로바이더 추상 기반 클래스

    모든 이미지 생성 프로바이더가 구현해야 하는 인터페이스 정의

    Example:
        class MyProvider(ImageProvider):
            @property
            def provider_name(self) -> str:
                return "my_provider"

            async def generate(self, params: ImageGenerationParams) -> ImageGenerationResult:
                # 구현
                pass
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
    def supported_sizes(self) -> list[str]:
        """지원하는 이미지 크기 목록 반환

        Returns:
            list[str]: 지원 크기 목록 (예: ["1024x1024", "1792x1024"])
        """
        pass

    @property
    @abstractmethod
    def supported_styles(self) -> list[str]:
        """지원하는 스타일 목록 반환

        Returns:
            list[str]: 지원 스타일 목록 (예: ["vivid", "natural"])
        """
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

    def validate_params(self, params: ImageGenerationParams) -> tuple:
        """파라미터 유효성 검사

        Args:
            params: 검사할 파라미터

        Returns:
            tuple: (유효 여부, 에러 메시지)
        """
        if not params.prompt or not params.prompt.strip():
            return False, "프롬프트가 비어있습니다"

        if params.size not in self.supported_sizes:
            return False, f"지원하지 않는 크기: {params.size}. 지원: {self.supported_sizes}"

        if params.style not in self.supported_styles:
            return False, f"지원하지 않는 스타일: {params.style}. 지원: {self.supported_styles}"

        return True, None

    def normalize_size(self, size: str) -> str:
        """크기 정규화 (프로바이더별 형식으로 변환)

        기본 구현은 입력을 그대로 반환.
        필요한 경우 서브클래스에서 오버라이드.

        Args:
            size: 입력 크기 문자열

        Returns:
            str: 정규화된 크기 문자열
        """
        return size
