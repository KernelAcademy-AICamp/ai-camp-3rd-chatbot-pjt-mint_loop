"""FastAPI 서버 - 프론트엔드와 Image Provider 연결

직접 Image Provider를 사용하여 이미지를 생성합니다.
MCP 서버 없이도 독립적으로 동작합니다.
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

from .providers import get_provider, ImageGenerationParams

logger = structlog.get_logger(__name__)

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


def build_travel_prompt(request: GenerateRequest) -> str:
    """여행 프롬프트 구성"""
    # 기본 여행 프롬프트
    base_prompt = f"A person traveling and exploring {request.destination}"

    # 컨셉 스타일
    concept_style = CONCEPT_STYLE_PROMPTS.get(request.concept, CONCEPT_STYLE_PROMPTS["filmlog"])

    # 필름 스톡 스타일
    film_style = FILM_STOCK_PROMPTS.get(request.filmStock, f"shot on {request.filmStock} film")

    # 의상 스타일
    outfit_prompt = f"wearing {request.outfitStyle} style clothing" if request.outfitStyle else ""

    # 컬러 팔레트 힌트
    color_hint = ""
    if request.colorPalette:
        colors = ", ".join(request.colorPalette[:3])
        color_hint = f"color palette featuring {colors} tones"

    # 여행 사진 느낌 공통 요소
    travel_photo_style = "authentic travel photography, candid moment, natural pose, real location, immersive atmosphere, environmental portrait"

    # 최종 프롬프트 조합
    prompt_parts = [
        base_prompt,
        request.additionalPrompt,
        outfit_prompt,
        travel_photo_style,
        film_style,
        concept_style,
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
    provider = os.getenv("IMAGE_PROVIDER", "openai")
    return {"status": "healthy", "provider": provider}


@app.post("/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest):
    """이미지 생성 엔드포인트

    프론트엔드에서 보낸 요청을 받아 직접 Provider를 사용하여 이미지를 생성합니다.
    """
    try:
        logger.info(f"Generate request: {request.destination}, concept={request.concept}")

        # 여행 프롬프트 구성
        travel_prompt = build_travel_prompt(request)
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

        # Provider 가져오기
        provider = get_provider()
        logger.info(f"Using provider: {provider.provider_name}")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
