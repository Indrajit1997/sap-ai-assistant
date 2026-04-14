from __future__ import annotations

import tempfile
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException, UploadFile

from backend.api.models import DocumentInfo, DocumentUploadResponse, URLIngestRequest, URLIngestResponse
from backend.ingestion.pipeline import IngestionPipeline
from backend.vectorstore import get_vector_store

log = structlog.get_logger()
router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile, module: str = ""):
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    allowed_extensions = {".pdf", ".html", ".htm", ".md", ".txt", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {allowed_extensions}",
        )

    # Validate file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    try:
        # Save to temp file and ingest
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        pipeline = IngestionPipeline()
        chunks_created = pipeline.ingest_file(tmp_path, module=module)

        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)

        return DocumentUploadResponse(
            message="Document ingested successfully",
            chunks_created=chunks_created,
            filename=file.filename,
        )
    except Exception as e:
        log.error("upload_error", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("/documents", response_model=DocumentInfo)
async def list_documents():
    from backend.config import get_settings
    settings = get_settings()
    store = get_vector_store()
    return DocumentInfo(
        total_chunks=store.count(),
        vector_store=settings.vector_store,
    )


@router.post("/documents/url", response_model=URLIngestResponse)
async def ingest_urls(request: URLIngestRequest):
    """Ingest one or more public URLs into the knowledge base."""
    try:
        pipeline = IngestionPipeline()
        total_chunks = pipeline.ingest_urls(request.urls, module=request.module)
        return URLIngestResponse(
            message="URLs ingested successfully",
            chunks_created=total_chunks,
            urls_processed=len(request.urls),
        )
    except Exception as e:
        log.error("url_ingest_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to ingest URLs: {str(e)}")


@router.delete("/documents/reset")
async def reset_documents():
    """Delete all documents from the vector store and start fresh."""
    store = get_vector_store()
    count_before = store.count()
    store.reset()
    log.info("documents_reset", deleted=count_before)
    return {"message": "Knowledge base reset successfully", "chunks_deleted": count_before}
