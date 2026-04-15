# SAP AI Assistant

A domain-specific RAG-powered AI chatbot for SAP documentation, KB articles, and implementation knowledge.

## Quick Start

### Prerequisites
- Python 3.11+
- API key for one of: Google Gemini (recommended), Anthropic, Groq, or AWS Bedrock

### Setup

```powershell
# Clone and setup
git clone git@github.com:Indrajit1997/sap-ai-assistant.git
cd sap-ai-assistant

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
pip install streamlit

# Copy environment config
Copy-Item .env.example .env
# Edit .env — set LLM_PROVIDER and your API key

# Start backend (terminal 1)
uvicorn backend.main:app --reload --port 8000

# Start Streamlit UI (terminal 2)
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

Open http://localhost:8501 in your browser.

### Ingest Documents

```powershell
# Ingest sample SAP docs
python scripts/ingest.py --path docs/sample/ --recursive --module S4HANA

# Ingest a single file
python scripts/ingest.py --path docs/your-doc.pdf

# Ingest from URL
python scripts/ingest.py --url https://help.sap.com/docs/...
```

### Deploy on a Remote Machine

```bash
bash scripts/start_codespace.sh
```

This script auto-bootstraps `.env`, ingests sample docs, starts the backend, and launches the Streamlit UI.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full system design.

## Project Structure

```
sap-ai-assistant/
├── .devcontainer/           # GitHub Codespaces / devcontainer config
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration (env-based)
│   ├── ingestion/           # Document loading, chunking, embedding
│   ├── vectorstore/         # ChromaDB + OpenSearch adapters
│   ├── rag/                 # Retrieval, reranking, prompt building
│   ├── llm/                 # LLM provider adapters (Gemini, Anthropic, Groq, Bedrock)
│   └── api/                 # API routes and models
├── frontend/
│   ├── streamlit_app.py     # Streamlit UI (chat, upload, URL ingest, reset)
│   └── react-app/           # React UI (in progress)
├── docs/sample/             # Sample SAP docs for testing
└── scripts/
    ├── ingest.py            # CLI ingestion tool (files + URLs)
    └── start_codespace.sh   # One-command server launcher
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat` | Send a message, get RAG-grounded response |
| GET | `/api/v1/chat/stream` | SSE streaming chat |
| POST | `/api/v1/documents/upload` | Upload documents for ingestion |
| POST | `/api/v1/documents/url` | Ingest from public URLs |
| GET | `/api/v1/documents` | List ingested documents |
| DELETE | `/api/v1/documents/{id}` | Remove a document |
| DELETE | `/api/v1/documents/reset` | Clear entire knowledge base |
| GET | `/api/v1/health` | Health check |

## LLM Providers

| Provider | Config | Notes |
|---|---|---|
| **Google Gemini** | `LLM_PROVIDER=gemini` + `GEMINI_API_KEY` | Recommended, free tier available |
| **Groq** | `LLM_PROVIDER=groq` + `GROQ_API_KEY` | Fast inference, free tier |
| **Anthropic** | `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` | Claude models |
| **AWS Bedrock** | `LLM_PROVIDER=bedrock` + AWS credentials | Enterprise |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Vector Store**: ChromaDB (dev) / OpenSearch (prod)
- **LLM**: Google Gemini / Anthropic / Groq / AWS Bedrock
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, local, free)
- **Frontend**: Streamlit (with retry + copy features)
- **Document Processing**: PDF, DOCX, HTML, Markdown, TXT, URLs
