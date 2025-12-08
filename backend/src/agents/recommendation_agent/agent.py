"""여행지 추천 LangGraph Agent

Strategy Pattern을 통해 OpenAI/Gemini 등 다양한 LLM Provider를 지원합니다.
기본 Provider: OpenAI (gpt-4o)
"""
import os
import structlog
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import RecommendationState, RecommendationInput, RecommendationOutput
from .nodes import (
    analyze_preferences_node,
    build_prompt_node,
    generate_recommendations_node,
    parse_response_node,
    get_fallback_destinations,
)

logger = structlog.get_logger(__name__)

# 기본 설정
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")


class RecommendationAgent:
    """여행지 추천 Agent

    LangGraph를 사용하여 구현된 여행지 추천 워크플로우:
    1. 사용자 선호도 분석
    2. 프롬프트 구성
    3. LLM 추천 생성 (OpenAI/Gemini 선택 가능)
    4. 응답 파싱

    Strategy Pattern을 통해 다양한 LLM Provider를 지원합니다.
    """

    def __init__(
        self,
        provider_type: str | None = None,
        model: str | None = None,
        checkpointer: MemorySaver | None = None
    ):
        """Agent 초기화

        Args:
            provider_type: LLM Provider 타입 ("openai", "gemini")
            model: 사용할 LLM 모델 (기본값: Provider별 기본 모델)
            checkpointer: 체크포인터 (선택사항)
        """
        self.provider_type = provider_type or DEFAULT_LLM_PROVIDER
        self.model = model or DEFAULT_LLM_MODEL
        self.checkpointer = checkpointer or MemorySaver()

        # 그래프 빌드
        self.graph = self._build_graph()

        logger.info(
            "RecommendationAgent initialized",
            provider=self.provider_type,
            model=self.model
        )

    def _build_graph(self):
        """LangGraph 워크플로우 구축"""

        # StateGraph 생성 (전체 상태 스키마 사용)
        workflow = StateGraph(RecommendationState)

        # Provider 타입과 모델을 인자로 전달하는 래퍼 함수
        async def _generate_recommendations(state):
            return await generate_recommendations_node(
                state,
                provider_type=self.provider_type,
                model=self.model
            )

        # 노드 추가
        workflow.add_node("analyze_preferences", analyze_preferences_node)
        workflow.add_node("build_prompt", build_prompt_node)
        workflow.add_node("generate_recommendations", _generate_recommendations)
        workflow.add_node("parse_response", parse_response_node)

        # 엣지 정의
        workflow.set_entry_point("analyze_preferences")
        workflow.add_edge("analyze_preferences", "build_prompt")
        workflow.add_edge("build_prompt", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "parse_response")
        workflow.add_edge("parse_response", END)

        # 컴파일
        return workflow.compile(
            checkpointer=self.checkpointer,
            debug=True
        )

    async def recommend(
        self,
        input_data: RecommendationInput,
        thread_id: str = "default",
        provider_type: str | None = None,
        model: str | None = None
    ) -> RecommendationOutput:
        """여행지 추천 실행

        Args:
            input_data: 사용자 입력 데이터
                - preferences: 사용자 선호도
                - concept: 선택한 컨셉
                - travel_scene: 꿈꾸는 여행 장면
                - travel_destination: 관심 지역
            thread_id: 대화 스레드 ID
            provider_type: 이 요청에서 사용할 Provider (선택, 인스턴스 기본값 오버라이드)
            model: 이 요청에서 사용할 모델 (선택, 인스턴스 기본값 오버라이드)

        Returns:
            RecommendationOutput: 추천 결과
                - destinations: 추천 여행지 목록
                - user_profile: 분석된 사용자 프로필
                - status: 상태
                - is_fallback: 폴백 데이터 사용 여부
        """
        try:
            # 요청별 오버라이드 가능
            actual_provider = provider_type or self.provider_type
            actual_model = model or self.model

            logger.info(
                "Starting recommendation generation",
                concept=input_data.get("concept"),
                destination=input_data.get("travel_destination"),
                provider=actual_provider,
                model=actual_model
            )

            # 초기 상태 구성
            initial_state: RecommendationState = {
                "messages": [HumanMessage(content="여행지 추천을 요청합니다.")],
                "user_preferences": input_data.get("preferences", {}),
                "concept": input_data.get("concept"),
                "travel_scene": input_data.get("travel_scene"),
                "travel_destination": input_data.get("travel_destination"),
                "llm_provider": actual_provider,
                "model": actual_model,
                "user_profile": {},
                "system_prompt": "",
                "user_prompt": "",
                "raw_response": "",
                "destinations": [],
                "status": "pending",
                "error": None
            }

            # 그래프 실행
            config = {"configurable": {"thread_id": thread_id}}
            result = await self.graph.ainvoke(initial_state, config)

            logger.info(f"Recommendation completed with status: {result['status']}")

            return {
                "destinations": result.get("destinations", []),
                "user_profile": result.get("user_profile", {}),
                "status": result["status"],
                "is_fallback": False
            }

        except Exception as e:
            logger.error(f"Recommendation failed: {e}")

            # 폴백 응답 반환
            return {
                "destinations": get_fallback_destinations(),
                "user_profile": {},
                "status": "completed",
                "is_fallback": True
            }
