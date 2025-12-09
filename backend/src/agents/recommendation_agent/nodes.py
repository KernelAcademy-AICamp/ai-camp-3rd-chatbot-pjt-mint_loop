"""여행지 추천 Agent의 워크플로우 노드 구현

각 노드는 RecommendationState를 입력받아 업데이트된 상태를 반환합니다.
Strategy Pattern을 통해 OpenAI/Gemini 등 다양한 LLM Provider를 지원합니다.
Google Places API를 통해 추가적인 장소 정보를 enrichment합니다.
"""
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import structlog
from langchain_core.messages import AIMessage

from .state import RecommendationState, Destination, PlaceDetails
from ...providers import get_llm_provider, LLMGenerationParams

# Google Maps 클라이언트 (Places API용)
try:
    import googlemaps
    _GOOGLE_MAPS_CREDENTIAL = os.getenv("GOOGLE_MAP_API_KEY")
    # 플레이스홀더 값이나 빈 값은 무시
    if _GOOGLE_MAPS_CREDENTIAL and not _GOOGLE_MAPS_CREDENTIAL.startswith("your-"):
        try:
            gmaps_client = googlemaps.Client(key=_GOOGLE_MAPS_CREDENTIAL)
        except ValueError:
            # Invalid API key
            gmaps_client = None
    else:
        gmaps_client = None
except ImportError:
    gmaps_client = None


logger = structlog.get_logger(__name__)

# 기본 설정 (gpt-4o-mini: 5-10초, gpt-4o: 30-40초)
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


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

        # 이미지 생성 컨텍스트 추출
        image_context = state.get("image_generation_context") or {}
        image_destination = image_context.get("destination", "")
        image_additional_prompt = image_context.get("additionalPrompt", "")
        image_film_stock = image_context.get("filmStock", "")
        image_outfit_style = image_context.get("outfitStyle", "")

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
            # 이미지 생성 컨텍스트 추가
            "image_destination": image_destination,
            "image_additional_prompt": image_additional_prompt,
            "image_film_stock": image_film_stock,
            "image_outfit_style": image_outfit_style,
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

    분석된 사용자 프로필을 기반으로 LLM 호출에 사용할
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

        # 이미지 생성 컨텍스트 라인들
        image_destination = user_profile.get("image_destination")
        image_additional_prompt = user_profile.get("image_additional_prompt")
        image_film_stock = user_profile.get("image_film_stock")
        image_outfit_style = user_profile.get("image_outfit_style")

        image_context_lines = []
        if image_destination:
            image_context_lines.append(f"- 이전에 미리보기 생성한 여행지: {image_destination}")
        if image_additional_prompt:
            image_context_lines.append(f"- 미리보기에서 묘사한 장면: {image_additional_prompt}")
        if image_film_stock:
            image_context_lines.append(f"- 선호하는 필름 스타일: {image_film_stock}")
        if image_outfit_style:
            image_context_lines.append(f"- 선호하는 의상 스타일: {image_outfit_style}")

        image_context_section = "\n".join(image_context_lines) if image_context_lines else ""

        # 이미지 미리보기 컨텍스트가 있으면 중요 참고 정보로 추가
        image_context_intro = ""
        if image_context_section:
            image_context_intro = f"""
[중요] 사용자가 이전에 생성한 이미지 미리보기 정보:
{image_context_section}
→ 이 정보를 반드시 참고하여 사용자가 관심 가진 지역과 비슷한 분위기의 여행지를 추천해주세요.
"""

        user_prompt = f"""사용자 프로필:
- 무드: {user_profile.get('mood') or '감성적인'} ({user_profile.get('mood_keywords', '')})
- 미학적 취향: {user_profile.get('aesthetic') or '빈티지'}
- 관심사: {user_profile.get('interests') or '사진, 예술'}
- 선택한 컨셉: {user_profile.get('concept') or 'filmlog'} ({user_profile.get('concept_vibe', '')})
- 꿈꾸는 여행 장면: {user_profile.get('travel_scene') or '특별한 순간을 기록하는 여행'}
{destination_line}
{image_context_intro}
위 프로필을 바탕으로, 숨겨진 여행지 3곳을 추천해주세요. 간결하게 JSON으로 응답:

{{"destinations": [
  {{"id": "dest_1", "name": "장소명", "city": "도시", "country": "국가", "description": "2문장 설명", "matchReason": "1문장", "tags": ["태그3개"], "photographyScore": 9, "estimatedBudget": "$$"}}
]}}"""

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
    provider_type: str | None = None,
    model: str | None = None
) -> RecommendationState:
    """추천 생성 노드

    LLMProvider를 통해 여행지 추천을 생성합니다.
    Strategy Pattern으로 OpenAI/Gemini 등 다양한 Provider를 지원합니다.

    Args:
        state: 현재 상태
        provider_type: 사용할 Provider 타입 ("openai", "gemini")
        model: 사용할 모델 (None이면 Provider 기본값 사용)
    """
    try:
        # Provider 타입 결정: 인자 > state > 환경변수 > 기본값
        actual_provider_type = (
            provider_type
            or state.get("llm_provider")
            or os.getenv("LLM_PROVIDER")
            or DEFAULT_LLM_PROVIDER
        )

        # 모델 결정: 인자 > state > 환경변수 > Provider 기본값
        actual_model = (
            model
            or state.get("model")
            or os.getenv("LLM_MODEL")
        )

        logger.info(
            f"Generating recommendations via {actual_provider_type}",
            provider=actual_provider_type,
            model=actual_model or "default"
        )

        # LLM Provider 가져오기 (Strategy Pattern)
        llm_provider = get_llm_provider(actual_provider_type)

        # 모델이 지정되지 않았으면 Provider 기본값 사용
        if not actual_model:
            actual_model = llm_provider.default_model

        system_prompt = state["system_prompt"]
        user_prompt = state["user_prompt"]

        # LLM 생성 파라미터 구성
        params = LLMGenerationParams(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            response_format="json",
        )

        # LLM 호출
        result = await llm_provider.generate(params, model=actual_model)

        if not result.success:
            raise ValueError(f"LLM 생성 실패: {result.error}")

        response_content = result.content
        if not response_content:
            raise ValueError("LLM 응답이 비어있습니다")

        logger.info(
            f"LLM response received successfully",
            provider=actual_provider_type,
            model=actual_model,
        )

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content=f"{actual_provider_type} ({actual_model}) 추천 생성 완료")
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

    LLM 응답을 파싱하여 구조화된 여행지 목록으로 변환합니다.
    파싱 실패 시 폴백 데이터를 반환합니다.
    """
    try:
        logger.info("Parsing LLM response")

        raw_response = state.get("raw_response", "")

        if not raw_response:
            raise ValueError("No raw response to parse")

        # JSON 파싱 시도
        try:
            parsed_response = json.loads(raw_response)
        except json.JSONDecodeError:
            # 마크다운 코드블록으로 감싸져 있을 수 있음
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
            if json_match:
                parsed_response = json.loads(json_match.group(1))
            else:
                # 텍스트에서 JSON 추출 시도
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


def _enrich_single_destination_sync(dest: dict, maps_credential: str) -> dict:
    """단일 여행지에 대한 Google Places API 정보 보강 (동기 함수)

    googlemaps 라이브러리가 동기 방식이므로, ThreadPoolExecutor에서 실행됩니다.
    """
    if not gmaps_client:
        return dest

    try:
        # 검색어 구성: 장소명 + 도시 + 국가
        search_query = f"{dest.get('name', '')} {dest.get('city', '')} {dest.get('country', '')}"
        logger.info(f"Searching places for: {search_query}")

        # 장소 검색
        search_result = gmaps_client.places(
            query=search_query,
            language="ko"
        )

        places = search_result.get("results", [])
        if not places:
            logger.info(f"No places found for {search_query}")
            return dest

        # 첫 번째 결과의 place_id로 상세 정보 조회
        place = places[0]
        place_id = place.get("place_id")

        if not place_id:
            return dest

        # 상세 정보 조회
        detail_result = gmaps_client.place(
            place_id=place_id,
            language="ko",
            fields=[
                "name",
                "formatted_address",
                "formatted_phone_number",
                "website",
                "url",
                "rating",
                "user_ratings_total",
                "reviews",
                "opening_hours",
                "price_level",
                "type",
                "geometry",
                "photo",
            ]
        )

        place_detail = detail_result.get("result", {})

        # 사진 정보 처리
        photos = []
        for photo in place_detail.get("photos", [])[:5]:
            photo_ref = photo.get("photo_reference")
            if photo_ref:
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={maps_credential}"
                photos.append({
                    "reference": photo_ref,
                    "url": photo_url,
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                })

        # 리뷰 정보 처리
        reviews = []
        for review in place_detail.get("reviews", [])[:5]:
            reviews.append({
                "author": review.get("author_name"),
                "rating": review.get("rating"),
                "text": review.get("text"),
                "time": review.get("relative_time_description"),
            })

        # PlaceDetails 구성
        place_details: PlaceDetails = {
            "place_id": place_id,
            "google_name": place_detail.get("name"),
            "google_address": place_detail.get("formatted_address"),
            "phone": place_detail.get("formatted_phone_number"),
            "website": place_detail.get("website"),
            "google_maps_url": place_detail.get("url"),
            "rating": place_detail.get("rating"),
            "user_ratings_total": place_detail.get("user_ratings_total"),
            "price_level": place_detail.get("price_level"),
            "opening_hours": place_detail.get("opening_hours", {}).get("weekday_text", []),
            "is_open_now": place_detail.get("opening_hours", {}).get("open_now"),
            "photos": photos,
            "reviews": reviews,
            "location": place_detail.get("geometry", {}).get("location"),
        }

        enriched_dest = {**dest, "placeDetails": place_details}
        logger.info(f"Enriched {dest.get('name')} with rating={place_details.get('rating')}")
        return enriched_dest

    except Exception as e:
        logger.error(f"Failed to enrich destination {dest.get('name')}: {e}")
        return dest


async def enrich_destinations_parallel(destinations: list[dict]) -> list[dict]:
    """여러 여행지에 대해 Google Places API 정보를 병렬로 보강

    동기 googlemaps 라이브러리를 ThreadPoolExecutor로 감싸서
    asyncio.gather로 병렬 실행합니다.

    Args:
        destinations: 보강할 여행지 목록

    Returns:
        placeDetails가 추가된 여행지 목록
    """
    if not gmaps_client or not destinations:
        return destinations

    maps_credential = _GOOGLE_MAPS_CREDENTIAL or ""

    loop = asyncio.get_event_loop()

    # ThreadPoolExecutor를 사용하여 동기 함수를 병렬로 실행
    with ThreadPoolExecutor(max_workers=min(len(destinations), 5)) as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                partial(_enrich_single_destination_sync, dest, maps_credential)
            )
            for dest in destinations
        ]
        enriched = await asyncio.gather(*tasks, return_exceptions=True)

    # 예외 처리: 실패한 경우 원본 반환
    result = []
    for i, enriched_dest in enumerate(enriched):
        if isinstance(enriched_dest, Exception):
            logger.error(f"Enrichment failed for destination {i}: {enriched_dest}")
            result.append(destinations[i])
        else:
            result.append(enriched_dest)

    return result


async def enrich_with_places_node(state: RecommendationState) -> RecommendationState:
    """Google Places API로 여행지 정보 보강 노드 (병렬 처리)

    추천된 각 여행지에 대해 Google Places API를 병렬로 호출하여
    실제 장소 정보(평점, 리뷰, 사진, 영업시간 등)를 추가합니다.
    """
    try:
        if not gmaps_client:
            logger.warning("Google Maps client not available, skipping places enrichment")
            return {
                **state,
                "status": "completed"
            }

        destinations = state.get("destinations", [])
        if not destinations:
            logger.info("No destinations to enrich")
            return {
                **state,
                "status": "completed"
            }

        logger.info(f"Enriching {len(destinations)} destinations with Places API data (parallel)")

        # 병렬로 모든 여행지 정보 보강
        enriched_destinations = await enrich_destinations_parallel(destinations)

        # 메시지 추가
        new_messages = state["messages"] + [
            AIMessage(content=f"Google Places API로 {len(enriched_destinations)}개 여행지 정보를 보강했습니다.")
        ]

        return {
            **state,
            "messages": new_messages,
            "destinations": enriched_destinations,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Places enrichment failed: {e}")
        return {
            **state,
            "status": "completed",  # 실패해도 기존 데이터로 완료 처리
            "error": str(e)
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
