from __future__ import annotations

from collections.abc import AsyncIterator

import structlog

from backend.config import get_settings
from backend.llm.base import LLMBase, LLMResponse

log = structlog.get_logger()


class GeminiLLM(LLMBase):
    """Google Gemini API adapter."""

    def __init__(self):
        from google import genai

        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set. Configure it in .env")
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model_id

    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048) -> LLMResponse:
        from google.genai import types

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
        )
        if system:
            config.system_instruction = system

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config,
        )

        usage = None
        if response.usage_metadata:
            usage = {
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count,
            }

        return LLMResponse(
            content=response.text,
            model=self._model,
            usage=usage,
        )

    async def generate_stream(self, prompt: str, system: str = "", max_tokens: int = 2048) -> AsyncIterator[str]:
        from google.genai import types

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
        )
        if system:
            config.system_instruction = system

        for chunk in self._client.models.generate_content_stream(
            model=self._model,
            contents=prompt,
            config=config,
        ):
            if chunk.text:
                yield chunk.text
