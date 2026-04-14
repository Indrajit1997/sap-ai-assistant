from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import structlog

from backend.config import get_settings

if TYPE_CHECKING:
    from backend.ingestion.chunker import TextChunk

log = structlog.get_logger()


class EmbedderBase(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        ...


class LocalEmbedder(EmbedderBase):
    """Uses sentence-transformers for local, free embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        log.info("loading_embedding_model", model=model_name)
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self._model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        return self._dimension


class BedrockEmbedder(EmbedderBase):
    """Uses Amazon Titan Embeddings via AWS Bedrock."""

    def __init__(self):
        import boto3
        settings = get_settings()
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self._model_id = "amazon.titan-embed-text-v2:0"
        self._dimension = 1024

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        import json
        results = []
        for text in texts:
            body = json.dumps({"inputText": text[:8192]})  # Titan max input
            response = self._client.invoke_model(modelId=self._model_id, body=body)
            result = json.loads(response["body"].read())
            results.append(result["embedding"])
        return results

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        return self._dimension


_embedder: EmbedderBase | None = None


def get_embedder() -> EmbedderBase:
    global _embedder
    if _embedder is None:
        settings = get_settings()
        if settings.embedding_provider == "bedrock":
            _embedder = BedrockEmbedder()
        else:
            _embedder = LocalEmbedder(settings.embedding_model)
    return _embedder
