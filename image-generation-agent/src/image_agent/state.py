"""이미지 생성 Agent의 State 정의"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class ImageGenerationState(TypedDict):
    """이미지 생성 Agent의 상태 스키마

    Attributes:
        messages: 대화 메시지 히스토리
        user_prompt: 사용자가 입력한 원본 텍스트
        extracted_keywords: Search MCP로부터 추출된 키워드 리스트
        optimized_prompt: 이미지 생성을 위해 최적화된 프롬프트
        generated_image_url: 생성된 이미지의 URL
        image_metadata: 이미지 메타데이터 (크기, 형식 등)
        status: 현재 작업 상태
        error: 에러 메시지 (있을 경우)
    """
    # LangGraph 메시지 관리
    messages: Annotated[list[BaseMessage], add_messages]

    # 입력 데이터
    user_prompt: str

    # 중간 처리 데이터
    extracted_keywords: list[str]
    optimized_prompt: str

    # 출력 데이터
    generated_image_url: str | None
    image_metadata: dict | None

    # 상태 관리
    status: Literal["pending", "extracting", "generating", "completed", "failed"]
    error: str | None


class ImageGenerationInput(TypedDict):
    """Agent 입력 스키마"""
    messages: list[dict]


class ImageGenerationOutput(TypedDict):
    """Agent 출력 스키마"""
    messages: list[BaseMessage]
    generated_image_url: str | None
    image_metadata: dict | None
    status: str
