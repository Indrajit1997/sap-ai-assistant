from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import chat, documents, health
from backend.config import get_settings

settings = get_settings()

# ── Logging ──
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelName(settings.log_level)
    ),
)

log = structlog.get_logger()


# ── Lifespan ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting_sap_ai_assistant", vector_store=settings.vector_store, llm=settings.llm_provider)
    # Initialize vector store on startup
    from backend.vectorstore import get_vector_store
    store = get_vector_store()
    app.state.vector_store = store
    log.info("vector_store_ready", type=settings.vector_store)
    yield
    log.info("shutting_down")


# ── App ──
app = FastAPI(
    title="SAP AI Assistant",
    description="Domain-specific RAG chatbot for SAP documentation",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# ── Routes ──
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
