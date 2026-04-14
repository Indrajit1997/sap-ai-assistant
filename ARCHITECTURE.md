# SAP AI Assistant — Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                               │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐   │
│  │   Streamlit App   │    │   React + Vite (Production UI)      │   │
│  │   (Quick Demo)    │    │   - Chat Window + Streaming          │   │
│  │                   │    │   - Source Citation Panel             │   │
│  │                   │    │   - Document Upload                   │   │
│  └────────┬─────────┘    └──────────────┬───────────────────────┘   │
│           │                              │                           │
│           └──────────┬───────────────────┘                           │
│                      ▼                                               │
│              REST API / WebSocket                                    │
└──────────────────────┼──────────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────────┐
│                  API LAYER (FastAPI)                                 │
│  ┌───────────────────┴────────────────────────────────────────┐     │
│  │  /api/v1/chat          → Chat + streaming responses        │     │
│  │  /api/v1/chat/feedback → User feedback on responses        │     │
│  │  /api/v1/documents     → Upload, list, delete documents    │     │
│  │  /api/v1/health        → Health check + readiness          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Middleware: CORS, Rate Limiting, Request ID, Error Handling        │
└──────────────────────┼──────────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────────┐
│                  RAG ENGINE                                          │
│                                                                      │
│  ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌──────────────┐   │
│  │  Query    │──▶│ Retriever │──▶│ Reranker │──▶│   Prompt     │   │
│  │  Parser   │   │           │   │          │   │   Builder    │   │
│  └──────────┘   └───────────┘   └──────────┘   └──────┬───────┘   │
│                                                         │           │
│                                                         ▼           │
│                                                  ┌─────────────┐   │
│                                                  │  LLM Client │   │
│                                                  │ (Bedrock /   │   │
│                                                  │  Anthropic)  │   │
│                                                  └─────────────┘   │
└──────────────────────┼──────────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────────┐
│              DOCUMENT INGESTION PIPELINE                             │
│                                                                      │
│  Documents ──▶ Loader ──▶ Chunker ──▶ Embedder ──▶ Vector Store    │
│  (PDF/HTML/     (Parse)   (Semantic    (Embedding    (ChromaDB /    │
│   MD/DOCX)                Chunking)    Model)        OpenSearch)    │
│                                                                      │
│  Supported: PDF, HTML, Markdown, DOCX, Plain Text                   │
│  Chunking: Recursive with overlap (512 tokens, 50 overlap)          │
│  Embeddings: Amazon Titan / sentence-transformers                   │
└─────────────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────────┐
│              DATA / STORAGE LAYER                                    │
│                                                                      │
│  ┌─────────────────┐         ┌─────────────────────────────────┐   │
│  │   ChromaDB       │         │   AWS OpenSearch Serverless     │   │
│  │   (Development)  │         │   (Production)                  │   │
│  │   - Local persist│         │   - Managed, scalable           │   │
│  │   - Zero config  │         │   - k-NN vector search          │   │
│  └─────────────────┘         └─────────────────────────────────┘   │
│                                                                      │
│  Both implement VectorStoreBase interface → swap with config        │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **API Framework** | FastAPI | Async, auto-docs, streaming support, Pydantic validation |
| **Vector Store (Dev)** | ChromaDB | Zero-setup, persistent, great for hackathon |
| **Vector Store (Prod)** | OpenSearch | AWS-native, scalable, k-NN support |
| **LLM** | AWS Bedrock (Claude) | Enterprise-grade, fallback to direct Anthropic |
| **Embeddings** | Sentence-Transformers / Titan | Local-first with cloud fallback |
| **Chunking** | Recursive Character | SAP docs have mixed structure; recursive handles it best |
| **Frontend (Demo)** | Streamlit | 30-min setup, good for hackathon demo |
| **Frontend (Prod)** | React + Vite | Production quality, streaming, responsive |
| **Streaming** | Server-Sent Events | Real-time token streaming for chat UX |

## Data Flow

### Ingestion Flow
1. User uploads SAP documents (PDF/HTML/MD) via API or CLI
2. **Loader** extracts raw text, preserving structure metadata
3. **Chunker** splits text into semantic chunks (512 tokens, 50 overlap)
4. **Embedder** generates vector embeddings for each chunk
5. **Vector Store** indexes chunks with metadata (source, page, section)

### Query Flow
1. User sends a question via chat
2. **Query Parser** normalizes and extracts intent
3. **Retriever** searches vector store for top-k relevant chunks
4. **Reranker** re-scores results for relevance (cross-encoder)
5. **Prompt Builder** constructs a grounded prompt with context + citations
6. **LLM** generates a response with source references
7. Response streams back to frontend with citations

## SAP-Specific Optimizations
- **Metadata tagging**: Documents tagged by SAP module (S/4HANA, SF, etc.)
- **SAP vocabulary**: Custom tokenization rules for SAP transaction codes, table names
- **Source attribution**: Every response cites exact document + section
- **Confidence scoring**: Low-confidence answers flagged with suggestion to check SAP docs
