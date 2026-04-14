from __future__ import annotations

import structlog

from backend.config import get_settings
from backend.ingestion.embedder import get_embedder
from backend.vectorstore import get_vector_store
from backend.vectorstore.base import SearchResult

log = structlog.get_logger()


class Retriever:
    """Retrieves relevant document chunks from the vector store."""

    def __init__(self):
        self.embedder = get_embedder()
        self.store = get_vector_store()
        self.settings = get_settings()

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        module_filter: str | None = None,
    ) -> list[SearchResult]:
        top_k = top_k or self.settings.rag_top_k

        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)

        # Build metadata filter
        filter_metadata = None
        if module_filter:
            filter_metadata = {"sap_module": module_filter}

        # Search vector store
        results = self.store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )

        # Filter by score threshold
        threshold = self.settings.rag_score_threshold
        filtered = [r for r in results if r.score >= threshold]

        log.info(
            "retrieval_complete",
            query_len=len(query),
            raw_results=len(results),
            filtered_results=len(filtered),
            threshold=threshold,
        )
        return filtered
