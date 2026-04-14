from __future__ import annotations

import json

import structlog
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.api.models import ChatRequest, ChatResponse, SourceInfo
from backend.rag.engine import RAGEngine

log = structlog.get_logger()
router = APIRouter()


def _get_rag_engine() -> RAGEngine:
    return RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        engine = _get_rag_engine()

        if request.stream:
            # Return SSE stream
            return await _stream_response(engine, request)

        result = await engine.query(
            question=request.question,
            module_filter=request.module_filter,
        )

        return ChatResponse(
            answer=result.answer,
            sources=[SourceInfo(**s) for s in result.sources],
            model=result.model,
            usage=result.usage,
        )
    except Exception as e:
        log.error("chat_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process your question. Please try again.")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    engine = _get_rag_engine()
    return await _stream_response(engine, request)


async def _stream_response(engine: RAGEngine, request: ChatRequest) -> EventSourceResponse:
    async def event_generator():
        try:
            stream, sources = await engine.query_stream(
                question=request.question,
                module_filter=request.module_filter,
            )

            # Stream tokens
            async for token in stream:
                yield {"event": "token", "data": json.dumps({"token": token})}

            # Send sources at the end
            yield {"event": "sources", "data": json.dumps({"sources": sources})}
            yield {"event": "done", "data": "{}"}

        except Exception as e:
            log.error("stream_error", error=str(e))
            yield {"event": "error", "data": json.dumps({"error": "An error occurred during streaming."})}

    return EventSourceResponse(event_generator())
