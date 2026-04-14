from __future__ import annotations

import structlog

from backend.config import get_settings
from backend.llm.base import LLMBase

log = structlog.get_logger()

_llm: LLMBase | None = None


def get_llm() -> LLMBase:
    global _llm
    if _llm is None:
        settings = get_settings()
        if settings.llm_provider == "bedrock":
            from backend.llm.bedrock import BedrockLLM
            _llm = BedrockLLM()
            log.info("llm_initialized", provider="bedrock", model=settings.bedrock_model_id)
        elif settings.llm_provider == "anthropic":
            from backend.llm.anthropic_direct import AnthropicLLM
            _llm = AnthropicLLM()
            log.info("llm_initialized", provider="anthropic")
        elif settings.llm_provider == "gemini":
            from backend.llm.gemini import GeminiLLM
            _llm = GeminiLLM()
            log.info("llm_initialized", provider="gemini", model=settings.gemini_model_id)
        elif settings.llm_provider == "groq":
            from backend.llm.groq_llm import GroqLLM
            _llm = GroqLLM()
            log.info("llm_initialized", provider="groq", model=settings.groq_model_id)
        else:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
    return _llm
