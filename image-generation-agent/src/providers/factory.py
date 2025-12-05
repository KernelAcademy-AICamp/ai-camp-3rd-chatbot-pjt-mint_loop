"""Image Provider Factory

프로바이더 생성 및 관리를 위한 팩토리 패턴 구현
"""

from __future__ import annotations

import os
from typing import Literal, Optional, Dict, Type

import structlog

from .base import ImageProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

logger = structlog.get_logger(__name__)

# 지원하는 프로바이더 타입
ProviderType = Literal["openai", "gemini"]

# 프로바이더 레지스트리
_PROVIDER_REGISTRY: Dict[str, Type[ImageProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


class ProviderFactory:
    """이미지 프로바이더 팩토리

    싱글톤 패턴으로 프로바이더 인스턴스를 관리합니다.

    Example:
        factory = ProviderFactory()
        provider = factory.get_provider("openai")
        result = await provider.generate(params)
    """

    _instance = None
    _providers: Dict[str, ImageProvider] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._providers = {}
        return cls._instance

    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[str] = None,
        **kwargs,
    ) -> ImageProvider:
        """프로바이더 인스턴스 가져오기

        Args:
            provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
            **kwargs: 프로바이더 초기화 인자

        Returns:
            ImageProvider: 프로바이더 인스턴스

        Raises:
            ValueError: 지원하지 않는 프로바이더 타입
        """
        # 프로바이더 타입 결정
        if provider_type is None:
            provider_type = os.getenv("IMAGE_PROVIDER", "openai")

        provider_type = provider_type.lower()

        # 레지스트리에서 확인
        if provider_type not in _PROVIDER_REGISTRY:
            available = list(_PROVIDER_REGISTRY.keys())
            raise ValueError(
                f"지원하지 않는 프로바이더: {provider_type}. "
                f"사용 가능: {available}"
            )

        # 캐시된 인스턴스 확인 (kwargs가 없는 경우만)
        cache_key = f"{provider_type}:{hash(frozenset(kwargs.items()) if kwargs else frozenset())}"
        if cache_key in cls._providers:
            return cls._providers[cache_key]

        # 새 인스턴스 생성
        provider_class = _PROVIDER_REGISTRY[provider_type]
        provider = provider_class(**kwargs)

        # 캐시에 저장
        cls._providers[cache_key] = provider

        logger.info(
            "Provider created",
            provider_type=provider_type,
            provider_name=provider.provider_name,
        )

        return provider

    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[ImageProvider],
    ) -> None:
        """커스텀 프로바이더 등록

        Args:
            name: 프로바이더 이름
            provider_class: 프로바이더 클래스
        """
        _PROVIDER_REGISTRY[name.lower()] = provider_class
        logger.info("Provider registered", name=name)

    @classmethod
    def list_providers(cls) -> list[str]:
        """등록된 프로바이더 목록 반환"""
        return list(_PROVIDER_REGISTRY.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """캐시된 프로바이더 인스턴스 삭제"""
        cls._providers.clear()


# 편의 함수
def get_provider(
    provider_type: Optional[str] = None,
    **kwargs,
) -> ImageProvider:
    """프로바이더 인스턴스 가져오기 (편의 함수)

    Args:
        provider_type: 프로바이더 타입 (None이면 환경변수에서 결정)
        **kwargs: 프로바이더 초기화 인자

    Returns:
        ImageProvider: 프로바이더 인스턴스
    """
    return ProviderFactory.get_provider(provider_type, **kwargs)


def list_providers() -> list[str]:
    """등록된 프로바이더 목록 반환"""
    return ProviderFactory.list_providers()
