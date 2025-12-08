"""여행지 추천 Agent의 State 정의"""
from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class UserPreferences(TypedDict, total=False):
    """사용자 선호도"""
    mood: Optional[str]
    aesthetic: Optional[str]
    duration: Optional[str]
    interests: list[str]


class Activity(TypedDict, total=False):
    """액티비티 정보"""
    name: str
    description: str
    duration: str
    bestTime: str
    localTip: str
    photoOpportunity: str


class PlacePhoto(TypedDict, total=False):
    """Google Places 사진 정보"""
    reference: str
    url: Optional[str]
    width: Optional[int]
    height: Optional[int]


class PlaceReview(TypedDict, total=False):
    """Google Places 리뷰 정보"""
    author: str
    rating: int
    text: str
    time: str


class PlaceDetails(TypedDict, total=False):
    """Google Places API에서 가져온 장소 상세 정보"""
    place_id: Optional[str]
    google_name: Optional[str]
    google_address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    google_maps_url: Optional[str]
    rating: Optional[float]
    user_ratings_total: Optional[int]
    price_level: Optional[int]
    opening_hours: list[str]
    is_open_now: Optional[bool]
    photos: list[PlacePhoto]
    reviews: list[PlaceReview]
    location: Optional[dict]  # {"lat": float, "lng": float}


class Destination(TypedDict, total=False):
    """여행지 정보"""
    id: str
    name: str
    city: str
    country: str
    description: str
    matchReason: str
    localVibe: Optional[str]
    whyHidden: Optional[str]
    bestTimeToVisit: str
    photographyScore: int
    transportAccessibility: str
    safetyRating: int
    estimatedBudget: Optional[str]
    tags: list[str]
    photographyTips: list[str]
    storyPrompt: Optional[str]
    activities: list[Activity]
    # Google Places API 연동 데이터
    placeDetails: Optional[PlaceDetails]


class RecommendationState(TypedDict):
    """여행지 추천 Agent의 상태 스키마

    Attributes:
        messages: 대화 메시지 히스토리
        user_preferences: 사용자 선호도 정보
        concept: 선택한 컨셉 (flaneur, filmlog, midnight)
        travel_scene: 꿈꾸는 여행 장면 설명
        travel_destination: 관심 있는 지역
        system_prompt: 생성된 시스템 프롬프트
        user_prompt: 생성된 사용자 프롬프트
        raw_response: GPT-4o 원본 응답
        destinations: 추천된 여행지 목록
        user_profile: 사용자 프로필 요약
        status: 현재 작업 상태
        error: 에러 메시지 (있을 경우)
    """
    # LangGraph 메시지 관리
    messages: Annotated[list[BaseMessage], add_messages]

    # 입력 데이터
    user_preferences: UserPreferences
    concept: Optional[str]
    travel_scene: Optional[str]
    travel_destination: Optional[str]
    llm_provider: Optional[str]  # LLM Provider 타입 ("openai", "gemini")
    model: Optional[str]  # 사용할 LLM 모델 (동적 설정)

    # 중간 처리 데이터
    user_profile: dict
    system_prompt: str
    user_prompt: str
    raw_response: str

    # 출력 데이터
    destinations: list[Destination]

    # 상태 관리
    status: Literal["pending", "analyzing", "building", "generating", "parsing", "completed", "failed"]
    error: Optional[str]


class RecommendationInput(TypedDict):
    """Agent 입력 스키마"""
    preferences: UserPreferences
    concept: Optional[str]
    travel_scene: Optional[str]
    travel_destination: Optional[str]


class RecommendationOutput(TypedDict):
    """Agent 출력 스키마"""
    destinations: list[Destination]
    user_profile: dict
    status: str
    is_fallback: bool
