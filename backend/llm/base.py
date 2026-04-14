from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict | None = None


class LLMBase(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048) -> LLMResponse:
        ...

    @abstractmethod
    async def generate_stream(self, prompt: str, system: str = "", max_tokens: int = 2048) -> AsyncIterator[str]:
        ...
