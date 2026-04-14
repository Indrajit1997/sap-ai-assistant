from __future__ import annotations

from pydantic import BaseModel, Field


# ── Chat ──
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="The user's question")
    module_filter: str | None = Field(None, description="Filter by SAP module (e.g., S4HANA, SF)")
    stream: bool = Field(False, description="Enable streaming response")


class SourceInfo(BaseModel):
    index: int
    source: str
    page: int | None = None
    module: str | None = None
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo] = []
    model: str = ""
    usage: dict | None = None


# ── Documents ──
class DocumentUploadResponse(BaseModel):
    message: str
    chunks_created: int
    filename: str


class URLIngestRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, description="List of public URLs to ingest")
    module: str = Field("", description="SAP module tag")


class URLIngestResponse(BaseModel):
    message: str
    chunks_created: int
    urls_processed: int


class DocumentInfo(BaseModel):
    total_chunks: int
    vector_store: str


# ── Health ──
class HealthResponse(BaseModel):
    status: str
    version: str
    vector_store: str
    document_count: int
