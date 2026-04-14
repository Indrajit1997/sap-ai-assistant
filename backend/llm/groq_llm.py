from __future__ import annotations

from collections.abc import AsyncIterator

import structlog

from backend.config import get_settings
from backend.llm.base import LLMBase, LLMResponse

log = structlog.get_logger()


class GroqLLM(LLMBase):
    """Groq API adapter — runs Llama/Mixtral models at high speed, free tier available."""

    def __init__(self):
        from groq import AsyncGroq

        settings = get_settings()
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not set. Configure it in .env")
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._model = settings.groq_model_id

    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
        )

        usage = None
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

        return LLMResponse(
            content=response.choices[0].message.content,
            model=self._model,
            usage=usage,
        )

    async def generate_stream(self, prompt: str, system: str = "", max_tokens: int = 2048) -> AsyncIterator[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
