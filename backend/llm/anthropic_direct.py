from __future__ import annotations

from collections.abc import AsyncIterator

import structlog

from backend.config import get_settings
from backend.llm.base import LLMBase, LLMResponse

log = structlog.get_logger()


class AnthropicLLM(LLMBase):
    """Direct Anthropic API adapter (fallback when Bedrock is unavailable)."""

    def __init__(self):
        import anthropic
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Configure it in .env")
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = "claude-sonnet-4-20250514"

    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048) -> LLMResponse:
        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=self._model,
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        )

    async def generate_stream(self, prompt: str, system: str = "", max_tokens: int = 2048) -> AsyncIterator[str]:
        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
