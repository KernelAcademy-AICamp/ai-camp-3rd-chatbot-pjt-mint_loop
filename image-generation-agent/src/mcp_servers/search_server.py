"""Search MCP Server - 키워드 추출 및 컨텍스트 검색"""
import os
from typing import Any
from pathlib import Path

from dotenv import load_dotenv

# .env 파일을 현재 디렉토리 및 상위 디렉토리에서 검색
def find_and_load_dotenv():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).resolve().parent
    for _ in range(5):  # Check up to 5 parent directories
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True
        current = current.parent
    # Fallback to default behavior
    load_dotenv()
    return False

find_and_load_dotenv()

import structlog
from fastmcp import FastMCP
from tavily import TavilyClient
from langchain_openai import ChatOpenAI

logger = structlog.get_logger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP("SearchMCP")

# Tavily 클라이언트 초기화
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# LLM 초기화 (키워드 추출용)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)


@mcp.tool()
async def extract_keywords(user_prompt: str, max_keywords: int = 5) -> dict[str, Any]:
    """사용자 프롬프트에서 이미지 생성에 적합한 키워드 추출

    Args:
        user_prompt: 사용자가 입력한 텍스트
        max_keywords: 추출할 최대 키워드 수 (기본값: 5)

    Returns:
        dict: 추출된 키워드와 메타데이터
            - keywords: 추출된 키워드 리스트
            - categories: 키워드 카테고리 (주제, 스타일, 색상 등)
            - confidence: 추출 신뢰도 (0.0 ~ 1.0)
    """
    try:
        logger.info(f"Extracting keywords from prompt: {user_prompt[:100]}...")

        # LLM을 사용한 키워드 추출
        extraction_prompt = f"""
다음 텍스트에서 이미지 생성에 가장 중요한 키워드를 {max_keywords}개 추출하세요.
각 키워드는 시각적 요소, 분위기, 스타일, 색상, 구도 등을 포함해야 합니다.

텍스트: {user_prompt}

응답 형식 (JSON):
{{
    "keywords": ["키워드1", "키워드2", ...],
    "categories": {{
        "subject": ["주요 대상"],
        "style": ["예술 스타일"],
        "mood": ["분위기"],
        "colors": ["색상"]
    }},
    "confidence": 0.95
}}
"""

        response = await llm.ainvoke(extraction_prompt)

        # JSON 파싱
        import json
        result = json.loads(response.content)

        logger.info(f"Extracted {len(result['keywords'])} keywords")
        return result

    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        return {
            "keywords": [user_prompt],
            "categories": {},
            "confidence": 0.5,
            "error": str(e)
        }


@mcp.tool()
async def search_visual_references(keywords: list[str], max_results: int = 3) -> dict[str, Any]:
    """키워드를 기반으로 시각적 참조 자료 검색

    Args:
        keywords: 검색할 키워드 리스트
        max_results: 최대 검색 결과 수

    Returns:
        dict: 검색 결과
            - references: 참조 이미지 URL 및 설명
            - context: 추가 컨텍스트 정보
    """
    try:
        query = " ".join(keywords)
        logger.info(f"Searching visual references for: {query}")

        # Tavily로 이미지 관련 검색
        search_results = tavily_client.search(
            query=f"{query} image visual reference",
            max_results=max_results,
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

        return {
            "references": references,
            "query": query,
            "total_results": len(references)
        }

    except Exception as e:
        logger.error(f"Visual reference search failed: {e}")
        return {
            "references": [],
            "query": " ".join(keywords),
            "error": str(e)
        }


if __name__ == "__main__":
    # MCP 서버 실행 (0.0.0.0으로 바인딩하여 Docker 네트워크에서 접근 가능)
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8050)
