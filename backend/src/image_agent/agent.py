"""이미지 생성 LangGraph Agent"""
import structlog
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ImageGenerationState
from .nodes import extract_keywords_node, optimize_prompt_node, generate_image_node

logger = structlog.get_logger(__name__)


class ImageGenerationAgent:
    """이미지 생성 Agent

    LangGraph를 사용하여 구현된 이미지 생성 워크플로우:
    1. 사용자 입력 수신
    2. 키워드 추출 (Search MCP)
    3. 프롬프트 최적화 (Image MCP)
    4. 이미지 생성 (Image MCP)
    """

    def __init__(
        self,
        search_tools: list,
        image_tools: list,
        checkpointer: MemorySaver | None = None
    ):
        """Agent 초기화

        Args:
            search_tools: Search MCP 서버의 도구 리스트
            image_tools: Image Generation MCP 서버의 도구 리스트
            checkpointer: 체크포인터 (선택사항)
        """
        self.search_tools = search_tools
        self.image_tools = image_tools
        self.checkpointer = checkpointer or MemorySaver()

        # 그래프 빌드
        self.graph = self._build_graph()

        logger.info("ImageGenerationAgent initialized")

    def _build_graph(self):
        """LangGraph 워크플로우 구축"""

        # StateGraph 생성 (전체 상태 스키마 사용)
        workflow = StateGraph(ImageGenerationState)

        # async 노드 래퍼 함수 생성
        async def _extract_keywords(state):
            return await extract_keywords_node(state, self.search_tools)

        async def _optimize_prompt(state):
            return await optimize_prompt_node(state, self.image_tools)

        async def _generate_image(state):
            return await generate_image_node(state, self.image_tools)

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
        thread_id: str = "default"
    ) -> dict:
        """이미지 생성 실행

        Args:
            user_prompt: 사용자 입력 텍스트
            thread_id: 대화 스레드 ID

        Returns:
            dict: 생성 결과
                - generated_image_url: 이미지 URL
                - image_metadata: 메타데이터
                - status: 상태
        """
        try:
            logger.info(f"Starting image generation for prompt: {user_prompt[:100]}...")

            # 초기 상태 구성
            initial_state = {
                "messages": [HumanMessage(content=user_prompt)],
                "user_prompt": user_prompt,
                "extracted_keywords": [],
                "optimized_prompt": "",
                "generated_image_url": None,
                "image_metadata": None,
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
