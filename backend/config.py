from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── LLM ──
    llm_provider: str = "bedrock"
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model_id: str = "gemini-2.0-flash"
    groq_api_key: str = ""
    groq_model_id: str = "llama-3.3-70b-versatile"

    # ── Embeddings ──
    embedding_provider: str = "local"
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Vector Store ──
    vector_store: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    opensearch_host: str = ""
    opensearch_port: int = 443
    opensearch_index: str = "sap-docs"

    # ── RAG ──
    rag_top_k: int = 5
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    rag_score_threshold: float = 0.3

    # ── API ──
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:8501"

    # ── Logging ──
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
