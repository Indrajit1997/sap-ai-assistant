from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorStoreBase(ABC):
    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict] | None = None,
    ) -> None:
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        ...

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        ...

    @abstractmethod
    def reset(self) -> None:
        """Delete all documents from the store."""
        ...

    @abstractmethod
    def count(self) -> int:
        ...
