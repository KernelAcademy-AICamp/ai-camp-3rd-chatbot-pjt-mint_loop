"""Tests for MCP Servers"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import json


@pytest.mark.asyncio
async def test_extract_keywords():
    """Test keyword extraction tool"""
    from src.mcp_servers.search_server import extract_keywords

    # Mock LLM response
    with patch('src.mcp_servers.search_server.llm') as mock_llm:
        mock_response = Mock()
        mock_response.content = json.dumps({
            "keywords": ["sunset", "beach", "waves"],
            "categories": {"subject": ["beach"]},
            "confidence": 0.9
        })
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await extract_keywords("beautiful beach at sunset")

        assert "keywords" in result
        assert len(result["keywords"]) > 0
        assert "confidence" in result


@pytest.mark.asyncio
async def test_search_visual_references():
    """Test visual reference search tool"""
    from src.mcp_servers.search_server import search_visual_references

    # Mock Tavily client
    with patch('src.mcp_servers.search_server.tavily_client') as mock_tavily:
        mock_tavily.search = Mock(return_value={
            "results": [
                {
                    "title": "Beach Sunset Image",
                    "url": "https://example.com/image1",
                    "content": "Beautiful beach sunset"
                }
            ]
        })

        result = await search_visual_references(["beach", "sunset"])

        assert "references" in result
        assert "query" in result
        assert len(result["references"]) > 0


@pytest.mark.asyncio
async def test_generate_image():
    """Test image generation tool"""
    from src.mcp_servers.image_server import generate_image

    # Mock OpenAI client
    with patch('src.mcp_servers.image_server.openai_client') as mock_openai:
        mock_image_data = Mock()
        mock_image_data.url = "https://example.com/generated_image.png"
        mock_image_data.revised_prompt = "A beautiful beach at sunset"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_openai.images.generate = AsyncMock(return_value=mock_response)

        result = await generate_image("beach sunset")

        assert result["url"] == "https://example.com/generated_image.png"
        assert "metadata" in result
        assert result["metadata"]["model"] == "dall-e-3"


@pytest.mark.asyncio
async def test_optimize_prompt_for_image():
    """Test prompt optimization tool"""
    from src.mcp_servers.image_server import optimize_prompt_for_image

    result = await optimize_prompt_for_image(
        base_prompt="beach scene",
        keywords=["sunset", "waves", "peaceful"]
    )

    assert "optimized_prompt" in result
    assert "beach scene" in result["optimized_prompt"]
    assert "sunset" in result["optimized_prompt"]
    assert "high quality" in result["optimized_prompt"]


@pytest.mark.asyncio
async def test_extract_keywords_error_handling():
    """Test error handling in keyword extraction"""
    from src.mcp_servers.search_server import extract_keywords

    # Mock LLM to raise error
    with patch('src.mcp_servers.search_server.llm') as mock_llm:
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        result = await extract_keywords("test prompt")

        assert "error" in result
        assert "keywords" in result  # Should still return fallback


@pytest.mark.asyncio
async def test_generate_image_error_handling():
    """Test error handling in image generation"""
    from src.mcp_servers.image_server import generate_image

    # Mock OpenAI client to raise error
    with patch('src.mcp_servers.image_server.openai_client') as mock_openai:
        mock_openai.images.generate = AsyncMock(side_effect=Exception("API Error"))

        result = await generate_image("test prompt")

        assert "error" in result
        assert result["url"] is None
