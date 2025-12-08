"""Translation service for Korean to English conversion."""
import re
from typing import Optional

import structlog

from ..config.prompts import TRANSLATION_SYSTEM_PROMPT
from ...providers.gemini_provider import GeminiLLMProvider, LLMGenerationParams

logger = structlog.get_logger(__name__)


class TranslationService:
    """Service for translating Korean text to English."""

    def __init__(self, llm_provider: GeminiLLMProvider):
        self._provider = llm_provider

    def has_korean(self, text: str) -> bool:
        """Check if text contains Korean characters."""
        return bool(re.search(r'[가-힣]', text))

    async def translate(self, text: str) -> str:
        """Translate Korean text to English."""
        if not text or not text.strip() or not self.has_korean(text):
            return text

        try:
            params = LLMGenerationParams(
                prompt=f"Translate to English: {text}",
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                temperature=0.3,
                response_format="text"
            )
            result = await self._provider.generate(params)

            if result.success and result.content:
                translated = result.content.strip().strip('"')
                return translated

            logger.warning("Translation failed, using original", text=text[:50])
            return text

        except Exception as e:
            logger.warning("Translation error", error=str(e))
            return text

    async def translate_fields(self, fields: dict[str, str]) -> dict[str, str]:
        """Translate multiple fields containing Korean."""
        korean_fields = {k: v for k, v in fields.items() if v and self.has_korean(v)}

        if not korean_fields:
            return {}

        combined = "\n".join([f"[{k}]: {v}" for k, v in korean_fields.items()])

        try:
            params = LLMGenerationParams(
                prompt=f"Translate each labeled Korean text to English. Keep labels and format.\n\n{combined}",
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                temperature=0.3,
                response_format="text"
            )
            result = await self._provider.generate(params)

            if not result.success or not result.content:
                return {}

            translated = {}
            for line in result.content.strip().split('\n'):
                line = line.strip()
                if line.startswith('[') and ']: ' in line:
                    key_end = line.index(']')
                    key = line[1:key_end]
                    value = line[key_end + 3:].strip()
                    translated[key] = value

            logger.info("Translated fields", count=len(translated))
            return translated

        except Exception as e:
            logger.warning("Batch translation error", error=str(e))
            return {}
