# SAP AI Assistant

A domain-specific RAG-powered AI chatbot for SAP documentation, KB articles, and implementation knowledge.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for React frontend)
- AWS credentials (for Bedrock) OR Anthropic API key

### Setup

```powershell
# Clone and setup
cd C:\Users\isen\source\repos\sap-ai-assistant

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your API keys

# Start backend
uvicorn backend.main:app --reload --port 8000

# Start Streamlit frontend (new terminal)
streamlit run frontend/streamlit_app.py

# OR start React frontend (new terminal)
cd frontend/react-app
npm install
npm run dev
```

### Ingest Documents

```powershell
# Ingest a single file
python scripts/ingest.py --path docs/sample/your-doc.pdf

# Ingest a directory
python scripts/ingest.py --path docs/sample/ --recursive

# Ingest with specific SAP module tag
python scripts/ingest.py --path docs/ --module S4HANA --recursive
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full system design.

## Project Structure

```
sap-ai-assistant/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration (env-based)
│   ├── ingestion/           # Document loading, chunking, embedding
│   ├── vectorstore/         # ChromaDB + OpenSearch adapters
│   ├── rag/                 # Retrieval, reranking, prompt building
│   ├── llm/                 # LLM provider adapters
│   └── api/                 # API routes and models
├── frontend/
│   ├── streamlit_app.py     # Quick demo UI
│   └── react-app/           # Production React UI
├── docs/sample/             # Sample SAP docs for testing
└── scripts/                 # CLI tools
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat` | Send a message, get RAG-grounded response |
| GET | `/api/v1/chat/stream` | SSE streaming chat |
| POST | `/api/v1/documents/upload` | Upload documents for ingestion |
| GET | `/api/v1/documents` | List ingested documents |
| DELETE | `/api/v1/documents/{id}` | Remove a document |
| GET | `/api/v1/health` | Health check |

## Tech Stack

- **Backend**: Python, FastAPI, LangChain (minimal)
- **Vector Store**: ChromaDB (dev) / OpenSearch (prod)
- **LLM**: AWS Bedrock (Claude) / Anthropic API
- **Embeddings**: sentence-transformers / Amazon Titan
- **Frontend**: Streamlit (demo) + React+Vite (production)
