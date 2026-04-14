from fastapi import APIRouter

from backend.api.models import HealthResponse
from backend.config import get_settings
from backend.vectorstore import get_vector_store

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    store = get_vector_store()
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        vector_store=settings.vector_store,
        document_count=store.count(),
    )
