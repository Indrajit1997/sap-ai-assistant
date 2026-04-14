from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

from backend.ingestion.loader import Document

log = structlog.get_logger()


@dataclass
class TextChunk:
    content: str
    metadata: dict = field(default_factory=dict)
    chunk_index: int = 0


class TextChunker:
    """Recursive character text splitter optimized for SAP documentation."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Separators ordered by priority — try to split at natural boundaries
        self.separators = [
            "\n\n\n",       # Major section breaks
            "\n\n",         # Paragraph breaks
            "\n",           # Line breaks
            ". ",           # Sentence breaks
            "; ",           # Clause breaks
            " ",            # Word breaks
        ]

    def chunk_document(self, document: Document) -> list[TextChunk]:
        text = document.content
        text = self._clean_text(text)

        if not text:
            return []

        raw_chunks = self._recursive_split(text)

        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            if chunk_text.strip():
                chunks.append(TextChunk(
                    content=chunk_text.strip(),
                    metadata={
                        **document.metadata,
                        "chunk_index": i,
                        "chunk_total": len(raw_chunks),
                        "doc_id": document.doc_id,
                    },
                    chunk_index=i,
                ))

        log.debug("chunked_document", doc_id=document.doc_id, chunks=len(chunks))
        return chunks

    def chunk_documents(self, documents: list[Document]) -> list[TextChunk]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        log.info("chunking_complete", total_docs=len(documents), total_chunks=len(all_chunks))
        return all_chunks

    def _clean_text(self, text: str) -> str:
        # Normalize whitespace but preserve paragraph structure
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        return text.strip()

    def _recursive_split(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        # Find the best separator
        for sep in self.separators:
            if sep in text:
                parts = text.split(sep)
                return self._merge_chunks(parts, sep)

        # Fallback: hard split at chunk_size
        return self._hard_split(text)

    def _merge_chunks(self, parts: list[str], separator: str) -> list[str]:
        chunks = []
        current = ""

        for part in parts:
            candidate = current + separator + part if current else part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # If this single part exceeds chunk_size, recurse
                if len(part) > self.chunk_size:
                    chunks.extend(self._recursive_split(part))
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_end = chunks[i - 1][-self.chunk_overlap:]
            result.append(prev_end + " " + chunks[i])
        return result

    def _hard_split(self, text: str) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks
