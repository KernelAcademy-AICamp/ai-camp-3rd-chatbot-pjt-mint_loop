"""Chat service for conversation management."""
import json
from typing import Any

import structlog

from ..config.prompts import CHATBOT_SYSTEM_PROMPT
from ..models.requests import ChatRequest, RejectedItems
from ..models.responses import ChatResponse
from ...providers.gemini_provider import GeminiLLMProvider, LLMGenerationParams

logger = structlog.get_logger(__name__)

DEFAULT_COLLECTED = {
    "city": None, "spotName": None, "mainAction": None, "conceptId": None,
    "outfitStyle": None, "posePreference": None, "filmType": None, "cameraModel": None
}

DEFAULT_REJECTED = {
    "cities": [], "spots": [], "actions": [], "concepts": [],
    "outfits": [], "poses": [], "films": [], "cameras": []
}


class ChatService:
    """Service for managing chat conversations."""

    def __init__(self, llm_provider: GeminiLLMProvider):
        self._provider = llm_provider

    async def process(self, request: ChatRequest) -> ChatResponse:
        """Process chat message and return response."""
        try:
            prompt = self._build_prompt(request)
            result = await self._call_llm(prompt)

            if not result.success:
                return self._error_response(request, result.error)

            return self._parse_response(request, result.content)

        except Exception as e:
            logger.error("Chat processing error", error=str(e))
            raise

    def _build_prompt(self, request: ChatRequest) -> str:
        """Build prompt from chat request."""
        history = self._format_history(request.conversationHistory[-10:])
        collected_info = self._format_collected(request.collectedData)
        rejected_info = self._format_rejected(request.rejectedItems)

        return f"""현재 단계: {request.currentStep}
{collected_info}{rejected_info}

대화 히스토리:
{history}

사용자의 새 메시지: {request.message}

위 정보를 바탕으로 JSON 형식으로 응답해주세요.
⚠️ 중요: 이미 확정된 정보는 그대로 유지하고, 거부된 항목은 다시 추천하지 마세요."""

    def _format_history(self, messages: list) -> str:
        """Format conversation history."""
        lines = []
        for msg in messages:
            role = "사용자" if msg.role == "user" else "어시스턴트"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)

    def _format_collected(self, data: dict | None) -> str:
        """Format collected data context."""
        if not data:
            return ""

        confirmed = {k: v for k, v in data.items() if v is not None}
        result = ""
        if confirmed:
            result = f"\n✅ 확정된 정보:\n{json.dumps(confirmed, ensure_ascii=False, indent=2)}"
        result += f"\n\n전체 상태:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
        return result

    def _format_rejected(self, items: RejectedItems | None) -> str:
        """Format rejected items context."""
        if not items:
            return ""

        rejected = items.model_dump()
        non_empty = {k: v for k, v in rejected.items() if v}
        if not non_empty:
            return ""

        return f"\n\n🚨 거부된 항목:\n{json.dumps(non_empty, ensure_ascii=False, indent=2)}"

    async def _call_llm(self, prompt: str) -> Any:
        """Call LLM with prompt."""
        params = LLMGenerationParams(
            prompt=prompt,
            system_prompt=CHATBOT_SYSTEM_PROMPT,
            temperature=0.7,
            response_format="json"
        )
        return await self._provider.generate(params)

    def _parse_response(self, request: ChatRequest, content: str) -> ChatResponse:
        """Parse LLM response into ChatResponse."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, using raw text")
            return ChatResponse(
                reply=content,
                currentStep=request.currentStep,
                nextStep=request.currentStep,
                rejectedItems=request.rejectedItems
            )

        collected = self._merge_collected(request.collectedData, data.get("collectedData"))
        rejected = self._merge_rejected(request.rejectedItems, data.get("rejectedItems"))

        return ChatResponse(
            reply=data.get("reply", "다시 말씀해주시겠어요?"),
            currentStep=data.get("currentStep", request.currentStep),
            nextStep=data.get("nextStep", request.currentStep),
            isComplete=data.get("isComplete", False),
            collectedData=collected,
            rejectedItems=rejected
        )

    def _merge_collected(self, existing: dict | None, new: dict | None) -> dict:
        """Merge collected data, preserving existing values."""
        result = dict(existing) if existing else dict(DEFAULT_COLLECTED)
        if new:
            for key in result:
                if new.get(key) is not None:
                    result[key] = new[key]
        return result

    def _merge_rejected(self, existing: RejectedItems | None, new: dict | None) -> RejectedItems:
        """Merge rejected items."""
        base = existing.model_dump() if existing else dict(DEFAULT_REJECTED)
        if new:
            for key in base:
                if key in new and new[key]:
                    base[key] = list(set(base[key] + new[key]))
        return RejectedItems(**base)

    def _error_response(self, request: ChatRequest, error: str | None) -> ChatResponse:
        """Create error response."""
        return ChatResponse(
            reply="죄송해요, 잠시 문제가 생겼어요. 다시 말씀해주시겠어요?",
            currentStep=request.currentStep,
            nextStep=request.currentStep,
            rejectedItems=request.rejectedItems,
            error=error
        )
