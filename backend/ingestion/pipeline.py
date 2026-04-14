from __future__ import annotations

import uuid
from pathlib import Path

import structlog

from backend.config import get_settings
from backend.ingestion.chunker import TextChunker
from backend.ingestion.embedder import get_embedder
from backend.ingestion.loader import DocumentLoader
from backend.vectorstore import get_vector_store

log = structlog.get_logger()


class IngestionPipeline:
    """Orchestrates the full document ingestion: load → chunk → embed → store."""

    def __init__(self):
        settings = get_settings()
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
        )
        self.embedder = get_embedder()
        self.store = get_vector_store()

    def ingest_file(self, file_path: str | Path, module: str = "") -> int:
        path = Path(file_path)
        documents = self.loader.load_file(path)

        if module:
            for doc in documents:
                doc.metadata["sap_module"] = module

        return self._process_documents(documents)

    def ingest_directory(self, dir_path: str | Path, recursive: bool = True, module: str = "") -> int:
        path = Path(dir_path)
        documents = self.loader.load_directory(path, recursive=recursive)

        if module:
            for doc in documents:
                doc.metadata["sap_module"] = module

        return self._process_documents(documents)

    def ingest_text(self, text: str, metadata: dict | None = None) -> int:
        from backend.ingestion.loader import Document
        doc = Document(content=text, metadata=metadata or {})
        return self._process_documents([doc])

    def ingest_url(self, url: str, module: str = "") -> int:
        """Ingest a single public URL."""
        documents = self.loader.load_url(url)

        if module:
            for doc in documents:
                doc.metadata["sap_module"] = module

        return self._process_documents(documents)

    def ingest_urls(self, urls: list[str], module: str = "") -> int:
        """Ingest multiple public URLs."""
        documents = self.loader.load_urls(urls)

        if module:
            for doc in documents:
                doc.metadata["sap_module"] = module

        return self._process_documents(documents)

    def _process_documents(self, documents) -> int:
        if not documents:
            log.warning("no_documents_to_process")
            return 0

        # Chunk
        chunks = self.chunker.chunk_documents(documents)
        if not chunks:
            log.warning("no_chunks_produced")
            return 0

        # Embed
        texts = [c.content for c in chunks]
        log.info("generating_embeddings", count=len(texts))
        embeddings = self.embedder.embed_texts(texts)

        # Store
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [c.metadata for c in chunks]

        self.store.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        log.info("ingestion_complete", chunks_stored=len(chunks))
        return len(chunks)
