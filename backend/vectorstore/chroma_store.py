from __future__ import annotations

import structlog

from backend.config import get_settings
from backend.vectorstore.base import SearchResult, VectorStoreBase

log = structlog.get_logger()


class ChromaVectorStore(VectorStoreBase):
    """ChromaDB-backed vector store — zero config, persistent, great for dev."""

    def __init__(self):
        import chromadb

        settings = get_settings()
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            name="sap_documents",
            metadata={"hnsw:space": "cosine"},
        )
        log.info("chroma_initialized", persist_dir=settings.chroma_persist_dir)

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict] | None = None,
    ) -> None:
        # ChromaDB has a batch limit; process in chunks of 500
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = i + batch_size
            self._collection.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end] if metadatas else None,
            )
        log.info("chroma_added", count=len(ids))

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = self._collection.query(**kwargs)

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns cosine distance; convert to similarity
                distance = results["distances"][0][i]
                score = 1.0 - distance
                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i],
                    score=score,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                ))
        return search_results

    def delete(self, ids: list[str]) -> None:
        self._collection.delete(ids=ids)
        log.info("chroma_deleted", count=len(ids))

    def reset(self) -> None:
        self._client.delete_collection("sap_documents")
        self._collection = self._client.get_or_create_collection(
            name="sap_documents",
            metadata={"hnsw:space": "cosine"},
        )
        log.info("chroma_reset")

    def count(self) -> int:
        return self._collection.count()
