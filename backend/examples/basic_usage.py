"""기본 사용 예제"""
import asyncio
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

async def main():
    """기본 이미지 생성 예제"""

    # 1. MCP 서버에서 도구 로드
    from langchain_mcp_adapters.client import MultiServerMCPClient

    mcp_servers = {
        "search": {
            "transport": "streamable_http",
            "url": "http://localhost:8050/mcp"
        },
        "image": {
            "transport": "streamable_http",
            "url": "http://localhost:8051/mcp"
        }
    }

    print("Connecting to MCP servers...")
    mcp_client = MultiServerMCPClient(mcp_servers)
    tools = await mcp_client.get_tools()

    # 도구 분류
    search_tools = [t for t in tools if "search" in t.name or "keyword" in t.name]
    image_tools = [t for t in tools if "image" in t.name or "prompt" in t.name]

    print(f"Loaded {len(search_tools)} search tools and {len(image_tools)} image tools")

    # 2. Agent 생성
    from src.image_agent.agent import ImageGenerationAgent

    agent = ImageGenerationAgent(
        search_tools=search_tools,
        image_tools=image_tools
    )

    # 3. 이미지 생성
    user_prompt = "석양이 지는 바닷가에서 서핑을 즐기는 사람들"

    print(f"\n사용자 입력: {user_prompt}")
    print("이미지 생성 중...")

    result = await agent.generate(user_prompt)

    # 4. 결과 출력
    print("\n=== 생성 결과 ===")
    print(f"상태: {result['status']}")

    if result['status'] == 'completed':
        print(f"추출된 키워드: {', '.join(result['extracted_keywords'])}")
        print(f"최적화된 프롬프트: {result['optimized_prompt']}")
        print(f"이미지 URL: {result['generated_image_url']}")
        print(f"메타데이터: {result['image_metadata']}")
    else:
        print(f"에러: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
