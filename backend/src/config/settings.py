"""Settings and Configuration Management"""
import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""

    # LLM API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

    # Provider Selection
    image_provider: Literal["openai", "gemini"] = Field(
        default="openai",
        env="IMAGE_PROVIDER",
        description="이미지 생성 프로바이더 (openai 또는 gemini)"
    )

    # Image Generation Settings - OpenAI
    openai_image_model: str = Field(default="dall-e-3", env="OPENAI_IMAGE_MODEL")

    # Image Generation Settings - Gemini
    gemini_image_model: str = Field(
        default="imagen-3.0-generate-002",
        env="GEMINI_IMAGE_MODEL"
    )

    # Common Image Settings
    image_default_size: str = Field(
        default="1024x1024",
        env="IMAGE_DEFAULT_SIZE"
    )
    image_default_quality: Literal["standard", "hd"] = Field(
        default="standard",
        env="IMAGE_DEFAULT_QUALITY"
    )
    image_default_style: Literal["vivid", "natural"] = Field(
        default="vivid",
        env="IMAGE_DEFAULT_STYLE"
    )

    # MCP Server Settings
    search_mcp_port: int = Field(default=8050, env="SEARCH_MCP_PORT")
    image_mcp_port: int = Field(default=8051, env="IMAGE_MCP_PORT")
    search_mcp_url: str = Field(
        default="http://localhost:8050/mcp",
        env="SEARCH_MCP_URL"
    )
    image_mcp_url: str = Field(
        default="http://localhost:8051/mcp",
        env="IMAGE_MCP_URL"
    )

    # A2A Settings (Optional)
    a2a_agent_name: str = Field(default="ImageGenerationAgent", env="A2A_AGENT_NAME")
    a2a_agent_port: int = Field(default=8080, env="A2A_AGENT_PORT")
    a2a_agent_host: str = Field(default="0.0.0.0", env="A2A_AGENT_HOST")

    # Debug Settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Performance Settings
    max_keywords: int = Field(default=5, env="MAX_KEYWORDS")
    search_max_results: int = Field(default=3, env="SEARCH_MAX_RESULTS")
    image_timeout: int = Field(default=60, env="IMAGE_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings = None


def get_settings() -> Settings:
    """Get settings singleton instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
