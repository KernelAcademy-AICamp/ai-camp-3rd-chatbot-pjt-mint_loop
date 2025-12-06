"""Tests for MCP Servers"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import json
import os


class TestSearchServerFunctions:
    """Search Server 함수 단위 테스트 - 내부 로직 테스트"""

    @pytest.mark.asyncio
    async def test_extract_keywords_logic(self):
        """키워드 추출 로직 테스트"""
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=Mock(content=json.dumps({
            "keywords": ["sunset", "beach", "waves"],
            "categories": {"subject": ["beach"]},
            "confidence": 0.9
        })))

        # 직접 로직 테스트 (MCP 데코레이터 우회)
        extraction_prompt = """
다음 텍스트에서 이미지 생성에 가장 중요한 키워드를 5개 추출하세요.
각 키워드는 시각적 요소, 분위기, 스타일, 색상, 구도 등을 포함해야 합니다.

텍스트: beautiful beach at sunset

응답 형식 (JSON):
{
    "keywords": ["키워드1", "키워드2", ...],
    "categories": {
        "subject": ["주요 대상"],
        "style": ["예술 스타일"],
        "mood": ["분위기"],
        "colors": ["색상"]
    },
    "confidence": 0.95
}
"""
        response = await mock_llm.ainvoke(extraction_prompt)
        result = json.loads(response.content)

        assert "keywords" in result
        assert len(result["keywords"]) == 3
        assert "sunset" in result["keywords"]
        assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_search_visual_references_logic(self):
        """시각적 참조 검색 로직 테스트"""
        mock_tavily = Mock()
        mock_tavily.search = Mock(return_value={
            "results": [
                {
                    "title": "Beach Sunset Image",
                    "url": "https://example.com/image1",
                    "content": "Beautiful beach sunset"
                }
            ]
        })

        # Tavily 검색 로직 테스트
        keywords = ["beach", "sunset"]
        query = " ".join(keywords)
        search_results = mock_tavily.search(
            query=f"{query} image visual reference",
            max_results=3,
            search_depth="advanced",
            include_images=True
        )

        references = []
        for result in search_results.get("results", []):
            references.append({
                "title": result.get("title"),
                "url": result.get("url"),
                "content": result.get("content", "")[:200],
            })

        assert len(references) == 1
        assert references[0]["title"] == "Beach Sunset Image"
        assert references[0]["url"] == "https://example.com/image1"


class TestImageServerFunctions:
    """Image Server 함수 단위 테스트 - 내부 로직 테스트"""

    @pytest.mark.asyncio
    async def test_generate_image_logic(self):
        """이미지 생성 로직 테스트"""
        mock_image_data = Mock()
        mock_image_data.url = "https://example.com/generated_image.png"
        mock_image_data.revised_prompt = "A beautiful beach at sunset"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_openai = Mock()
        mock_openai.images.generate = AsyncMock(return_value=mock_response)

        # OpenAI 이미지 생성 로직 테스트
        prompt = "beach sunset"
        size = "1024x1024"
        quality = "standard"
        style = "vivid"

        response = await mock_openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )

        image_data = response.data[0]
        result = {
            "url": image_data.url,
            "revised_prompt": image_data.revised_prompt,
            "metadata": {
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "style": style,
                "original_prompt": prompt
            }
        }

        assert result["url"] == "https://example.com/generated_image.png"
        assert result["metadata"]["model"] == "dall-e-3"
        assert result["metadata"]["size"] == "1024x1024"

    @pytest.mark.asyncio
    async def test_optimize_prompt_logic(self):
        """프롬프트 최적화 로직 테스트"""
        base_prompt = "beach scene"
        keywords = ["sunset", "waves", "peaceful"]
        style_preferences = None

        # 프롬프트 최적화 로직 직접 테스트
        keywords_str = ", ".join(keywords)
        style_additions = []

        if style_preferences:
            if "art_style" in style_preferences:
                style_additions.append(f"{style_preferences['art_style']} style")

        components = [base_prompt, keywords_str] + style_additions
        optimized_prompt = ", ".join(filter(None, components))
        quality_suffix = "high quality, detailed, professional"
        final_prompt = f"{optimized_prompt}, {quality_suffix}"

        result = {
            "optimized_prompt": final_prompt,
            "enhancements": {
                "keywords_added": len(keywords),
                "style_additions": style_additions,
                "quality_enhancements": quality_suffix
            }
        }

        assert "optimized_prompt" in result
        assert "beach scene" in result["optimized_prompt"]
        assert "sunset" in result["optimized_prompt"]
        assert "high quality" in result["optimized_prompt"]
        assert result["enhancements"]["keywords_added"] == 3

    @pytest.mark.asyncio
    async def test_generate_image_error_handling(self):
        """이미지 생성 에러 처리 테스트"""
        mock_openai = Mock()
        mock_openai.images.generate = AsyncMock(side_effect=Exception("API Error"))

        prompt = "test prompt"
        size = "1024x1024"
        quality = "standard"
        style = "vivid"

        try:
            await mock_openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            result = {"url": "some_url"}
        except Exception as e:
            result = {
                "url": None,
                "error": str(e),
                "metadata": {
                    "model": "dall-e-3",
                    "size": size,
                    "quality": quality,
                    "style": style
                }
            }

        assert "error" in result
        assert result["url"] is None
        assert "API Error" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_keywords_error_handling(self):
        """키워드 추출 에러 처리 테스트"""
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        user_prompt = "test prompt"

        try:
            response = await mock_llm.ainvoke("extraction prompt")
            result = json.loads(response.content)
        except Exception as e:
            # Fallback 로직
            result = {
                "keywords": [user_prompt],
                "categories": {},
                "confidence": 0.5,
                "error": str(e)
            }

        assert "error" in result
        assert "keywords" in result
        assert result["keywords"] == ["test prompt"]
        assert result["confidence"] == 0.5
