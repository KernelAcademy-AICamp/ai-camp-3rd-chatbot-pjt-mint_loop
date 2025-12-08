"""여행지 추천 API 모듈"""
import json
from typing import Optional, Literal

import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

# OpenAI 클라이언트 (환경변수 OPENAI_API_KEY 자동 사용)
openai_client = AsyncOpenAI()

# 타입 정의
Concept = Literal["flaneur", "filmlog", "midnight"]
Mood = Literal["romantic", "adventurous", "nostalgic", "peaceful"]

# 컨셉별 분위기 키워드
CONCEPT_VIBES: dict[str, str] = {
    "flaneur": "도시 산책자, 문학적 감성, 카페 문화, 예술가의 영혼, 보헤미안",
    "filmlog": "필름 카메라, 빈티지, 노스탤지어, 아날로그 감성, 따뜻한 추억",
    "midnight": "밤의 예술, 재즈, 1920년대, 보헤미안 밤문화, 신비로운 분위기",
}

# 무드별 키워드
MOOD_KEYWORDS: dict[str, str] = {
    "romantic": "로맨틱, 사랑스러운, 감성적인 골목, 석양, 와인",
    "adventurous": "모험, 탐험, 숨겨진 길, 현지인만 아는, 발견의 기쁨",
    "nostalgic": "향수, 옛 추억, 빈티지, 시간여행, 과거의 아름다움",
    "peaceful": "평화로운, 고요한, 명상적, 자연, 힐링",
}


class UserPreferences(BaseModel):
    """사용자 선호도"""
    mood: Optional[str] = None
    aesthetic: Optional[str] = None
    duration: Optional[str] = None
    interests: list[str] = []


class RecommendationRequest(BaseModel):
    """여행지 추천 요청"""
    preferences: UserPreferences
    concept: Optional[str] = None
    travelScene: Optional[str] = None
    travelDestination: Optional[str] = None


class Activity(BaseModel):
    """액티비티 정보"""
    name: str
    description: str
    duration: str
    bestTime: str
    localTip: str
    photoOpportunity: str


class Destination(BaseModel):
    """여행지 정보"""
    id: str
    name: str
    city: str
    country: str
    description: str
    matchReason: str
    localVibe: Optional[str] = None
    whyHidden: Optional[str] = None
    bestTimeToVisit: str
    photographyScore: int
    transportAccessibility: str
    safetyRating: int
    estimatedBudget: Optional[str] = None
    tags: list[str] = []
    photographyTips: list[str] = []
    storyPrompt: Optional[str] = None
    activities: list[Activity] = []


class RecommendationResponse(BaseModel):
    """여행지 추천 응답"""
    status: str
    destinations: list[Destination]
    userProfile: Optional[dict] = None
    isFallback: bool = False


async def generate_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """여행지 추천 생성"""
    try:
        preferences = request.preferences
        concept = request.concept
        travel_scene = request.travelScene
        travel_destination = request.travelDestination

        logger.info(f"Recommendations request: mood={preferences.mood}, concept={concept}")

        # 프롬프트 구성
        concept_vibe = CONCEPT_VIBES.get(concept, "") if concept else ""
        mood_keyword = MOOD_KEYWORDS.get(preferences.mood, "") if preferences.mood else ""
        interests_str = ", ".join(preferences.interests) if preferences.interests else ""

        system_prompt = """당신은 Trip Kit의 AI 여행 큐레이터입니다. 사용자의 감성과 취향을 깊이 이해하고, 관광객들이 모르는 "진짜 현지 감성"을 가진 숨겨진 명소를 추천합니다.
            핵심 원칙:
            1. 과도하게 유명하거나 관광스러운 장소는 절대 추천하지 않습니다
            2. 현지인들이 사랑하는 숨겨진 로컬 스폿 중심으로 추천합니다
            3. 인생샷을 남길 수 있는 포토제닉한 장소를 우선합니다
            4. 각 장소에서 할 수 있는 특별한 경험/액티비티를 함께 제안합니다
            5. "여행은 단순히 가는 것이 아니라 기록을 만드는 경험"이라는 철학을 담습니다"""

        user_prompt = f"""사용자 프로필:
            - 무드: {preferences.mood or '감성적인'} ({mood_keyword})
            - 미학적 취향: {preferences.aesthetic or '빈티지'}
            - 관심사: {interests_str or '사진, 예술'}
            - 선택한 컨셉: {concept or 'filmlog'} ({concept_vibe})
            - 꿈꾸는 여행 장면: {travel_scene or '특별한 순간을 기록하는 여행'}
            {f'- 관심 있는 지역: {travel_destination}' if travel_destination else ''}

            위 프로필을 바탕으로, 이 사용자에게 완벽하게 맞는 숨겨진 여행지 3곳을 추천해주세요.

            다음 JSON 형식으로 응답해주세요:
            {{
            "destinations": [
                {{
                "id": "dest_1",
                "name": "장소 이름 (특별한 수식어 포함)",
                "city": "도시명",
                "country": "국가명",
                "description": "이 장소의 특별한 매력을 감성적으로 설명 (3-4문장)",
                "matchReason": "사용자의 취향에 맞는 구체적인 이유 (2-3문장)",
                "localVibe": "현지 분위기를 한 문장으로",
                "whyHidden": "왜 숨겨진 명소인지 설명",
                "bestTimeToVisit": "추천 방문 시기와 이유",
                "photographyScore": 8-10,
                "transportAccessibility": "easy|moderate|challenging",
                "safetyRating": 7-10,
                "estimatedBudget": "$|$$|$$$",
                "tags": ["관련 태그 3-5개"],
                "photographyTips": ["사진 촬영 팁 2-3개"],
                "storyPrompt": "이 장소에서 만들 수 있는 나만의 스토리 제안",
                "activities": [
                    {{
                    "name": "액티비티명",
                    "description": "경험 설명",
                    "duration": "소요 시간",
                    "bestTime": "추천 시간대",
                    "localTip": "현지인 팁",
                    "photoOpportunity": "포토 스팟 설명"
                    }}
                ]
                }}
            ]
            }}
        각 장소마다 2-3개의 특별한 액티비티를 포함해주세요."""

        # GPT-4o 호출
        completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
        )

        response_content = completion.choices[0].message.content
        if not response_content:
            raise ValueError("No response from OpenAI")

        parsed_response = json.loads(response_content)
        destinations = parsed_response.get("destinations", [])

        logger.info(f"Generated {len(destinations)} recommendations")

        return RecommendationResponse(
            status="success",
            destinations=destinations,
            userProfile={
                "mood": preferences.mood,
                "aesthetic": preferences.aesthetic,
                "concept": concept,
                "travelScene": travel_scene,
            },
        )

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return RecommendationResponse(
            status="success",
            destinations=get_fallback_destinations(),
            isFallback=True,
        )


def get_fallback_destinations() -> list[dict]:
    """폴백 여행지 데이터"""
    return [
        {
            "id": "dest_fallback_1",
            "name": "핀란드 로바니에미 산타마을의 순백 겨울",
            "city": "로바니에미",
            "country": "핀란드",
            "description": "북극선 위에 위치한 진짜 산타의 고향.",
            "matchReason": "동화 속 크리스마스를 꿈꾸셨다면 완벽한 곳입니다.",
            "localVibe": "눈 내리는 고요 속 따뜻한 핫초코 한 잔의 여유",
            "whyHidden": "진짜 매력은 주변 숲속 오두막에 있습니다",
            "bestTimeToVisit": "12월 중순 - 1월",
            "photographyScore": 10,
            "transportAccessibility": "moderate",
            "safetyRating": 10,
            "estimatedBudget": "$$$",
            "tags": ["winter", "aurora", "snow"],
            "photographyTips": ["오로라 촬영 시 삼각대 필수"],
            "storyPrompt": "오로라 아래서 소원을 빌다",
            "activities": [],
        },
        {
            "id": "dest_fallback_2",
            "name": "프랑스 고르드, 중세로의 시간 여행",
            "city": "고르드",
            "country": "프랑스",
            "description": "프로방스의 절벽 위에 매달린 듯한 중세 마을.",
            "matchReason": "빈티지와 역사를 사랑하신다면 완벽해요.",
            "localVibe": "라벤더 향기 속 중세의 발자국",
            "whyHidden": "에펠탑에 가려져 있지만 진짜 프랑스 감성",
            "bestTimeToVisit": "6월 말 - 7월 초",
            "photographyScore": 10,
            "transportAccessibility": "challenging",
            "safetyRating": 9,
            "estimatedBudget": "$$",
            "tags": ["medieval", "provence", "lavender"],
            "photographyTips": ["일몰에 마을 전경을 담으세요"],
            "storyPrompt": "중세 돌담길을 거닐다",
            "activities": [],
        },
        {
            "id": "dest_fallback_3",
            "name": "일본 나오시마, 예술이 숨 쉬는 섬",
            "city": "나오시마",
            "country": "일본",
            "description": "세토 내해의 작은 섬 전체가 미술관.",
            "matchReason": "예술과 자연의 조화를 사랑하신다면 완벽해요.",
            "localVibe": "파도 소리와 함께 예술을 감상하는 오후",
            "whyHidden": "외국인에겐 아직 숨겨진 보석",
            "bestTimeToVisit": "4-5월 또는 10-11월",
            "photographyScore": 10,
            "transportAccessibility": "moderate",
            "safetyRating": 10,
            "estimatedBudget": "$$",
            "tags": ["art", "island", "architecture"],
            "photographyTips": ["노란 호박은 해질녘에"],
            "storyPrompt": "섬 전체가 캔버스인 곳에서",
            "activities": [],
        },
    ]
