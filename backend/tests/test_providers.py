"""Provider Tests

이미지 생성 프로바이더 테스트
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.providers.base import (
    ImageGenerationParams,
    ImageGenerationResult,
    ImageProvider,
)
from src.providers.openai_provider import OpenAIProvider, DALLE3_SIZES
from src.providers.gemini_provider import GeminiProvider, SIZE_TO_ASPECT_RATIO
from src.providers.factory import ProviderFactory, get_provider, list_providers


class TestImageGenerationParams:
    """ImageGenerationParams 테스트"""

    def test_default_values(self):
        """기본값 테스트"""
        params = ImageGenerationParams(prompt="test prompt")
        assert params.prompt == "test prompt"
        assert params.size == "1024x1024"
        assert params.quality == "standard"
        assert params.style == "vivid"
        assert params.extra_params == {}

    def test_custom_values(self):
        """커스텀 값 테스트"""
        params = ImageGenerationParams(
            prompt="custom prompt",
            size="1792x1024",
            quality="hd",
            style="natural",
            extra_params={"custom": "value"},
        )
        assert params.size == "1792x1024"
        assert params.quality == "hd"
        assert params.style == "natural"
        assert params.extra_params == {"custom": "value"}

    def test_to_dict(self):
        """to_dict 변환 테스트"""
        params = ImageGenerationParams(
            prompt="test",
            extra_params={"key": "value"},
        )
        result = params.to_dict()
        assert result["prompt"] == "test"
        assert result["key"] == "value"


class TestImageGenerationResult:
    """ImageGenerationResult 테스트"""

    def test_success_result(self):
        """성공 결과 생성 테스트"""
        result = ImageGenerationResult.success_result(
            url="https://example.com/image.png",
            provider="test_provider",
            revised_prompt="revised",
            metadata={"model": "test"},
        )
        assert result.success is True
        assert result.url == "https://example.com/image.png"
        assert result.provider == "test_provider"
        assert result.revised_prompt == "revised"
        assert result.error is None

    def test_failure_result(self):
        """실패 결과 생성 테스트"""
        result = ImageGenerationResult.failure_result(
            error="Test error",
            provider="test_provider",
            metadata={"size": "1024x1024"},
        )
        assert result.success is False
        assert result.url is None
        assert result.error == "Test error"

    def test_to_dict(self):
        """to_dict 변환 테스트"""
        result = ImageGenerationResult.success_result(
            url="https://example.com/image.png",
            provider="openai",
            metadata={"model": "dall-e-3"},
        )
        data = result.to_dict()
        assert data["url"] == "https://example.com/image.png"
        assert data["metadata"]["provider"] == "openai"


class TestOpenAIProvider:
    """OpenAI 프로바이더 테스트"""

    def _create_provider(self):
        """Mock client로 프로바이더 생성"""
        mock_client = AsyncMock()
        return OpenAIProvider(client=mock_client)

    def test_provider_name(self):
        """프로바이더 이름 테스트"""
        provider = self._create_provider()
        assert provider.provider_name == "openai"

    def test_supported_sizes(self):
        """지원 크기 테스트"""
        provider = self._create_provider()
        assert provider.supported_sizes == DALLE3_SIZES
        assert "1024x1024" in provider.supported_sizes

    def test_supported_styles(self):
        """지원 스타일 테스트"""
        provider = self._create_provider()
        assert "vivid" in provider.supported_styles
        assert "natural" in provider.supported_styles

    def test_validate_params_success(self):
        """파라미터 검증 성공 테스트"""
        provider = self._create_provider()
        params = ImageGenerationParams(
            prompt="valid prompt",
            size="1024x1024",
            quality="standard",
            style="vivid",
        )
        is_valid, error = provider.validate_params(params)
        assert is_valid is True
        assert error is None

    def test_validate_params_empty_prompt(self):
        """빈 프롬프트 검증 테스트"""
        provider = self._create_provider()
        params = ImageGenerationParams(prompt="")
        is_valid, error = provider.validate_params(params)
        assert is_valid is False
        assert "비어있습니다" in error

    def test_validate_params_invalid_size(self):
        """잘못된 크기 검증 테스트"""
        provider = self._create_provider()
        params = ImageGenerationParams(prompt="test", size="invalid")
        is_valid, error = provider.validate_params(params)
        assert is_valid is False
        assert "지원하지 않는 크기" in error

    @pytest.mark.asyncio
    async def test_generate_success(self):
        """이미지 생성 성공 테스트"""
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(
                url="https://example.com/image.png",
                revised_prompt="revised prompt",
            )
        ]

        mock_client = AsyncMock()
        mock_client.images.generate = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(client=mock_client)
        params = ImageGenerationParams(prompt="test prompt")

        result = await provider.generate(params)

        assert result.success is True
        assert result.url == "https://example.com/image.png"
        assert result.revised_prompt == "revised prompt"
        assert result.provider == "openai"

    @pytest.mark.asyncio
    async def test_generate_failure(self):
        """이미지 생성 실패 테스트"""
        mock_client = AsyncMock()
        mock_client.images.generate = AsyncMock(
            side_effect=Exception("API Error")
        )

        provider = OpenAIProvider(client=mock_client)
        params = ImageGenerationParams(prompt="test prompt")

        result = await provider.generate(params)

        assert result.success is False
        assert "API Error" in result.error


class TestGeminiProvider:
    """Gemini 프로바이더 테스트"""

    def test_provider_name(self):
        """프로바이더 이름 테스트"""
        provider = GeminiProvider()
        assert provider.provider_name == "gemini"

    def test_supported_sizes(self):
        """지원 크기 테스트"""
        provider = GeminiProvider()
        assert "1024x1024" in provider.supported_sizes
        assert "1:1" in provider.supported_sizes

    def test_normalize_size(self):
        """크기 정규화 테스트"""
        provider = GeminiProvider()
        assert provider.normalize_size("1024x1024") == "1:1"
        assert provider.normalize_size("1792x1024") == "16:9"
        assert provider.normalize_size("1:1") == "1:1"
        assert provider.normalize_size("unknown") == "1:1"

    def test_enhance_prompt_with_style(self):
        """스타일 프롬프트 보강 테스트"""
        provider = GeminiProvider()
        enhanced = provider._enhance_prompt_with_style("base prompt", "vivid")
        assert "base prompt" in enhanced
        assert "vibrant colors" in enhanced

    def test_validate_params_success(self):
        """파라미터 검증 성공 테스트"""
        provider = GeminiProvider()
        params = ImageGenerationParams(
            prompt="valid prompt",
            size="1:1",
            style="vivid",
        )
        is_valid, error = provider.validate_params(params)
        assert is_valid is True


class TestProviderFactory:
    """프로바이더 팩토리 테스트"""

    def setup_method(self):
        """테스트 전 캐시 클리어"""
        ProviderFactory.clear_cache()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_provider_openai(self):
        """OpenAI 프로바이더 가져오기 테스트"""
        ProviderFactory.clear_cache()
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)
        assert provider.provider_name == "openai"

    def test_get_provider_gemini(self):
        """Gemini 프로바이더 가져오기 테스트"""
        provider = get_provider("gemini")
        assert isinstance(provider, GeminiProvider)
        assert provider.provider_name == "gemini"

    def test_get_provider_invalid(self):
        """잘못된 프로바이더 테스트"""
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider")
        assert "지원하지 않는 프로바이더" in str(exc_info.value)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_provider_caching(self):
        """프로바이더 캐싱 테스트"""
        ProviderFactory.clear_cache()
        provider1 = get_provider("openai")
        provider2 = get_provider("openai")
        assert provider1 is provider2

    def test_list_providers(self):
        """프로바이더 목록 테스트"""
        providers = list_providers()
        assert "openai" in providers
        assert "gemini" in providers

    @patch.dict("os.environ", {"IMAGE_PROVIDER": "gemini"})
    def test_default_provider_from_env(self):
        """환경변수에서 기본 프로바이더 테스트"""
        ProviderFactory.clear_cache()
        provider = get_provider()
        assert provider.provider_name == "gemini"


class TestProviderIntegration:
    """프로바이더 통합 테스트"""

    @pytest.mark.asyncio
    async def test_openai_full_workflow(self):
        """OpenAI 전체 워크플로우 테스트"""
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(
                url="https://example.com/image.png",
                revised_prompt="A beautiful sunset",
            )
        ]

        mock_client = AsyncMock()
        mock_client.images.generate = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(client=mock_client)
        params = ImageGenerationParams(
            prompt="A sunset over mountains",
            size="1024x1024",
            quality="hd",
            style="vivid",
        )

        # 검증
        is_valid, _ = provider.validate_params(params)
        assert is_valid

        # 생성
        result = await provider.generate(params)
        assert result.success
        assert result.url is not None

        # 결과 변환
        data = result.to_dict()
        assert "url" in data
        assert "metadata" in data
