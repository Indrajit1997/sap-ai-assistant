from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import structlog

from backend.llm import get_llm
from backend.rag.prompt_builder import build_rag_prompt
from backend.rag.retriever import Retriever
from backend.vectorstore.base import SearchResult

log = structlog.get_logger()


@dataclass
class RAGResponse:
    answer: str
    sources: list[dict] = field(default_factory=list)
    model: str = ""
    usage: dict | None = None


class RAGEngine:
    """Orchestrates the full RAG pipeline: retrieve → build prompt → generate."""

    def __init__(self):
        self.retriever = Retriever()
        self.llm = get_llm()

    async def query(self, question: str, module_filter: str | None = None) -> RAGResponse:
        # 1. Retrieve relevant chunks
        results = self.retriever.retrieve(question, module_filter=module_filter)

        # 2. Build grounded prompt
        system_prompt, user_prompt = build_rag_prompt(question, results)

        # 3. Generate response
        llm_response = await self.llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=2048,
        )

        # 4. Build source citations
        sources = self._build_sources(results)

        log.info("rag_query_complete", question_len=len(question), sources=len(sources))

        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            model=llm_response.model,
            usage=llm_response.usage,
        )

    async def query_stream(
        self, question: str, module_filter: str | None = None
    ) -> tuple[AsyncIterator[str], list[dict]]:
        """Stream the response token by token, return sources separately."""
        # 1. Retrieve
        results = self.retriever.retrieve(question, module_filter=module_filter)

        # 2. Build prompt
        system_prompt, user_prompt = build_rag_prompt(question, results)

        # 3. Stream response
        stream = self.llm.generate_stream(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=2048,
        )

        sources = self._build_sources(results)
        return stream, sources

    def _build_sources(self, results: list[SearchResult]) -> list[dict]:
        sources = []
        for i, r in enumerate(results, 1):
            sources.append({
                "index": i,
                "source": r.metadata.get("source", "Unknown"),
                "page": r.metadata.get("page"),
                "module": r.metadata.get("sap_module"),
                "score": round(r.score, 3),
                "preview": r.content[:200] + "..." if len(r.content) > 200 else r.content,
            })
        return sources
