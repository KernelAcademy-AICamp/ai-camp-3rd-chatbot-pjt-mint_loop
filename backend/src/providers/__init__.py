"""Providers Package

Strategy Pattern 기반의 Provider 추상화 레이어
- ImageProvider: 이미지 생성 (OpenAI DALL-E 3, Vertex AI Imagen 3)
- LLMProvider: 텍스트 생성 (OpenAI GPT-4, Google Gemini)
"""

from .base import (
    # 타입
    ProviderType,
    BaseProvider,
    # Image Provider
    ImageProvider,
    ImageGenerationParams,
    ImageGenerationResult,
    # LLM Provider
    LLMProvider,
    LLMGenerationParams,
    LLMGenerationResult,
)

from .factory import (
    ProviderFactory,
    get_image_provider,
    get_llm_provider,
    get_provider,  # 하위 호환성
    list_providers,
)

from .openai_provider import (
    OpenAIImageProvider,
    OpenAILLMProvider,
    OpenAIProvider,  # 하위 호환성 (= OpenAIImageProvider)
)

from .gemini_provider import (
    GeminiImageProvider,
    GeminiLLMProvider,
    GeminiProvider,  # 하위 호환성 (= GeminiImageProvider)
)

__all__ = [
    # 타입
    "ProviderType",
    "BaseProvider",
    # Image Provider
    "ImageProvider",
    "ImageGenerationParams",
    "ImageGenerationResult",
    "OpenAIImageProvider",
    "GeminiImageProvider",
    # LLM Provider
    "LLMProvider",
    "LLMGenerationParams",
    "LLMGenerationResult",
    "OpenAILLMProvider",
    "GeminiLLMProvider",
    # Factory
    "ProviderFactory",
    "get_image_provider",
    "get_llm_provider",
    "list_providers",
    # 하위 호환성
    "OpenAIProvider",
    "GeminiProvider",
    "get_provider",
]
