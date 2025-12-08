"""Provider Factory Module

프로바이더 생성 및 관리를 위한 통합 팩토리 패턴 구현
- ImageProvider 및 LLMProvider 모두 지원
- 싱글톤 패턴으로 인스턴스 캐싱
"""

from __future__ import annotations

import os
from typing import Literal, Optional, Dict, Type, Union

import structlog

from .base import (
    BaseProvider,
    ImageProvider,
    LLMProvider,
    ProviderType,
)
from .openai_provider import OpenAIImageProvider, OpenAILLMProvider
from .gemini_provider import GeminiImageProvider, GeminiLLMProvider

logger = structlog.get_logger(__name__)

# =============================================================================
# 타입 정의
# =============================================================================

ImageProviderName = Literal["openai", "gemini"]
LLMProviderName = Literal["openai", "gemini"]

# =============================================================================
# Provider 레지스트리
# =============================================================================

_IMAGE_PROVIDER_REGISTRY: Dict[str, Type[ImageProvider]] = {
    "openai": OpenAIImageProvider,
    "gemini": GeminiImageProvider,
}

_LLM_PROVIDER_REGISTRY: Dict[str, Type[LLMProvider]] = {
    "openai": OpenAILLMProvider,
    "gemini": GeminiLLMProvider,
}


# =============================================================================
# 통합 Provider Factory
# =============================================================================

class ProviderFactory:
    """통합 Provider 팩토리

    싱글톤 패턴으로 Image/LLM 프로바이더 인스턴스를 관리합니다.

    Example:
        # Image Provider
        image_provider = ProviderFactory.get_image_provider("openai")
        result = await image_provider.generate(params)

        # LLM Provider
        llm_provider = ProviderFactory.get_llm_provider("openai")
        result = await llm_provider.generate(params)
    """

    _instance = None
    _image_providers: Dict[str, ImageProvider] = {}
    _llm_providers: Dict[str, LLMProvider] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._image_providers = {}
            cls._llm_providers = {}
        return cls._instance

    # =========================================================================
    # Image Provider 메서드
    # =========================================================================

    @classmethod
    def get_image_provider(
        cls,
        provider_type: Optional[str] = None,
        **kwargs,
    ) -> ImageProvider:
        """이미지 생성 프로바이더 인스턴스 가져오기

        Args:
            provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
            **kwargs: 프로바이더 초기화 인자

        Returns:
            ImageProvider: 이미지 프로바이더 인스턴스

        Raises:
            ValueError: 지원하지 않는 프로바이더 타입
        """
        if provider_type is None:
            provider_type = os.getenv("IMAGE_PROVIDER", "openai")

        provider_type = provider_type.lower()

        if provider_type not in _IMAGE_PROVIDER_REGISTRY:
            available = list(_IMAGE_PROVIDER_REGISTRY.keys())
            raise ValueError(
                f"지원하지 않는 Image 프로바이더: {provider_type}. "
                f"사용 가능: {available}"
            )

        cache_key = cls._make_cache_key(provider_type, kwargs)
        if cache_key in cls._image_providers:
            return cls._image_providers[cache_key]

        provider_class = _IMAGE_PROVIDER_REGISTRY[provider_type]
        provider = provider_class(**kwargs)

        cls._image_providers[cache_key] = provider

        logger.info(
            "Image provider created",
            provider_type=provider_type,
            provider_name=provider.provider_name,
        )

        return provider

    # =========================================================================
    # LLM Provider 메서드
    # =========================================================================

    @classmethod
    def get_llm_provider(
        cls,
        provider_type: Optional[str] = None,
        **kwargs,
    ) -> LLMProvider:
        """LLM 텍스트 생성 프로바이더 인스턴스 가져오기

        Args:
            provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
            **kwargs: 프로바이더 초기화 인자

        Returns:
            LLMProvider: LLM 프로바이더 인스턴스

        Raises:
            ValueError: 지원하지 않는 프로바이더 타입
        """
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "openai")

        provider_type = provider_type.lower()

        if provider_type not in _LLM_PROVIDER_REGISTRY:
            available = list(_LLM_PROVIDER_REGISTRY.keys())
            raise ValueError(
                f"지원하지 않는 LLM 프로바이더: {provider_type}. "
                f"사용 가능: {available}"
            )

        cache_key = cls._make_cache_key(f"llm_{provider_type}", kwargs)
        if cache_key in cls._llm_providers:
            return cls._llm_providers[cache_key]

        provider_class = _LLM_PROVIDER_REGISTRY[provider_type]
        provider = provider_class(**kwargs)

        cls._llm_providers[cache_key] = provider

        logger.info(
            "LLM provider created",
            provider_type=provider_type,
            provider_name=provider.provider_name,
            default_model=provider.default_model,
        )

        return provider

    # =========================================================================
    # 유틸리티 메서드
    # =========================================================================

    @staticmethod
    def _make_cache_key(provider_type: str, kwargs: dict) -> str:
        """캐시 키 생성"""
        if not kwargs:
            return provider_type
        return f"{provider_type}:{hash(frozenset(kwargs.items()))}"

    @classmethod
    def register_image_provider(
        cls,
        name: str,
        provider_class: Type[ImageProvider],
    ) -> None:
        """커스텀 이미지 프로바이더 등록"""
        _IMAGE_PROVIDER_REGISTRY[name.lower()] = provider_class
        logger.info("Image provider registered", name=name)

    @classmethod
    def register_llm_provider(
        cls,
        name: str,
        provider_class: Type[LLMProvider],
    ) -> None:
        """커스텀 LLM 프로바이더 등록"""
        _LLM_PROVIDER_REGISTRY[name.lower()] = provider_class
        logger.info("LLM provider registered", name=name)

    @classmethod
    def list_image_providers(cls) -> list[str]:
        """등록된 이미지 프로바이더 목록 반환"""
        return list(_IMAGE_PROVIDER_REGISTRY.keys())

    @classmethod
    def list_llm_providers(cls) -> list[str]:
        """등록된 LLM 프로바이더 목록 반환"""
        return list(_LLM_PROVIDER_REGISTRY.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """캐시된 프로바이더 인스턴스 삭제"""
        cls._image_providers.clear()
        cls._llm_providers.clear()


# =============================================================================
# 편의 함수
# =============================================================================

def get_image_provider(
    provider_type: Optional[str] = None,
    **kwargs,
) -> ImageProvider:
    """이미지 프로바이더 인스턴스 가져오기 (편의 함수)

    Args:
        provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
        **kwargs: 프로바이더 초기화 인자

    Returns:
        ImageProvider: 이미지 프로바이더 인스턴스
    """
    return ProviderFactory.get_image_provider(provider_type, **kwargs)


def get_llm_provider(
    provider_type: Optional[str] = None,
    **kwargs,
) -> LLMProvider:
    """LLM 프로바이더 인스턴스 가져오기 (편의 함수)

    Args:
        provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
        **kwargs: 프로바이더 초기화 인자

    Returns:
        LLMProvider: LLM 프로바이더 인스턴스
    """
    return ProviderFactory.get_llm_provider(provider_type, **kwargs)


def list_providers() -> dict[str, list[str]]:
    """등록된 프로바이더 목록 반환"""
    return {
        "image": ProviderFactory.list_image_providers(),
        "llm": ProviderFactory.list_llm_providers(),
    }


# =============================================================================
# 하위 호환성을 위한 별칭
# =============================================================================

# 기존 코드 호환성 (이미지 프로바이더 전용)
def get_provider(
    provider_type: Optional[str] = None,
    **kwargs,
) -> ImageProvider:
    """기존 API 호환성을 위한 함수 (이미지 프로바이더 반환)"""
    return get_image_provider(provider_type, **kwargs)
