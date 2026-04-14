# Hackathon Plan — SAP AI Assistant
## April 14-15, 2026 (2 Days)

---

## DAY 1 — Foundation & Core RAG Pipeline (April 14)

### Morning (3-4 hours): Environment Setup + Ingestion Pipeline

| Time | Task | Status |
|------|------|--------|
| **Hour 1** | Environment setup | ⬜ |
| | `python -m venv .venv` + activate | |
| | `pip install -r backend/requirements.txt` | |
| | Copy `.env.example → .env`, configure keys | |
| | Test: `uvicorn backend.main:app --reload` → check `/api/v1/health` | |
| **Hour 2** | Test document ingestion | ⬜ |
| | Run: `python scripts/ingest.py --path docs/sample/ --recursive` | |
| | Verify chunks in ChromaDB (check health endpoint for count) | |
| | Upload a real SAP PDF and test ingestion | |
| **Hour 3** | Configure LLM provider | ⬜ |
| | Option A: Set up AWS Bedrock credentials | |
| | Option B: Set `LLM_PROVIDER=anthropic` + add API key | |
| | Test chat endpoint: `POST /api/v1/chat` with sample question | |
| **Hour 4** | First end-to-end test | ⬜ |
| | Ingest sample SAP docs | |
| | Ask questions via API | |
| | Verify source citations work | |

### Afternoon (3-4 hours): Frontend + Demo

| Time | Task | Status |
|------|------|--------|
| **Hour 5** | Launch Streamlit UI | ⬜ |
| | `pip install streamlit` (already in requirements) | |
| | `streamlit run frontend/streamlit_app.py` | |
| | Test chat, upload, source display | |
| **Hour 6** | Ingest real SAP content | ⬜ |
| | Gather SAP OSS notes, KB articles, PDF guides | |
| | Ingest with module tags: `--module S4HANA` | |
| | Test domain-specific Q&A quality | |
| **Hour 7** | Tune RAG parameters | ⬜ |
| | Adjust `RAG_CHUNK_SIZE` (try 256, 512, 1024) | |
| | Adjust `RAG_TOP_K` (try 3, 5, 8) | |
| | Adjust `RAG_SCORE_THRESHOLD` | |
| | Test retrieval quality with domain questions | |
| **Hour 8** | Run tests + fix issues | ⬜ |
| | `pytest backend/tests/ -v` | |
| | Fix any edge cases found | |

### Day 1 Checkpoint ✅
- [ ] Backend API running with health check
- [ ] Documents ingested into ChromaDB
- [ ] Chat endpoint returning RAG-grounded answers
- [ ] Streamlit UI functional with chat + upload
- [ ] Source citations displayed correctly

---

## DAY 2 — Polish, React UI, & Production Readiness (April 15)

### Morning (3-4 hours): React UI + Streaming

| Time | Task | Status |
|------|------|--------|
| **Hour 1** | Set up React frontend | ⬜ |
| | `cd frontend/react-app && npm install && npm run dev` | |
| | Verify Vite proxy works (requests hitting backend) | |
| | Test basic chat flow | |
| **Hour 2** | Implement streaming (optional enhancement) | ⬜ |
| | Test SSE streaming endpoint `/api/v1/chat/stream` | |
| | Connect React UI to streaming | |
| | Add typing animation | |
| **Hour 3** | OpenSearch adapter (stretch goal) | ⬜ |
| | Set up AWS OpenSearch Serverless collection | |
| | Configure credentials in `.env` | |
| | Switch `VECTOR_STORE=opensearch` | |
| | Re-ingest documents and test | |
| **Hour 4** | Add more SAP content | ⬜ |
| | Ingest SuccessFactors documentation | |
| | Ingest OnBase integration guides | |
| | Ingest internal KB articles | |

### Afternoon (3-4 hours): Demo Prep & Presentation

| Time | Task | Status |
|------|------|--------|
| **Hour 5** | Polish UI and UX | ⬜ |
| | Test edge cases (empty queries, long docs, etc.) | |
| | Improve error messages | |
| | Add loading states | |
| **Hour 6** | Prepare demo scenarios | ⬜ |
| | Scenario 1: SAP S/4HANA table question | |
| | Scenario 2: SuccessFactors API question | |
| | Scenario 3: OnBase integration question | |
| | Scenario 4: Upload new doc → immediate Q&A | |
| **Hour 7** | Create demo deck / recording | ⬜ |
| | Architecture diagram walkthrough | |
| | Live demo of all scenarios | |
| | Show source citations + confidence | |
| **Hour 8** | Final testing + cleanup | ⬜ |
| | End-to-end smoke test | |
| | Clean up code, remove debug prints | |
| | Push to git repository | |

### Day 2 Checkpoint ✅
- [ ] React UI running with polished chat experience
- [ ] Streaming responses working (if implemented)
- [ ] Multiple SAP modules ingested and queryable
- [ ] Demo scenarios prepared and tested
- [ ] Code clean, documented, pushed to repo

---

## Quick Reference Commands

```powershell
# === Backend ===
cd C:\Users\isen\source\repos\sap-ai-assistant
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000

# === Streamlit ===
streamlit run frontend/streamlit_app.py

# === React ===
cd frontend/react-app
npm install
npm run dev

# === Ingest Documents ===
python scripts/ingest.py --path docs/sample/ --recursive --module S4HANA
python scripts/ingest.py --path "C:\path\to\sap\docs.pdf" --module SF

# === Tests ===
pytest backend/tests/ -v

# === API Tests (PowerShell) ===
# Health check
Invoke-RestMethod http://localhost:8000/api/v1/health

# Chat
$body = @{question="What is ACDOCA?"} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/chat -Body $body -ContentType "application/json"

# Document count
Invoke-RestMethod http://localhost:8000/api/v1/documents
```

---

## Architecture Decisions Log

| Decision | Chosen | Why | Alternative |
|---|---|---|---|
| Vector store (dev) | ChromaDB | Zero-config, instant start | Weaviate, Qdrant |
| Vector store (prod) | OpenSearch | AWS-native, managed | Pinecone, Weaviate |
| Embeddings | sentence-transformers (local) | Free, no API needed | Titan, OpenAI Ada |
| LLM | Bedrock Claude | Enterprise, fallback ready | Anthropic direct |
| Chunking | Recursive 512 tokens | Balance context/precision | Semantic chunking |
| API | FastAPI | Async, streaming, docs | Flask, Django |
| Frontend (demo) | Streamlit | 30 min to working UI | Gradio |
| Frontend (prod) | React + Vite + Tailwind | Production-quality | Next.js, Svelte |

---

## Stretch Goals (if time permits)
1. **Conversation memory** — multi-turn context with chat history
2. **Hybrid search** — combine vector + keyword (BM25) search
3. **Feedback loop** — thumbs up/down to improve retrieval
4. **Admin panel** — manage documents, view usage stats
5. **Export answers** — save Q&A pairs as internal KB articles
6. **Evaluation harness** — automated RAG quality scoring with test questions
