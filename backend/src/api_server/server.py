"""FastAPI 서버 - 프론트엔드와 Image Provider 연결

직접 Image Provider를 사용하여 이미지를 생성합니다.
RecommendationAgent를 사용하여 여행지를 추천합니다.
"""
import os
from pathlib import Path
from typing import Optional

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# .env 파일 로드 (상위 디렉토리에서 검색)
def find_and_load_dotenv():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True
        current = current.parent
    load_dotenv()
    return False

find_and_load_dotenv()

# 상위 패키지에서 providers import
from ..providers import get_provider, get_llm_provider, ImageGenerationParams, LLMGenerationParams
# RecommendationAgent import
from ..agents import RecommendationAgent

logger = structlog.get_logger(__name__)

# 모델 설정 (환경변수에서 가져오기)
DEFAULT_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
DEFAULT_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")

# RecommendationAgent 인스턴스 (싱글톤)
recommendation_agent = RecommendationAgent(model=DEFAULT_TEXT_MODEL)

# LLM Provider 인스턴스 (프롬프트 최적화용 - OpenAI GPT 사용)
PROMPT_OPTIMIZATION_MODEL = "gpt-4o-mini"
llm_provider = get_llm_provider("openai", model=PROMPT_OPTIMIZATION_MODEL)

# 컨셉별 필름 스타일 프롬프트 매핑
CONCEPT_STYLE_PROMPTS = {
    "flaneur": "shot on Kodak Portra 400, soft natural lighting, urban street photography style, literary cafe atmosphere, intellectual bohemian aesthetic, warm muted tones, slight film grain",
    "filmlog": "shot on Kodak ColorPlus 200, warm golden hour lighting, vintage film photography, nostalgic retro aesthetic, soft warm tones, natural film grain, authentic analog feel",
    "midnight": "shot on Kodak Tri-X 400, dramatic artistic lighting, 1920s Paris bohemian atmosphere, moody cinematic style, high contrast, classic black and white or deep warm tones",
}

# 필름 스톡별 스타일 프롬프트
FILM_STOCK_PROMPTS = {
    "Kodak Portra 400": "Kodak Portra 400 film, natural skin tones, soft pastel colors, fine grain, professional portrait quality",
    "Ilford HP5 Plus": "Ilford HP5 Plus black and white film, classic grain structure, rich tonal range, timeless documentary style",
    "Kodak ColorPlus 200": "Kodak ColorPlus 200 film, warm saturated colors, nostalgic vintage look, everyday moments aesthetic",
    "Fujifilm Superia 400": "Fujifilm Superia 400 film, vibrant greens and blues, punchy colors, casual snapshot style",
    "Kodak Tri-X 400": "Kodak Tri-X 400 black and white film, iconic grain, deep blacks, legendary street photography look",
    "Ilford Delta 3200": "Ilford Delta 3200 high-speed black and white, dramatic grain, low light capability, artistic night photography",
}


class GenerateRequest(BaseModel):
    """이미지 생성 요청"""
    destination: str
    concept: str  # flaneur, filmlog, midnight
    filmStock: str
    colorPalette: list[str] = []
    outfitStyle: str = ""
    additionalPrompt: str = ""


class GenerateResponse(BaseModel):
    """이미지 생성 응답"""
    status: str
    imageUrl: Optional[str] = None
    optimizedPrompt: Optional[str] = None
    extractedKeywords: list[str] = []
    metadata: Optional[dict] = None
    error: Optional[str] = None


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


class PlacePhoto(BaseModel):
    """Google Places 사진 정보"""
    reference: str
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class PlaceReview(BaseModel):
    """Google Places 리뷰 정보"""
    author: Optional[str] = None
    rating: Optional[int] = None
    text: Optional[str] = None
    time: Optional[str] = None


class PlaceDetails(BaseModel):
    """Google Places API 상세 정보"""
    place_id: Optional[str] = None
    google_name: Optional[str] = None
    google_address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None
    opening_hours: list[str] = []
    is_open_now: Optional[bool] = None
    photos: list[PlacePhoto] = []
    reviews: list[PlaceReview] = []
    location: Optional[dict] = None


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
    # Google Places API 연동 데이터
    placeDetails: Optional[PlaceDetails] = None


class RecommendationResponse(BaseModel):
    """여행지 추천 응답"""
    status: str
    destinations: list[Destination]
    userProfile: Optional[dict] = None
    isFallback: bool = False


async def optimize_destination_prompt(destination: str, additional_prompt: str = "") -> str:
    """LLM을 사용하여 한국어 여행지 설명을 영어 이미지 프롬프트로 최적화

    Args:
        destination: 사용자가 입력한 여행지 설명 (한국어 가능)
        additional_prompt: 추가 설명 (한국어 가능)

    Returns:
        영어로 최적화된 장소 및 장면 설명
    """
    try:
        # 입력 텍스트 결합
        input_text = destination
        if additional_prompt:
            input_text = f"{destination}, {additional_prompt}"

        system_prompt = """You are an expert at converting travel destination descriptions into optimized English prompts for image generation.

Your task:
1. Translate any non-English text to English
2. Extract and emphasize the KEY ENVIRONMENT/LOCATION type (beach, ocean, mountain, forest, city, etc.)
3. Extract scene details (time of day, weather, mood)
4. Output a concise, clear English description optimized for image generation

IMPORTANT: The environment/location keywords must be prominent and clear.

Output format (English only, no explanations):
[location with environment type], [scene description], [atmosphere/mood]

Examples:
Input: "포르투갈 나자레 해안의 파도, 해질녘 혼자 걷고 있는 모습"
Output: "Nazaré beach coastline in Portugal with ocean waves, person walking alone at sunset, golden hour atmosphere"

Input: "교토의 대나무 숲, 아침 안개 속 산책"
Output: "Arashiyama bamboo forest in Kyoto Japan, morning walk through misty bamboo grove, serene peaceful atmosphere"

Input: "파리 몽마르트 언덕의 카페"
Output: "Montmartre hill cafe in Paris France, charming Parisian street scene, artistic bohemian atmosphere"
"""

        params = LLMGenerationParams(
            prompt=f"Convert this to an optimized English image prompt:\n{input_text}",
            system_prompt=system_prompt,
            temperature=0.3,  # 낮은 온도로 일관된 출력
            max_tokens=200,
        )

        result = await llm_provider.generate(params)

        if result.success and result.content:
            optimized = result.content.strip()
            logger.info(f"Optimized destination prompt: {input_text[:50]}... -> {optimized[:100]}...")
            return optimized
        else:
            logger.warning(f"LLM optimization failed, using original: {result.error}")
            return destination

    except Exception as e:
        logger.error(f"Prompt optimization error: {e}")
        return destination


async def optimize_outfit_prompt(outfit_style: str) -> str:
    """LLM을 사용하여 한국어 의상 스타일을 영어로 번역

    Args:
        outfit_style: 사용자가 입력한 의상 스타일 (한국어 가능)

    Returns:
        영어로 번역된 의상 스타일
    """
    if not outfit_style:
        return ""

    try:
        system_prompt = """You are an expert at converting fashion/outfit descriptions into English for image generation.

Your task:
1. Translate any non-English text to English
2. Convert fashion terms to clear, descriptive English
3. Keep it concise and suitable for image generation prompts

Output format: Just the English outfit description, no explanations.

Examples:
Input: "블랙 레더, 메탈릭 악세서리, 미니멀 다크톤"
Output: "black leather jacket, metallic accessories, minimal dark-toned outfit"

Input: "화이트 린넨 셔츠, 라탄 가방"
Output: "white linen shirt, rattan bag, casual summer style"

Input: "빈티지 데님, 레트로 선글라스"
Output: "vintage denim, retro sunglasses, classic casual look"
"""

        params = LLMGenerationParams(
            prompt=f"Convert this outfit description to English:\n{outfit_style}",
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=100,
        )

        result = await llm_provider.generate(params)

        if result.success and result.content:
            optimized = result.content.strip().strip('"')
            logger.info(f"Optimized outfit prompt: {outfit_style[:30]}... -> {optimized[:50]}...")
            return optimized
        else:
            logger.warning(f"Outfit optimization failed, using original: {result.error}")
            return outfit_style

    except Exception as e:
        logger.error(f"Outfit optimization error: {e}")
        return outfit_style


async def build_travel_prompt(request: GenerateRequest) -> str:
    """여행 프롬프트 구성 (LLM 기반 최적화 포함)"""

    # 1. LLM으로 destination을 영어 프롬프트로 최적화
    optimized_destination = await optimize_destination_prompt(
        request.destination,
        request.additionalPrompt
    )

    # 2. LLM으로 outfit을 영어로 번역
    optimized_outfit = await optimize_outfit_prompt(request.outfitStyle)

    # 3. 필름 스톡 스타일
    film_style = FILM_STOCK_PROMPTS.get(request.filmStock, f"shot on {request.filmStock} film")

    # 4. 의상 스타일
    outfit_prompt = f"wearing {optimized_outfit}" if optimized_outfit else ""

    # 5. 컬러 팔레트 힌트
    color_hint = ""
    if request.colorPalette:
        colors = ", ".join(request.colorPalette[:3])
        color_hint = f"color palette featuring {colors} tones"

    # 6. 여행 사진 느낌 공통 요소
    travel_photo_style = "authentic travel photography, candid moment, natural lighting, environmental portrait"

    # 최종 프롬프트 조합 (장소 정보를 앞에 배치)
    prompt_parts = [
        f"A traveler at {optimized_destination}",  # 최적화된 영어 장소 설명
        outfit_prompt,
        travel_photo_style,
        film_style,
        color_hint,
        "high quality, detailed, professional photography"
    ]

    return ", ".join(filter(None, prompt_parts))


app = FastAPI(
    title="Trip Kit Image Generation API",
    description="Image Provider를 사용한 여행 이미지 생성 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"status": "ok", "service": "Trip Kit Image Generation API"}


@app.get("/health")
async def health_check():
    """헬스 체크"""
    provider = os.getenv("IMAGE_PROVIDER", "gemini")
    return {
        "status": "healthy",
        "provider": provider,
        "models": {
            "text": DEFAULT_TEXT_MODEL,
            "image": DEFAULT_IMAGE_MODEL,
        }
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest):
    """이미지 생성 엔드포인트

    프론트엔드에서 보낸 요청을 받아 직접 Provider를 사용하여 이미지를 생성합니다.
    """
    try:
        logger.info(f"Generate request: {request.destination}, concept={request.concept}")

        # 여행 프롬프트 구성 (LLM 기반 최적화 포함)
        travel_prompt = await build_travel_prompt(request)
        logger.info(f"Built travel prompt: {travel_prompt[:200]}...")

        # 키워드 추출 (간단히 분리)
        keywords = [
            request.destination,
            request.concept,
            request.filmStock,
        ]
        if request.outfitStyle:
            keywords.append(request.outfitStyle)
        keywords = [k for k in keywords if k]  # 빈 값 제거

        # Provider 가져오기 (Gemini + imagen 모델)
        provider = get_provider("gemini", model=DEFAULT_IMAGE_MODEL)
        logger.info(f"Using provider: {provider.provider_name}, model: {DEFAULT_IMAGE_MODEL}")

        # 이미지 생성 파라미터
        params = ImageGenerationParams(
            prompt=travel_prompt,
            size="1024x1024",
            quality="standard",
            style="vivid" if request.concept in ["flaneur", "midnight"] else "natural"
        )

        # 이미지 생성
        result = await provider.generate(params)

        if result.success:
            logger.info(f"Image generated successfully: {result.url[:50] if result.url else 'N/A'}...")

            return GenerateResponse(
                status="success",
                imageUrl=result.url,
                optimizedPrompt=travel_prompt,
                extractedKeywords=keywords,
                metadata={
                    "concept": request.concept,
                    "filmStock": request.filmStock,
                    "destination": request.destination,
                    "provider": result.provider,
                    "model": DEFAULT_IMAGE_MODEL,
                    "revised_prompt": result.revised_prompt,
                }
            )
        else:
            logger.error(f"Image generation failed: {result.error}")
            return GenerateResponse(
                status="error",
                error=result.error or "Unknown error"
            )

    except Exception as e:
        logger.error(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/destinations", response_model=RecommendationResponse)
async def get_destination_recommendations(request: RecommendationRequest):
    """여행지 추천 엔드포인트

    RecommendationAgent를 사용하여 사용자의 선호도와 컨셉을 기반으로
    AI가 숨겨진 여행지를 추천합니다.
    """
    try:
        logger.info(
            f"Recommendations request: mood={request.preferences.mood}, concept={request.concept}"
        )

        # Agent 입력 데이터 구성
        input_data = {
            "preferences": {
                "mood": request.preferences.mood,
                "aesthetic": request.preferences.aesthetic,
                "duration": request.preferences.duration,
                "interests": request.preferences.interests,
            },
            "concept": request.concept,
            "travel_scene": request.travelScene,
            "travel_destination": request.travelDestination,
        }

        # Agent 실행
        result = await recommendation_agent.recommend(input_data)

        logger.info(f"Recommendations generated: {len(result['destinations'])} destinations")

        return RecommendationResponse(
            status=result["status"],
            destinations=result["destinations"],
            userProfile=result.get("user_profile"),
            isFallback=result.get("is_fallback", False),
        )

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
