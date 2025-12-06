"""이미지 생성 LangGraph Agent

Google Gemini Imagen 모델을 사용합니다.
기본 모델: imagen-3.0-generate-002 (nano-banana)
Search MCP는 키워드 추출에 활용 (RAG 및 다른 에이전트에서 재사용 가능)
"""
import structlog
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ImageGenerationState
from .nodes import (
    extract_keywords_node,
    optimize_prompt_node,
    generate_image_node,
    DEFAULT_IMAGE_MODEL,
)

logger = structlog.get_logger(__name__)


class ImageGenerationAgent:
    """이미지 생성 Agent

    LangGraph를 사용하여 구현된 이미지 생성 워크플로우:
    1. 사용자 입력 수신
    2. 키워드 추출 (Search MCP)
    3. 프롬프트 최적화 (직접 구현)
    4. 이미지 생성 (Gemini Imagen)

    Google Gemini Imagen 모델을 사용합니다.
    기본 모델: imagen-3.0-generate-002 (nano-banana)
    """

    def __init__(
        self,
        search_tools: list,
        provider_type: str | None = None,
        image_model: str | None = None,
        checkpointer: MemorySaver | None = None
    ):
        """Agent 초기화

        Args:
            search_tools: Search MCP 서버의 도구 리스트 (키워드 추출용)
            provider_type: 이미지 생성 프로바이더 타입 (기본: gemini)
            image_model: 이미지 생성 모델 (기본: imagen-3.0-generate-002)
            checkpointer: 체크포인터 (선택사항)
        """
        self.search_tools = search_tools
        self.provider_type = provider_type or "gemini"
        self.image_model = image_model or DEFAULT_IMAGE_MODEL
        self.checkpointer = checkpointer or MemorySaver()

        # 그래프 빌드
        self.graph = self._build_graph()

        logger.info(
            "ImageGenerationAgent initialized",
            provider_type=self.provider_type,
            image_model=self.image_model
        )

    def _build_graph(self):
        """LangGraph 워크플로우 구축"""

        # StateGraph 생성 (전체 상태 스키마 사용)
        workflow = StateGraph(ImageGenerationState)

        # async 노드 래퍼 함수 생성
        async def _extract_keywords(state):
            return await extract_keywords_node(state, self.search_tools)

        async def _optimize_prompt(state):
            return await optimize_prompt_node(state)

        async def _generate_image(state):
            # provider_type과 image_model 전달
            return await generate_image_node(
                state,
                provider_type=self.provider_type,
                image_model=self.image_model
            )

        # 노드 추가
        workflow.add_node("extract_keywords", _extract_keywords)
        workflow.add_node("optimize_prompt", _optimize_prompt)
        workflow.add_node("generate_image", _generate_image)

        # 엣지 정의
        workflow.set_entry_point("extract_keywords")
        workflow.add_edge("extract_keywords", "optimize_prompt")
        workflow.add_edge("optimize_prompt", "generate_image")
        workflow.add_edge("generate_image", END)

        # 컴파일
        return workflow.compile(
            checkpointer=self.checkpointer,
            debug=True
        )

    async def generate(
        self,
        user_prompt: str,
        thread_id: str = "default",
        image_model: str | None = None
    ) -> dict:
        """이미지 생성 실행

        Args:
            user_prompt: 사용자 입력 텍스트
            thread_id: 대화 스레드 ID
            image_model: 이 요청에서 사용할 모델 (선택사항, 인스턴스 기본값 오버라이드)

        Returns:
            dict: 생성 결과
                - generated_image_url: 이미지 URL
                - image_metadata: 메타데이터
                - status: 상태
        """
        try:
            # 요청별 모델 오버라이드 가능
            actual_model = image_model or self.image_model

            logger.info(
                f"Starting image generation for prompt: {user_prompt[:100]}...",
                image_model=actual_model
            )

            # 초기 상태 구성
            initial_state = {
                "messages": [HumanMessage(content=user_prompt)],
                "user_prompt": user_prompt,
                "extracted_keywords": [],
                "optimized_prompt": "",
                "generated_image_url": None,
                "image_metadata": None,
                "image_model": actual_model,  # 모델 정보를 state에 포함
                "status": "pending",
                "error": None
            }

            # 그래프 실행
            config = {"configurable": {"thread_id": thread_id}}
            result = await self.graph.ainvoke(initial_state, config)

            logger.info(f"Image generation completed with status: {result['status']}")

            return {
                "generated_image_url": result.get("generated_image_url"),
                "image_metadata": result.get("image_metadata"),
                "extracted_keywords": result.get("extracted_keywords"),
                "optimized_prompt": result.get("optimized_prompt"),
                "status": result["status"],
                "error": result.get("error")
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "generated_image_url": None,
                "image_metadata": None,
                "status": "failed",
                "error": str(e)
            }
