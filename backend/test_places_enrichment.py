"""Places Enrichment 통합 테스트

recommendation_agent의 enrich_with_places_node가 정상 동작하는지 테스트합니다.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from src.agents.recommendation_agent.nodes import enrich_with_places_node


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_enrich_with_places():
    """enrich_with_places_node 테스트"""
    print_separator("enrich_with_places_node 테스트")

    # 테스트용 목업 상태 (파싱 완료 후 상태)
    mock_state = {
        "messages": [],
        "user_preferences": {"mood": "romantic"},
        "concept": "flaneur",
        "travel_scene": None,
        "travel_destination": None,
        "llm_provider": "openai",
        "model": "gpt-4o",
        "user_profile": {},
        "system_prompt": "",
        "user_prompt": "",
        "raw_response": "",
        "destinations": [
            {
                "id": "dest_1",
                "name": "카페 드 플로르",
                "city": "파리",
                "country": "프랑스",
                "description": "파리의 유명한 카페",
                "matchReason": "로맨틱한 분위기",
                "bestTimeToVisit": "봄",
                "photographyScore": 9,
                "transportAccessibility": "easy",
                "safetyRating": 9,
                "tags": ["cafe", "paris"],
                "photographyTips": ["오후 골든아워 촬영 추천"],
                "activities": [],
            },
            {
                "id": "dest_2",
                "name": "몽마르트르 언덕",
                "city": "파리",
                "country": "프랑스",
                "description": "예술가들의 언덕",
                "matchReason": "예술적 분위기",
                "bestTimeToVisit": "가을",
                "photographyScore": 10,
                "transportAccessibility": "moderate",
                "safetyRating": 8,
                "tags": ["art", "paris"],
                "photographyTips": ["일출 촬영 추천"],
                "activities": [],
            },
        ],
        "status": "parsing",
        "error": None,
    }

    print(f"입력 여행지: {len(mock_state['destinations'])}개")
    for dest in mock_state["destinations"]:
        print(f"  - {dest['name']} ({dest['city']}, {dest['country']})")

    # enrich_with_places_node 실행
    print("\nGoogle Places API로 정보 보강 중...")
    result = await enrich_with_places_node(mock_state)

    print(f"\n결과 상태: {result['status']}")
    print(f"보강된 여행지: {len(result['destinations'])}개")

    # 결과 출력
    for dest in result["destinations"]:
        print(f"\n{'─'*40}")
        print(f"여행지: {dest['name']}")
        print(f"위치: {dest['city']}, {dest['country']}")

        place_details = dest.get("placeDetails")
        if place_details:
            print(f"\n[Google Places 정보]")
            print(f"  Google 장소명: {place_details.get('google_name')}")
            print(f"  평점: {place_details.get('rating')} ({place_details.get('user_ratings_total', 0)}개 리뷰)")
            print(f"  주소: {place_details.get('google_address')}")
            print(f"  전화: {place_details.get('phone')}")
            print(f"  웹사이트: {place_details.get('website')}")
            print(f"  Google Maps: {place_details.get('google_maps_url')}")

            opening_hours = place_details.get("opening_hours", [])
            if opening_hours:
                print(f"  영업시간:")
                for hours in opening_hours[:3]:
                    print(f"    - {hours}")

            photos = place_details.get("photos", [])
            print(f"  사진: {len(photos)}개")
            if photos:
                print(f"    첫 번째 사진 URL: {photos[0].get('url', '')[:60]}...")

            reviews = place_details.get("reviews", [])
            print(f"  리뷰: {len(reviews)}개")
            if reviews:
                first_review = reviews[0]
                print(f"    첫 번째 리뷰: {first_review.get('author')} - ⭐{first_review.get('rating')}")
                review_text = first_review.get('text', '')[:100]
                print(f"    내용: {review_text}...")
        else:
            print("  [Places 정보 없음]")

    print_separator("테스트 완료")
    return result


async def main():
    print("\n" + "="*60)
    print("  Places Enrichment 통합 테스트")
    print("="*60)

    # API 키 확인
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    if not api_key:
        print("\n[ERROR] GOOGLE_MAP_API_KEY가 설정되지 않았습니다.")
        return

    print(f"\n[OK] API 키 설정됨: {api_key[:15]}...")

    try:
        await test_enrich_with_places()
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
