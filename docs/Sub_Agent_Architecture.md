# Sub-Agent Architecture for TripKit MVP
## Multi-Agent System Design for Production

**"실무에서 검증된 Sub-Agent 시스템 설계"**

---

## 📋 Document Information

- **Version**: 1.0.0
- **Last Updated**: 2025-12-04
- **Architecture Pattern**: Multi-Agent Orchestration with LangGraph
- **Related Documents**: [PRD](./PRD_TripKit_MVP.md), [TRD](./TRD_TripKit_MVP.md), [API](./API_Documentation.md)

---

## 🎯 Sub-Agent System Overview

### Design Philosophy

**"각 에이전트는 단일 책임을 가지며, 협업을 통해 복잡한 작업을 수행한다"**

### Architecture Pattern

```
Orchestrator Agent (Supervisor)
    ├── Conversation Agent (대화 관리)
    ├── Recommendation Agent (추천 생성)
    ├── Image Generation Agent (이미지 생성)
    ├── Content Enrichment Agent (콘텐츠 보강)
    └── Quality Assurance Agent (품질 검증)
```

### Key Principles

1. **Single Responsibility**: 각 에이전트는 하나의 명확한 역할
2. **Loose Coupling**: 에이전트 간 독립성 유지
3. **Asynchronous Communication**: 비동기 메시지 전달
4. **State Management**: LangGraph StateGraph 활용
5. **Error Resilience**: 에이전트 실패 시 graceful degradation

---

## 🤖 Sub-Agent Specifications

---

## 1. Orchestrator Agent (Supervisor)

**Role**: 전체 워크플로우 조율 및 Sub-Agent 관리

### Responsibilities

- Sub-Agent 작업 할당 및 우선순위 결정
- 워크플로우 상태 관리 및 모니터링
- 에이전트 간 메시지 라우팅
- 에러 처리 및 복구 전략 실행
- 최종 응답 조합 및 반환

### State Schema

```python
from typing import TypedDict, Literal, List, Dict, Any
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class OrchestratorState(TypedDict):
    """Orchestrator 상태"""
    messages: List[BaseMessage]
    user_request: str
    current_step: Literal["init", "conversation", "recommendation", "image_generation", "enrichment", "qa", "complete"]
    assigned_agents: List[str]
    agent_results: Dict[str, Any]
    errors: List[str]
    final_response: Dict[str, Any] | None
```

### Decision Logic

```python
def route_to_agent(state: OrchestratorState) -> str:
    """다음 실행할 에이전트 결정"""
    step = state["current_step"]

    routing_map = {
        "init": "conversation_agent",
        "conversation": "recommendation_agent",
        "recommendation": "image_generation_agent",
        "image_generation": "content_enrichment_agent",
        "enrichment": "qa_agent",
        "qa": "complete"
    }

    return routing_map.get(step, "complete")
```

### Implementation File

- **Location**: `image-generation-agent/src/orchestrator/supervisor.py`
- **Dependencies**: LangGraph, LangChain
- **MCP Integration**: All MCP servers

---

## 2. Conversation Agent

**Role**: 사용자 대화 관리 및 Vibe 추출

### Responsibilities

- 자연어 대화 처리 (5-7 턴 대화)
- 사용자 선호도 추출 (mood, aesthetic, duration, interests)
- 대화 컨텍스트 유지 및 관리
- 대화 완료 여부 판단
- 구조화된 Vibe 프로파일 생성

### State Schema

```python
class ConversationState(TypedDict):
    """Conversation Agent 상태"""
    messages: List[BaseMessage]
    session_id: str
    current_question: str
    extracted_preferences: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    is_complete: bool
    confidence_score: float  # 0.0-1.0
```

### Conversation Flow

```
1. Greeting & Context Setting
   ↓
2. Mood Extraction ("What's your travel mood?")
   ↓
3. Aesthetic Preference ("Urban, nature, vintage, or modern?")
   ↓
4. Duration & Timing ("How long are you traveling?")
   ↓
5. Interest Deep Dive ("Photography, food, art, history?")
   ↓
6. Confirmation & Summary
   ↓
7. Vibe Profile Generation
```

### Prompt Engineering

```python
CONVERSATION_SYSTEM_PROMPT = """
You are a travel vibe consultant for TripKit.

Your goal is to understand the user's emotional and aesthetic preferences
through natural conversation. Extract:
- Mood (romantic, adventurous, nostalgic, peaceful)
- Aesthetic (urban, nature, vintage, modern)
- Duration (short 1-3d, medium 4-7d, long 8+d)
- Interests (photography, food, art, history, nature, architecture)

Guidelines:
- Ask one question at a time
- Be warm, conversational, and inspiring
- Avoid generic travel agent language
- Focus on "vibe" and "feeling" rather than logistics
- Total conversation: 5-7 exchanges maximum
- Confirm understanding before finalizing

Example Questions:
- "What kind of feeling are you looking for in this trip? Romantic sunsets, adventurous exploration, or peaceful reflection?"
- "Are you drawn to urban energy or natural landscapes?"
- "How long do you have for this journey?"
"""
```

### Quality Metrics

- Extraction Accuracy: >85%
- Conversation Completion Rate: >80%
- Average Turns: 5-7
- User Satisfaction: >4.2/5

### Implementation File

- **Location**: `image-generation-agent/src/agents/conversation_agent.py`
- **Dependencies**: GPT-4, LangChain
- **MCP Integration**: Context7 (conversation patterns)

---

## 3. Recommendation Agent

**Role**: Vibe 기반 여행지 및 Hidden Spot 추천

### Responsibilities

- Vibe 프로파일 분석
- 목적지 매칭 알고리즘 실행
- Hidden Spot 발굴 (비주류 로컬 명소)
- 추천 이유 생성 (matchReason)
- Photography Score 계산
- 안전도 및 접근성 평가

### State Schema

```python
class RecommendationState(TypedDict):
    """Recommendation Agent 상태"""
    vibe_profile: Dict[str, Any]
    destinations: List[Dict[str, Any]]
    hidden_spots: List[Dict[str, Any]]
    selected_concept: Literal["flaneur", "filmlog", "midnight"] | None
    recommendation_reasoning: List[str]
    confidence_scores: Dict[str, float]
```

### Recommendation Algorithm

```python
def generate_recommendations(vibe_profile: Dict) -> List[Destination]:
    """
    Vibe-based recommendation algorithm

    Steps:
    1. Semantic search on destination database (embeddings)
    2. Filter by mood + aesthetic compatibility
    3. Rank by photography_score × vibe_match_score
    4. Diversity filtering (avoid similar destinations)
    5. Generate match_reason for each recommendation
    """

    # 1. Embedding-based search
    query_embedding = get_vibe_embedding(vibe_profile)
    candidate_destinations = vector_search(query_embedding, top_k=20)

    # 2. Filter by compatibility
    compatible_dests = filter_by_vibe_compatibility(
        candidate_destinations,
        vibe_profile
    )

    # 3. Score and rank
    scored_dests = []
    for dest in compatible_dests:
        vibe_score = calculate_vibe_match(dest, vibe_profile)
        photo_score = dest.photography_score / 10
        final_score = (vibe_score * 0.7) + (photo_score * 0.3)

        scored_dests.append({
            **dest,
            "match_score": final_score,
            "match_reason": generate_match_reason(dest, vibe_profile)
        })

    # 4. Diversity filtering
    diverse_dests = select_diverse_destinations(scored_dests, count=3)

    return diverse_dests
```

### Hidden Spot Criteria

**Must Have**:
- ❌ NOT in top-10 tourist lists
- ✅ High photogenic potential (8-10/10)
- ✅ Authentic local atmosphere
- ✅ Accessible by public transport
- ✅ Safe for solo travelers

**Scoring Formula**:
```
hidden_score = (authenticity × 0.4) + (photogenic × 0.3) + (accessibility × 0.2) + (safety × 0.1)
```

### Data Sources

- **Primary**: GPT-4 knowledge base + web search (Tavily)
- **Secondary**: Curated local database (future)
- **Validation**: Cross-reference multiple sources

### Implementation File

- **Location**: `image-generation-agent/src/agents/recommendation_agent.py`
- **Dependencies**: GPT-4, Tavily Search, Vector DB (future)
- **MCP Integration**: Search MCP, Context7

---

## 4. Image Generation Agent

**Role**: Film aesthetic 이미지 생성

### Responsibilities

- 프롬프트 최적화 (location + outfit + film stock)
- DALL-E 3 API 호출 및 에러 처리
- Film aesthetic 적용 (Kodak ColorPlus, Portra, Fuji Superia, Ilford HP5)
- 이미지 품질 검증
- 생성 메타데이터 관리

### State Schema

```python
class ImageGenerationState(TypedDict):
    """Image Generation Agent 상태"""
    location_context: Dict[str, Any]
    concept: str
    film_stock: str
    outfit_style: str
    optimized_prompt: str
    generated_image_url: str | None
    revised_prompt: str | None
    generation_metadata: Dict[str, Any]
    generation_attempts: int
    errors: List[str]
```

### Film Stock Prompts

```python
FILM_STOCK_PROMPTS = {
    "kodak_colorplus": {
        "aesthetic": "Warm, saturated tones with slight red-orange shift",
        "grain": "Fine grain structure, minimal noise",
        "style": "Budget-friendly vintage film look",
        "prompt_suffix": "shot on Kodak ColorPlus 200 film, warm tones, fine grain, slight vignetting, nostalgic atmosphere"
    },
    "kodak_portra": {
        "aesthetic": "Natural, accurate skin tones with subtle pastel colors",
        "grain": "Very fine grain, smooth texture",
        "style": "Professional portrait film aesthetic",
        "prompt_suffix": "shot on Kodak Portra 400 film, natural skin tones, subtle colors, professional quality, smooth grain"
    },
    "fuji_superia": {
        "aesthetic": "Vibrant, saturated colors with strong contrast",
        "grain": "Moderate grain, crisp detail",
        "style": "Bold consumer film look",
        "prompt_suffix": "shot on Fujifilm Superia 400 film, vibrant colors, strong saturation, crisp details, moderate grain"
    },
    "ilford_hp5": {
        "aesthetic": "High contrast black and white with rich tones",
        "grain": "Visible grain structure, dramatic",
        "style": "Classic monochrome film aesthetic",
        "prompt_suffix": "shot on Ilford HP5 Plus 400 black and white film, high contrast, rich blacks, dramatic grain, classic b&w look"
    }
}
```

### Prompt Engineering Template

```python
def build_image_prompt(
    location: Dict,
    concept: str,
    film_stock: str,
    outfit: str
) -> str:
    """
    DALL-E 3 프롬프트 생성

    Template Structure:
    1. Film aesthetic declaration
    2. Scene description (location)
    3. Subject description (person + outfit + camera)
    4. Composition and framing
    5. Lighting and mood
    6. Film stock characteristics
    """

    film_config = FILM_STOCK_PROMPTS[film_stock]

    prompt = f"""
Create a high-quality photograph in the style of {film_config['aesthetic']}.

Scene Description:
{location['description']}

Subject:
- Young person wearing {outfit}
- Holding vintage 35mm film camera (Canon AE-1 or similar)
- Natural, candid pose looking towards the scenery
- Gentle, genuine expression

Composition:
- Subject positioned in right third of frame
- {location['name']} in background
- Depth of field: f/1.8-2.8 for beautiful bokeh
- Natural framing with environmental elements

Lighting & Mood:
- {get_lighting_for_time(location.get('best_time_to_visit', 'golden hour'))}
- Authentic analog film atmosphere
- Nostalgic, cinematic quality

Film Aesthetic:
{film_config['prompt_suffix']}

Style: Highly detailed, professional film photography, authentic vintage look, NOT digital filter simulation.
"""

    return prompt.strip()
```

### Error Handling

```python
async def generate_with_retry(
    prompt: str,
    max_attempts: int = 3
) -> Dict[str, Any]:
    """재시도 로직이 포함된 이미지 생성"""

    for attempt in range(max_attempts):
        try:
            response = await openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                style="vivid",
                n=1
            )

            return {
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "attempts": attempt + 1,
                "success": True
            }

        except openai.BadRequestError as e:
            # Content policy violation
            if "content_policy" in str(e).lower():
                # Sanitize prompt and retry
                prompt = sanitize_prompt(prompt)
                continue
            raise

        except openai.RateLimitError:
            # Wait and retry
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            continue

        except Exception as e:
            logger.error(f"Image generation attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise

    return {"success": False, "error": "Max retries exceeded"}
```

### Quality Validation

```python
def validate_image_quality(image_url: str) -> bool:
    """생성된 이미지 품질 검증"""

    # 1. URL 유효성 확인
    if not image_url or not image_url.startswith("https://"):
        return False

    # 2. 이미지 다운로드 및 메타데이터 추출
    try:
        response = requests.get(image_url, timeout=10)
        image = Image.open(BytesIO(response.content))

        # 3. 기본 검증
        width, height = image.size
        if width < 1024 or height < 1024:
            return False

        # 4. 품질 검증 (future: ML-based quality assessment)
        # - 얼굴 검출
        # - Film grain 존재 여부
        # - 색상 프로파일 일치도

        return True

    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False
```

### Implementation File

- **Location**: `image-generation-agent/src/agents/image_generation_agent.py`
- **Dependencies**: DALL-E 3, Pillow
- **MCP Integration**: Image MCP Server

---

## 5. Content Enrichment Agent

**Role**: 추천 콘텐츠 보강 및 스타일링 패키지 생성

### Responsibilities

- Film camera 추천 (모델, 특성, 대여 정보)
- Camera settings 생성 (aperture, shutter speed, ISO)
- Outfit styling 큐레이션 (색상 팔레트, 구체적 아이템)
- Props 추천 (2-3개 소품)
- Photography angles 가이드 (3-5개 구도 기법)
- Local insider tips 추가

### State Schema

```python
class ContentEnrichmentState(TypedDict):
    """Content Enrichment Agent 상태"""
    location_id: str
    concept: str
    time_of_day: str
    weather: str
    season: str

    # Generated content
    camera_recommendation: Dict[str, Any]
    film_stock_recommendation: Dict[str, Any]
    camera_settings: Dict[str, Any]
    outfit_suggestions: Dict[str, Any]
    props: List[Dict[str, Any]]
    best_angles: List[Dict[str, Any]]
    local_tips: Dict[str, str]
```

### Camera Recommendation Logic

```python
CAMERA_DATABASE = {
    "flaneur": {
        "primary": "Leica M6",
        "alternative": ["Olympus Trip 35", "Contax T2"],
        "reasoning": "Compact, discreet cameras for urban wandering"
    },
    "filmlog": {
        "primary": "Canon AE-1",
        "alternative": ["Nikon FM2", "Pentax K1000"],
        "reasoning": "Reliable SLRs with manual controls for vintage aesthetic"
    },
    "midnight": {
        "primary": "Hasselblad 500C/M",
        "alternative": ["Mamiya RB67", "Pentax 67"],
        "reasoning": "Medium format for artistic, dreamlike quality"
    }
}

def recommend_camera(concept: str, budget: str = "medium") -> Dict:
    """Concept 기반 카메라 추천"""

    config = CAMERA_DATABASE.get(concept, CAMERA_DATABASE["filmlog"])

    return {
        "model": config["primary"],
        "alternatives": config["alternative"],
        "reasoning": config["reasoning"],
        "rental_info": get_rental_info(config["primary"]),
        "buy_links": get_purchase_links(config["primary"])
    }
```

### Outfit Styling Algorithm

```python
def generate_outfit_suggestions(
    concept: str,
    season: str,
    weather: str,
    color_preferences: List[str] = None
) -> Dict:
    """Concept와 계절 기반 스타일링 생성"""

    # 1. Color palette generation
    base_palettes = {
        "flaneur": ["#2C3E50", "#ECF0F1", "#34495E", "#BDC3C7"],  # Urban neutrals
        "filmlog": ["#F5E6D3", "#8B7355", "#A0826D", "#FFFFFF"],  # Vintage warm
        "midnight": ["#191970", "#4B0082", "#2F4F4F", "#C0C0C0"]  # Artistic dark
    }

    palette = base_palettes.get(concept, base_palettes["filmlog"])

    # 2. Seasonal adjustments
    seasonal_modifiers = {
        "spring": {"add_colors": ["pastel pink", "light green"], "fabrics": ["cotton", "linen"]},
        "summer": {"add_colors": ["white", "light blue"], "fabrics": ["linen", "breathable cotton"]},
        "fall": {"add_colors": ["burgundy", "mustard"], "fabrics": ["wool", "denim"]},
        "winter": {"add_colors": ["navy", "charcoal"], "fabrics": ["wool", "cashmere"]}
    }

    season_config = seasonal_modifiers.get(season, seasonal_modifiers["spring"])

    # 3. Specific item generation
    items = generate_specific_items(concept, season, weather)

    return {
        "color_palette": palette,
        "color_names": get_color_names(palette),
        "seasonal_additions": season_config["add_colors"],
        "recommended_fabrics": season_config["fabrics"],
        "specific_items": items,
        "avoid_items": get_avoid_items(concept),
        "shopping_tips": generate_shopping_tips(concept)
    }
```

### Props Recommendation

```python
PROPS_DATABASE = {
    "flaneur": [
        {"name": "Vintage book", "purpose": "Literary wanderer aesthetic"},
        {"name": "City map", "purpose": "Navigation storytelling element"},
        {"name": "Coffee in thermos", "purpose": "Urban explorer vibe"}
    ],
    "filmlog": [
        {"name": "Vintage Polaroid camera", "purpose": "Nostalgic layering"},
        {"name": "Film photography book", "purpose": "Artistic context"},
        {"name": "Woven basket", "purpose": "Vintage travel charm"}
    ],
    "midnight": [
        {"name": "Vintage pocket watch", "purpose": "Time travel symbolism"},
        {"name": "Leather-bound journal", "purpose": "Artistic documentation"},
        {"name": "Antique monocular", "purpose": "Poetic observation tool"}
    ]
}

def recommend_props(
    concept: str,
    location_type: str,
    count: int = 3
) -> List[Dict]:
    """Concept 기반 소품 추천"""

    base_props = PROPS_DATABASE.get(concept, PROPS_DATABASE["filmlog"])

    # Location-specific adjustments
    if location_type == "coastal":
        base_props.append({
            "name": "Seashell collection jar",
            "purpose": "Coastal memory keeper"
        })
    elif location_type == "urban":
        base_props.append({
            "name": "Vintage metro ticket",
            "purpose": "Urban exploration token"
        })

    # Select top props
    selected = base_props[:count]

    # Enrich with sourcing info
    for prop in selected:
        prop["where_to_find"] = generate_sourcing_info(prop["name"])
        prop["styling_tips"] = generate_styling_tips(prop["name"], concept)

    return selected
```

### Photography Angles Guide

```python
def generate_photography_angles(
    location: Dict,
    concept: str,
    time_of_day: str
) -> List[Dict]:
    """촬영 구도 가이드 생성"""

    base_angles = [
        {
            "name": "Rule of thirds",
            "description": "Position subject in third intersections",
            "camera_height": "eye-level",
            "best_lighting": "golden hour",
            "diagram_type": "grid_overlay"
        },
        {
            "name": "Leading lines",
            "description": "Use natural lines to guide viewer's eye",
            "camera_height": "low angle",
            "best_lighting": "any",
            "diagram_type": "line_overlay"
        },
        {
            "name": "Bokeh background",
            "description": "Wide aperture for creamy background blur",
            "camera_height": "eye-level or above",
            "best_lighting": "soft diffused",
            "diagram_type": "focus_diagram"
        },
        {
            "name": "Silhouette",
            "description": "Backlit subject against bright background",
            "camera_height": "low angle",
            "best_lighting": "sunset/sunrise",
            "diagram_type": "exposure_diagram"
        },
        {
            "name": "Frame within frame",
            "description": "Use environmental elements as natural frame",
            "camera_height": "varies",
            "best_lighting": "any",
            "diagram_type": "composition_overlay"
        }
    ]

    # Time-of-day specific recommendations
    time_based_angles = filter_angles_by_time(base_angles, time_of_day)

    # Concept-specific adjustments
    concept_angles = adjust_for_concept(time_based_angles, concept)

    # Add visual examples and diagrams
    for angle in concept_angles:
        angle["visual_example"] = f"https://angles.tripkit.com/{angle['name']}.jpg"
        angle["diagram_url"] = f"https://angles.tripkit.com/diagrams/{angle['diagram_type']}.svg"
        angle["technique"] = generate_technique_description(angle, location)

    return concept_angles[:5]  # Top 5 angles
```

### Implementation File

- **Location**: `image-generation-agent/src/agents/content_enrichment_agent.py`
- **Dependencies**: GPT-4, Database (film stocks, cameras)
- **MCP Integration**: Context7 (photography knowledge)

---

## 6. Quality Assurance Agent

**Role**: 생성된 콘텐츠 품질 검증 및 개선

### Responsibilities

- 추천 정확도 검증 (vibe match 확인)
- 이미지 품질 평가 (film aesthetic 적합성)
- 콘텐츠 완성도 체크 (필수 필드 누락 확인)
- 안전성 검증 (부적절한 콘텐츠 필터링)
- 사용자 피드백 수집 및 학습

### State Schema

```python
class QualityAssuranceState(TypedDict):
    """Quality Assurance Agent 상태"""
    content_to_validate: Dict[str, Any]
    validation_results: Dict[str, bool]
    quality_scores: Dict[str, float]
    improvement_suggestions: List[str]
    is_approved: bool
    confidence_level: float
```

### Validation Checklist

```python
class QAChecklist:
    """품질 검증 체크리스트"""

    @staticmethod
    def validate_recommendations(destinations: List[Dict]) -> Dict:
        """추천 콘텐츠 검증"""

        checks = {
            "count": len(destinations) == 3,
            "all_have_match_reason": all(d.get("matchReason") for d in destinations),
            "photography_scores": all(1 <= d.get("photographyScore", 0) <= 10 for d in destinations),
            "safety_ratings": all(1 <= d.get("safetyRating", 0) <= 10 for d in destinations),
            "descriptions_length": all(50 <= len(d.get("description", "")) <= 300 for d in destinations),
            "no_duplicates": len(set(d["id"] for d in destinations)) == len(destinations)
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
            "quality_score": sum(checks.values()) / len(checks)
        }

    @staticmethod
    def validate_image(image_data: Dict) -> Dict:
        """이미지 품질 검증"""

        checks = {
            "url_valid": bool(image_data.get("url") and image_data["url"].startswith("https://")),
            "prompt_exists": bool(image_data.get("prompt")),
            "metadata_complete": all(
                key in image_data.get("metadata", {})
                for key in ["model", "size", "quality"]
            ),
            "generation_time_acceptable": image_data.get("generationTime", 99999) < 30000  # <30s
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
            "quality_score": sum(checks.values()) / len(checks)
        }

    @staticmethod
    def validate_styling_package(styling: Dict) -> Dict:
        """스타일링 패키지 검증"""

        checks = {
            "camera_recommended": bool(styling.get("cameraModel")),
            "film_stock_complete": bool(styling.get("filmStock") and styling["filmStock"].get("name")),
            "camera_settings_valid": all(
                key in styling.get("cameraSettings", {})
                for key in ["aperture", "shutterSpeed", "iso"]
            ),
            "outfit_has_palette": bool(styling.get("outfitSuggestions", {}).get("colorPalette")),
            "props_count": 2 <= len(styling.get("props", [])) <= 4,
            "angles_count": 3 <= len(styling.get("bestAngles", [])) <= 5
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
            "quality_score": sum(checks.values()) / len(checks)
        }
```

### Safety Validation

```python
async def validate_safety(content: Dict) -> Dict:
    """안전성 검증 (부적절한 콘텐츠 필터링)"""

    # 1. Text content moderation
    text_to_check = " ".join([
        str(v) for v in content.values()
        if isinstance(v, (str, list))
    ])

    moderation_result = await openai_client.moderations.create(
        input=text_to_check
    )

    # 2. Image URL validation (if present)
    image_safe = True
    if content.get("generated_image_url"):
        # Check image content (future: use moderation API)
        image_safe = True  # Placeholder

    return {
        "text_safe": not moderation_result.results[0].flagged,
        "image_safe": image_safe,
        "categories": moderation_result.results[0].categories,
        "approved": not moderation_result.results[0].flagged and image_safe
    }
```

### Improvement Suggestions

```python
def generate_improvements(validation_results: Dict) -> List[str]:
    """검증 결과 기반 개선 제안"""

    suggestions = []

    # Check each validation result
    for category, result in validation_results.items():
        if not result.get("passed"):
            failed_checks = [
                check for check, passed in result.get("checks", {}).items()
                if not passed
            ]

            for check in failed_checks:
                suggestions.append(
                    get_improvement_suggestion(category, check)
                )

    # Quality score-based suggestions
    overall_quality = sum(
        r.get("quality_score", 0)
        for r in validation_results.values()
    ) / len(validation_results)

    if overall_quality < 0.8:
        suggestions.append(
            "Overall quality below threshold. Consider regenerating content."
        )

    return suggestions
```

### Implementation File

- **Location**: `image-generation-agent/src/agents/qa_agent.py`
- **Dependencies**: OpenAI Moderation API
- **MCP Integration**: Sequential (systematic validation)

---

## 🔄 Agent Communication & Workflow

### Message Passing Protocol

```python
from typing import TypedDict, Literal
from datetime import datetime

class AgentMessage(TypedDict):
    """에이전트 간 메시지 프로토콜"""
    sender: str  # Agent ID
    receiver: str  # Target agent ID or "orchestrator"
    message_type: Literal["request", "response", "error", "status"]
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str  # Request tracking
    priority: Literal["high", "normal", "low"]
```

### Workflow State Machine

```python
from langgraph.graph import StateGraph, END

def build_multi_agent_workflow():
    """Multi-Agent 워크플로우 구축"""

    workflow = StateGraph(OrchestratorState)

    # Add agent nodes
    workflow.add_node("conversation", conversation_agent_node)
    workflow.add_node("recommendation", recommendation_agent_node)
    workflow.add_node("image_generation", image_generation_agent_node)
    workflow.add_node("content_enrichment", content_enrichment_agent_node)
    workflow.add_node("qa", qa_agent_node)

    # Define edges
    workflow.set_entry_point("conversation")

    workflow.add_conditional_edges(
        "conversation",
        lambda state: "recommendation" if state.get("is_complete") else "conversation"
    )

    workflow.add_edge("recommendation", "image_generation")
    workflow.add_edge("image_generation", "content_enrichment")
    workflow.add_edge("content_enrichment", "qa")

    workflow.add_conditional_edges(
        "qa",
        lambda state: END if state.get("is_approved") else "content_enrichment"
    )

    return workflow.compile()
```

### Parallel Execution Pattern

```python
import asyncio

async def parallel_agent_execution(
    agents: List[Callable],
    state: Dict[str, Any]
) -> List[Dict]:
    """병렬 에이전트 실행"""

    tasks = [
        asyncio.create_task(agent(state))
        for agent in agents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle errors
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Agent {agents[i].__name__} failed: {result}")
        else:
            successful_results.append(result)

    return successful_results
```

---

## 📂 Project Structure

```
image-generation-agent/
├── src/
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── supervisor.py              # Orchestrator Agent
│   │   └── state.py                   # Global state definitions
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── conversation_agent.py      # Conversation Agent
│   │   ├── recommendation_agent.py    # Recommendation Agent
│   │   ├── image_generation_agent.py  # Image Generation Agent
│   │   ├── content_enrichment_agent.py # Content Enrichment Agent
│   │   └── qa_agent.py                # Quality Assurance Agent
│   │
│   ├── mcp_servers/
│   │   ├── __init__.py
│   │   ├── search_server.py           # Search MCP Server
│   │   └── image_server.py            # Image Generation MCP Server
│   │
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── message_protocol.py        # Agent message protocol
│   │   ├── state_management.py        # State utilities
│   │   └── error_handling.py          # Error handling utilities
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                # Configuration
│   │   ├── prompts.py                 # Prompt templates
│   │   └── constants.py               # Constants and enums
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                 # Logging utilities
│       └── monitoring.py              # Monitoring and metrics
│
├── tests/
│   ├── unit/
│   │   ├── test_conversation_agent.py
│   │   ├── test_recommendation_agent.py
│   │   ├── test_image_generation_agent.py
│   │   ├── test_content_enrichment_agent.py
│   │   └── test_qa_agent.py
│   │
│   └── integration/
│       ├── test_full_workflow.py
│       └── test_agent_communication.py
│
├── examples/
│   ├── basic_workflow.py              # 기본 워크플로우 예제
│   ├── parallel_agents.py             # 병렬 실행 예제
│   └── custom_workflow.py             # 커스텀 워크플로우 예제
│
└── docs/
    ├── agent_specifications/          # 각 에이전트 상세 문서
    └── workflow_diagrams/             # 워크플로우 다이어그램
```

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

1. **Orchestrator Setup**
   - StateGraph 구조 설계
   - Message protocol 구현
   - Error handling framework

2. **Agent Scaffolding**
   - 각 에이전트 기본 구조 생성
   - State schema 정의
   - Node 함수 템플릿

### Phase 2: Individual Agents (Week 2-3)

1. **Conversation Agent** (2 days)
   - Prompt engineering
   - Vibe extraction logic
   - Conversation flow management

2. **Recommendation Agent** (3 days)
   - Vibe matching algorithm
   - Hidden spot generation
   - Scoring and ranking

3. **Image Generation Agent** (2 days)
   - Film stock prompts
   - DALL-E 3 integration
   - Quality validation

4. **Content Enrichment Agent** (2 days)
   - Camera recommendations
   - Styling generation
   - Photography angles

5. **Quality Assurance Agent** (2 days)
   - Validation logic
   - Safety checks
   - Improvement suggestions

### Phase 3: Integration & Testing (Week 4)

1. **Agent Integration**
   - Workflow assembly
   - Message passing
   - Error recovery

2. **Testing**
   - Unit tests per agent
   - Integration tests
   - End-to-end workflow tests

3. **Optimization**
   - Performance tuning
   - Parallel execution
   - Caching strategies

---

## 📊 Success Metrics

### Agent Performance KPIs

| Agent | Metric | Target |
|-------|--------|--------|
| Conversation | Extraction Accuracy | >85% |
| Conversation | Completion Rate | >80% |
| Recommendation | Vibe Match Score | >0.75 |
| Recommendation | Hidden Spot Quality | >8/10 |
| Image Generation | Success Rate | >90% |
| Image Generation | Generation Time | <15s |
| Content Enrichment | Completeness | >95% |
| QA | Approval Rate (first pass) | >80% |

### System-Level Metrics

- **End-to-End Success Rate**: >85%
- **Average Workflow Time**: <60s
- **Error Recovery Rate**: >90%
- **User Satisfaction**: >4.2/5

---

## 🔧 Configuration & Deployment

### Environment Variables

```bash
# Agent Configuration
ORCHESTRATOR_MAX_RETRIES=3
AGENT_TIMEOUT_SECONDS=30
PARALLEL_EXECUTION_ENABLED=true
MAX_CONCURRENT_AGENTS=5

# Model Configuration
CONVERSATION_MODEL=gpt-4o
RECOMMENDATION_MODEL=gpt-4o
ENRICHMENT_MODEL=gpt-4o-mini
IMAGE_MODEL=dall-e-3

# MCP Servers
SEARCH_MCP_URL=http://localhost:8050
IMAGE_MCP_URL=http://localhost:8051

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
SENTRY_DSN=https://...
```

### Docker Compose

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    environment:
      - AGENT_TYPE=orchestrator
    ports:
      - "8080:8080"
    depends_on:
      - search-mcp
      - image-mcp

  search-mcp:
    build:
      context: .
      dockerfile: Dockerfile.search-mcp
    ports:
      - "8050:8050"

  image-mcp:
    build:
      context: .
      dockerfile: Dockerfile.image-mcp
    ports:
      - "8051:8051"
```

---

## 📚 References

- [LangGraph Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [Agent-to-Agent (A2A) Protocol](https://github.com/anthropics/a2a)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/best-practices)

---

**Document Status**: ✅ Ready for Implementation
**Next Steps**: Begin Phase 1 - Core Infrastructure Setup
