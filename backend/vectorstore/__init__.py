from backend.vectorstore.base import VectorStoreBase
from backend.vectorstore.chroma_store import ChromaVectorStore

_store: VectorStoreBase | None = None


def get_vector_store() -> VectorStoreBase:
    global _store
    if _store is None:
        from backend.config import get_settings
        settings = get_settings()
        if settings.vector_store == "opensearch":
            from backend.vectorstore.opensearch_store import OpenSearchVectorStore
            _store = OpenSearchVectorStore()
        else:
            _store = ChromaVectorStore()
    return _store


__all__ = ["VectorStoreBase", "get_vector_store"]
