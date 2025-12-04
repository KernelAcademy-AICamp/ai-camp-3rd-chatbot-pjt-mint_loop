"""Tests for ImageGenerationAgent"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.messages import HumanMessage, AIMessage

from src.image_agent.agent import ImageGenerationAgent
from src.image_agent.state import ImageGenerationState


@pytest.fixture
def mock_search_tools():
    """Mock Search MCP tools"""
    extract_tool = Mock()
    extract_tool.name = "extract_keywords"
    extract_tool.ainvoke = AsyncMock(return_value={
        "keywords": ["sunset", "beach", "surfing", "people"],
        "categories": {
            "subject": ["beach", "surfing"],
            "mood": ["peaceful", "active"]
        },
        "confidence": 0.9
    })

    return [extract_tool]


@pytest.fixture
def mock_image_tools():
    """Mock Image Generation MCP tools"""
    optimize_tool = Mock()
    optimize_tool.name = "optimize_prompt_for_image"
    optimize_tool.ainvoke = AsyncMock(return_value={
        "optimized_prompt": "sunset beach surfing people, high quality, detailed",
        "enhancements": {"keywords_added": 4}
    })

    generate_tool = Mock()
    generate_tool.name = "generate_image"
    generate_tool.ainvoke = AsyncMock(return_value={
        "url": "https://example.com/image.png",
        "metadata": {
            "model": "dall-e-3",
            "size": "1024x1024"
        }
    })

    return [optimize_tool, generate_tool]


@pytest.mark.asyncio
async def test_agent_initialization(mock_search_tools, mock_image_tools):
    """Test agent initialization"""
    agent = ImageGenerationAgent(
        search_tools=mock_search_tools,
        image_tools=mock_image_tools
    )

    assert agent is not None
    assert agent.search_tools == mock_search_tools
    assert agent.image_tools == mock_image_tools
    assert agent.graph is not None


@pytest.mark.asyncio
async def test_image_generation_success(mock_search_tools, mock_image_tools):
    """Test successful image generation"""
    agent = ImageGenerationAgent(
        search_tools=mock_search_tools,
        image_tools=mock_image_tools
    )

    result = await agent.generate("sunset beach with surfers")

    assert result["status"] == "completed"
    assert result["generated_image_url"] == "https://example.com/image.png"
    assert len(result["extracted_keywords"]) > 0
    assert result["optimized_prompt"] is not None
    assert result["error"] is None


@pytest.mark.asyncio
async def test_image_generation_with_error(mock_search_tools):
    """Test image generation with error"""
    # Mock tool that raises error
    error_tool = Mock()
    error_tool.name = "extract_keywords"
    error_tool.ainvoke = AsyncMock(side_effect=Exception("Tool error"))

    agent = ImageGenerationAgent(
        search_tools=[error_tool],
        image_tools=[]
    )

    result = await agent.generate("test prompt")

    assert result["status"] == "failed"
    assert result["error"] is not None
    assert result["generated_image_url"] is None


@pytest.mark.asyncio
async def test_agent_with_custom_thread_id(mock_search_tools, mock_image_tools):
    """Test agent with custom thread ID"""
    agent = ImageGenerationAgent(
        search_tools=mock_search_tools,
        image_tools=mock_image_tools
    )

    result = await agent.generate(
        "beach sunset",
        thread_id="custom_thread_123"
    )

    assert result["status"] == "completed"
