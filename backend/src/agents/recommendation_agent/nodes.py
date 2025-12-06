"""여행지 추천 Agent의 워크플로우 노드 구현

각 노드는 RecommendationState를 입력받아 업데이트된 상태를 반환합니다.
Google Gemini (gemini-2.5-pro) 모델을 사용합니다.
"""
import json
import os
import structlog
from langchain_core.messages import AIMessage

from .state import RecommendationState, Destination


logger = structlog.get_logger(__name__)

# 기본 모델 설정
DEFAULT_TEXT_MODEL = "gemini-2.5-flash"


def _get_gemini_credential() -> str | None:
    """Gemini API 키를 환경변수에서 가져옴"""
    # GEMINI_API_KEY 우선, 없으면 GOOGLE_API_KEY
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def get_gemini_client():
    """Google Gemini 클라이언트 반환 (lazy initialization)"""
    try:
        from google import genai
        credential = _get_gemini_credential()
        if not credential:
            raise ValueError("GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수가 필요합니다")
        return genai.Client(api_key=credential)
    except ImportError:
        raise ImportError(
            "google-genai 패키지가 필요합니다. "
            "pip install google-genai 로 설치하세요."
        )


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


async def analyze_preferences_node(state: RecommendationState) -> RecommendationState:
    """사용자 선호도 분석 노드

    사용자의 선호도, 컨셉, 여행 장면 등을 분석하여
    프롬프트 생성에 필요한 정보를 추출합니다.
    """
    try:
        logger.info("Analyzing user preferences")

        preferences = state["user_preferences"]
        concept = state.get("concept")
        mood = preferences.get("mood")

        # 컨셉/무드 키워드 추출
        concept_vibe = CONCEPT_VIBES.get(concept, "") if concept else ""
        mood_keyword = MOOD_KEYWORDS.get(mood, "") if mood else ""
        interests_str = ", ".join(preferences.get("interests", [])) if preferences.get("interests") else ""

        # 사용자 프로필 구성
        user_profile = {
            "mood": mood,
            "mood_keywords": mood_keyword,
            "aesthetic": preferences.get("aesthetic"),
            "concept": concept,
            "concept_vibe": concept_vibe,
            "interests": interests_str,
            "travel_scene": state.get("travel_scene"),
            "travel_destination": state.get("travel_destination"),
        }

        logger.info(f"User profile analyzed: mood={mood}, concept={concept}")

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content=f"사용자 선호도 분석 완료: {mood} 무드, {concept} 컨셉")
        ]

        return {
            **state,
            "messages": new_messages,
            "user_profile": user_profile,
            "status": "analyzing"
        }

    except Exception as e:
        logger.error(f"Preference analysis failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }


async def build_prompt_node(state: RecommendationState) -> RecommendationState:
    """프롬프트 구성 노드

    분석된 사용자 프로필을 기반으로 Gemini 호출에 사용할
    시스템 프롬프트와 사용자 프롬프트를 생성합니다.
    """
    try:
        logger.info("Building prompts for recommendation generation")

        user_profile = state["user_profile"]

        system_prompt = """당신은 Trip Kit의 AI 여행 큐레이터입니다. 사용자의 감성과 취향을 깊이 이해하고, 관광객들이 모르는 "진짜 현지 감성"을 가진 숨겨진 명소를 추천합니다.

핵심 원칙:
1. 과도하게 유명하거나 관광스러운 장소는 절대 추천하지 않습니다
2. 현지인들이 사랑하는 숨겨진 로컬 스폿 중심으로 추천합니다
3. 인생샷을 남길 수 있는 포토제닉한 장소를 우선합니다
4. 각 장소에서 할 수 있는 특별한 경험/액티비티를 함께 제안합니다
5. "여행은 단순히 가는 것이 아니라 기록을 만드는 경험"이라는 철학을 담습니다

반드시 JSON 형식으로만 응답해주세요."""

        travel_destination = user_profile.get("travel_destination")
        destination_line = f"- 관심 있는 지역: {travel_destination}" if travel_destination else ""

        user_prompt = f"""사용자 프로필:
- 무드: {user_profile.get('mood') or '감성적인'} ({user_profile.get('mood_keywords', '')})
- 미학적 취향: {user_profile.get('aesthetic') or '빈티지'}
- 관심사: {user_profile.get('interests') or '사진, 예술'}
- 선택한 컨셉: {user_profile.get('concept') or 'filmlog'} ({user_profile.get('concept_vibe', '')})
- 꿈꾸는 여행 장면: {user_profile.get('travel_scene') or '특별한 순간을 기록하는 여행'}
{destination_line}

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

        logger.info("Prompts built successfully")

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content="추천 프롬프트 구성 완료")
        ]

        return {
            **state,
            "messages": new_messages,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "status": "building"
        }

    except Exception as e:
        logger.error(f"Prompt building failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }


async def generate_recommendations_node(
    state: RecommendationState,
    model: str | None = None
) -> RecommendationState:
    """추천 생성 노드

    Google Gemini를 호출하여 여행지 추천을 생성합니다.

    Args:
        state: 현재 상태
        model: 사용할 모델 (None이면 state에서 가져오거나 기본값 사용)
    """
    try:
        # 모델 결정: 인자 > state > 환경변수 > 기본값
        actual_model = (
            model
            or state.get("model")
            or os.getenv("GEMINI_TEXT_MODEL")
            or DEFAULT_TEXT_MODEL
        )

        logger.info(f"Generating recommendations via Gemini ({actual_model})")

        system_prompt = state["system_prompt"]
        user_prompt = state["user_prompt"]

        # Gemini 클라이언트 가져오기
        client = get_gemini_client()

        # Gemini API 호출
        response = client.models.generate_content(
            model=actual_model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config={
                "temperature": 0.8,
                "response_mime_type": "application/json",
            }
        )

        response_content = response.text
        if not response_content:
            raise ValueError("No response from Gemini")

        logger.info(f"Gemini response received successfully (model: {actual_model})")

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content=f"Gemini ({actual_model}) 추천 생성 완료")
        ]

        return {
            **state,
            "messages": new_messages,
            "raw_response": response_content,
            "status": "generating"
        }

    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        return {
            **state,
            "status": "failed",
            "error": str(e)
        }


async def parse_response_node(state: RecommendationState) -> RecommendationState:
    """응답 파싱 노드

    Gemini 응답을 파싱하여 구조화된 여행지 목록으로 변환합니다.
    파싱 실패 시 폴백 데이터를 반환합니다.
    """
    try:
        logger.info("Parsing Gemini response")

        raw_response = state.get("raw_response", "")

        if not raw_response:
            raise ValueError("No raw response to parse")

        # JSON 파싱 시도
        try:
            parsed_response = json.loads(raw_response)
        except json.JSONDecodeError:
            # Gemini가 마크다운 코드블록으로 감싸서 반환할 수 있음
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
            if json_match:
                parsed_response = json.loads(json_match.group(1))
            else:
                # 그냥 텍스트에서 JSON 추출 시도
                json_start = raw_response.find('{')
                json_end = raw_response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed_response = json.loads(raw_response[json_start:json_end])
                else:
                    raise ValueError("Could not extract JSON from response")

        destinations = parsed_response.get("destinations", [])

        logger.info(f"Parsed {len(destinations)} destinations")

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content=f"추천 완료! {len(destinations)}개의 숨겨진 여행지를 찾았습니다.")
        ]

        return {
            **state,
            "messages": new_messages,
            "destinations": destinations,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Response parsing failed: {e}, using fallback")

        # 폴백 데이터 반환
        fallback_destinations = get_fallback_destinations()

        new_messages = state["messages"] + [
            AIMessage(content="파싱 오류로 기본 추천 데이터를 사용합니다.")
        ]

        return {
            **state,
            "messages": new_messages,
            "destinations": fallback_destinations,
            "status": "completed"
        }


def get_fallback_destinations() -> list[Destination]:
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
