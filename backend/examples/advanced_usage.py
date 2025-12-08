"""고급 사용 예제

이 예제는 이미지 생성 Agent의 고급 기능을 보여줍니다:
1. 다양한 스타일 프리셋 사용
2. 배치 처리
3. 이미지 히스토리 관리
4. 스트리밍 업데이트
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

import structlog
from dotenv import load_dotenv

load_dotenv()

logger = structlog.get_logger(__name__)


class AdvancedImageGenerator:
    """고급 이미지 생성 기능을 제공하는 래퍼 클래스"""

    # 스타일 프리셋 정의
    STYLE_PRESETS = {
        "realistic": {
            "style": "natural",
            "quality": "hd",
            "enhancements": "photorealistic, detailed, 8k resolution"
        },
        "artistic": {
            "style": "vivid",
            "quality": "standard",
            "enhancements": "artistic, creative, expressive"
        },
        "anime": {
            "style": "vivid",
            "quality": "standard",
            "enhancements": "anime style, manga, Japanese art"
        },
        "minimalist": {
            "style": "natural",
            "quality": "standard",
            "enhancements": "minimalist, simple, clean design"
        },
        "vintage": {
            "style": "natural",
            "quality": "standard",
            "enhancements": "vintage, retro, old-fashioned aesthetic"
        }
    }

    def __init__(self, agent):
        """
        Args:
            agent: ImageGenerationAgent 인스턴스
        """
        self.agent = agent
        self.history: List[Dict[str, Any]] = []
        self.history_file = Path("image_generation_history.json")

        # 기존 히스토리 로드
        self._load_history()

        logger.info("AdvancedImageGenerator initialized")

    def _load_history(self):
        """저장된 히스토리 로드"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                logger.info(f"Loaded {len(self.history)} history entries")
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
                self.history = []

    def _save_history(self):
        """히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.history)} history entries")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    async def generate_with_style(
        self,
        user_prompt: str,
        style_preset: str = "realistic",
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """스타일 프리셋을 적용하여 이미지 생성

        Args:
            user_prompt: 사용자 입력 텍스트
            style_preset: 스타일 프리셋 이름
            thread_id: 대화 스레드 ID

        Returns:
            dict: 생성 결과
        """
        if style_preset not in self.STYLE_PRESETS:
            logger.warning(f"Unknown style preset: {style_preset}, using 'realistic'")
            style_preset = "realistic"

        preset = self.STYLE_PRESETS[style_preset]
        logger.info(f"Generating image with {style_preset} style")

        # 프롬프트에 스타일 추가
        enhanced_prompt = f"{user_prompt}, {preset['enhancements']}"

        # 이미지 생성
        result = await self.agent.generate(
            user_prompt=enhanced_prompt,
            thread_id=thread_id
        )

        # 히스토리에 추가
        if result["status"] == "completed":
            history_entry = {
                "user_prompt": user_prompt,
                "style_preset": style_preset,
                "image_url": result["generated_image_url"],
                "keywords": result["extracted_keywords"],
                "timestamp": result["image_metadata"].get("timestamp", "")
            }
            self.history.append(history_entry)
            self._save_history()

        return result

    async def batch_generate(
        self,
        prompts: List[str],
        style_preset: str = "realistic",
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """여러 프롬프트를 배치로 처리

        Args:
            prompts: 프롬프트 리스트
            style_preset: 스타일 프리셋
            max_concurrent: 최대 동시 실행 수

        Returns:
            list: 생성 결과 리스트
        """
        logger.info(f"Batch generating {len(prompts)} images")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_semaphore(prompt, index):
            async with semaphore:
                thread_id = f"batch_{index}"
                logger.info(f"Processing {index + 1}/{len(prompts)}: {prompt[:50]}...")
                return await self.generate_with_style(
                    user_prompt=prompt,
                    style_preset=style_preset,
                    thread_id=thread_id
                )

        tasks = [
            generate_with_semaphore(prompt, i)
            for i, prompt in enumerate(prompts)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 에러 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                processed_results.append({
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        logger.info(f"Batch generation completed: {len(processed_results)} results")
        return processed_results

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 히스토리 조회

        Args:
            limit: 조회할 최대 개수

        Returns:
            list: 히스토리 엔트리 리스트
        """
        return self.history[-limit:]

    def search_history(self, keyword: str) -> List[Dict[str, Any]]:
        """키워드로 히스토리 검색

        Args:
            keyword: 검색 키워드

        Returns:
            list: 매칭되는 히스토리 엔트리
        """
        keyword_lower = keyword.lower()
        return [
            entry for entry in self.history
            if keyword_lower in entry["user_prompt"].lower()
            or any(keyword_lower in kw.lower() for kw in entry.get("keywords", []))
        ]


async def create_agent():
    """Agent 생성 헬퍼 함수

    리팩토링: Search MCP만 연결, Image MCP 제거
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from src.image_agent.agent import ImageGenerationAgent

    # Search MCP만 연결 (Image MCP 제거)
    mcp_servers = {
        "search": {
            "transport": "streamable_http",
            "url": "http://localhost:8050/mcp"
        }
    }

    mcp_client = MultiServerMCPClient(mcp_servers)
    tools = await mcp_client.get_tools()

    search_tools = [t for t in tools if "search" in t.name or "keyword" in t.name]

    # image_tools 파라미터 제거됨
    agent = ImageGenerationAgent(search_tools=search_tools)

    return agent


async def example_1_style_presets():
    """예제 1: 다양한 스타일 프리셋 사용"""
    print("\n=== 예제 1: 스타일 프리셋 ===\n")

    agent = await create_agent()
    advanced_gen = AdvancedImageGenerator(agent)

    # 동일한 프롬프트로 다양한 스타일 테스트
    base_prompt = "산속의 작은 오두막"

    for style in ["realistic", "artistic", "anime", "minimalist", "vintage"]:
        print(f"\n스타일: {style}")
        print(f"프롬프트: {base_prompt}")

        result = await advanced_gen.generate_with_style(
            user_prompt=base_prompt,
            style_preset=style,
            thread_id=f"style_test_{style}"
        )

        if result["status"] == "completed":
            print(f"✓ 생성 완료: {result['generated_image_url']}")
        else:
            print(f"✗ 생성 실패: {result.get('error')}")


async def example_2_batch_processing():
    """예제 2: 배치 처리"""
    print("\n=== 예제 2: 배치 처리 ===\n")

    agent = await create_agent()
    advanced_gen = AdvancedImageGenerator(agent)

    # 여러 프롬프트 배치 처리
    prompts = [
        "미래 도시의 스카이라인",
        "고요한 호수가 있는 숲",
        "활기찬 전통 시장",
        "별이 빛나는 밤하늘 아래 캠핑",
        "현대적인 카페 인테리어"
    ]

    print(f"{len(prompts)}개의 이미지를 배치 생성합니다...\n")

    results = await advanced_gen.batch_generate(
        prompts=prompts,
        style_preset="artistic",
        max_concurrent=2  # 동시에 2개씩 처리
    )

    # 결과 출력
    success_count = sum(1 for r in results if r["status"] == "completed")
    print(f"\n배치 처리 완료: {success_count}/{len(results)} 성공")

    for i, result in enumerate(results):
        if result["status"] == "completed":
            print(f"\n{i+1}. {prompts[i]}")
            print(f"   URL: {result['generated_image_url']}")
            print(f"   키워드: {', '.join(result['extracted_keywords'])}")


async def example_3_history_management():
    """예제 3: 히스토리 관리"""
    print("\n=== 예제 3: 히스토리 관리 ===\n")

    agent = await create_agent()
    advanced_gen = AdvancedImageGenerator(agent)

    # 최근 히스토리 조회
    print("최근 생성 이미지 (최대 5개):")
    recent_history = advanced_gen.get_history(limit=5)

    if not recent_history:
        print("  (히스토리 없음)")
    else:
        for i, entry in enumerate(recent_history, 1):
            print(f"\n{i}. {entry['user_prompt']}")
            print(f"   스타일: {entry.get('style_preset', 'N/A')}")
            print(f"   URL: {entry['image_url']}")

    # 키워드 검색
    print("\n\n'산' 키워드로 히스토리 검색:")
    search_results = advanced_gen.search_history("산")

    if not search_results:
        print("  (결과 없음)")
    else:
        for i, entry in enumerate(search_results, 1):
            print(f"\n{i}. {entry['user_prompt']}")
            print(f"   키워드: {', '.join(entry.get('keywords', []))}")


async def main():
    """고급 예제 실행"""

    print("=== 이미지 생성 Agent 고급 사용 예제 ===")
    print("(리팩토링: Image MCP 제거, providers 직접 호출)")

    # 예제 선택
    print("\n실행할 예제를 선택하세요:")
    print("1. 스타일 프리셋")
    print("2. 배치 처리")
    print("3. 히스토리 관리")
    print("4. 모두 실행")

    choice = input("\n선택 (1-4): ").strip()

    if choice == "1":
        await example_1_style_presets()
    elif choice == "2":
        await example_2_batch_processing()
    elif choice == "3":
        await example_3_history_management()
    elif choice == "4":
        await example_1_style_presets()
        await example_2_batch_processing()
        await example_3_history_management()
    else:
        print("잘못된 선택입니다.")

    print("\n\n완료!")


if __name__ == "__main__":
    asyncio.run(main())
