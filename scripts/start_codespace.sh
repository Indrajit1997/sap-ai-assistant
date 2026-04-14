#!/usr/bin/env bash
# Start both backend and frontend for Codespaces
set -e

echo "========================================="
echo "  SAP AI Assistant - Codespace Launcher"
echo "========================================="

# 1. Create .env if it doesn't exist
if [ ! -f .env ]; then
  echo ""
  echo "⚠️  No .env file found. Create one from .env.example:"
  echo "   cp .env.example .env"
  echo "   Then edit .env and configure your provider credentials"
  echo "   (for example: LLM_PROVIDER=gemini plus GEMINI_API_KEY,"
  echo "   or LLM_PROVIDER=anthropic plus ANTHROPIC_API_KEY)."
  echo ""
fi

# 2. Ingest sample docs if vector store is empty
if [ ! -d "data/chroma" ]; then
  echo "📄 Ingesting sample SAP documentation..."
  python scripts/ingest.py --path docs/sample/ --recursive --module S4HANA
  echo ""
fi

# 3. Start backend in background
echo "🚀 Starting backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

cleanup() {
  if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" > /dev/null 2>&1; then
    kill "$BACKEND_PID" > /dev/null 2>&1 || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "   Backend PID: $BACKEND_PID (logs: /tmp/backend.log)"

# Wait for backend to be ready
echo "   Waiting for backend..."
BACKEND_READY=0
for i in {1..15}; do
  if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend ready!"
    BACKEND_READY=1
    break
  fi
  sleep 1
done

if [ "$BACKEND_READY" -ne 1 ]; then
  echo "   ❌ Backend failed to start. Recent logs:"
  tail -n 50 /tmp/backend.log || true
  exit 1
fi

# 4. Start Streamlit (foreground so terminal stays open)
echo ""
echo "🎨 Starting Streamlit UI on port 8501..."
echo "   Share the port 8501 URL from the PORTS tab with your testers!"
echo "========================================="
echo ""
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
