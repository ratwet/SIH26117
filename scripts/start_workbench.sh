#!/usr/bin/env bash
# =====================================================================
# SovereignWorkbench - Service Launcher (scripts/start_workbench.sh)
# Starts local Ollama model engine and FastAPI/LangGraph backend server
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}🛡️  STARTING SOVEREIGNWORKBENCH (MRPL PS 117) - SERVER NODE        ${NC}"
echo -e "${BLUE}=====================================================================${NC}"

# 1. Check Ollama Daemon
echo -e "\n[1/3] Checking Local Ollama Model Engine..."
if curl -s -f http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Ollama is running on http://127.0.0.1:11434${NC}"
else
  echo -e "${YELLOW}⚠️  Ollama not responding on 127.0.0.1:11434.${NC}"
  if command -v ollama > /dev/null 2>&1; then
    echo -e "Attempting to start Ollama daemon in background..."
    OLLAMA_NO_UPDATE=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ Ollama daemon launched in background.${NC}"
  else
    echo -e "${YELLOW}ℹ️  Ollama binary not found. Sovereign hardware-agnostic emulation engine will activate.${NC}"
  fi
fi

# 2. Check Directory Infrastructure
echo -e "\n[2/3] Verifying Local Storage Infrastructure..."
mkdir -p data/uploads data/deliverables data/chromadb models_storage
echo -e "${GREEN}✅ Storage directories verified: data/ & models_storage/${NC}"

# 3. Locate Python & Uvicorn Runtime
echo -e "\n[3/3] Launching FastAPI Gateway & LangGraph State Engine..."
export PYTHONPATH="$ROOT_DIR/backend:$PYTHONPATH"

UVICORN_BIN=""
if [ -x "$HOME/myenv/bin/uvicorn" ]; then
  UVICORN_BIN="$HOME/myenv/bin/uvicorn"
elif [ -x "$ROOT_DIR/.venv/bin/uvicorn" ]; then
  UVICORN_BIN="$ROOT_DIR/.venv/bin/uvicorn"
elif [ -x "$ROOT_DIR/venv/bin/uvicorn" ]; then
  UVICORN_BIN="$ROOT_DIR/venv/bin/uvicorn"
elif [ -x "$HOME/.local/bin/uvicorn" ]; then
  UVICORN_BIN="$HOME/.local/bin/uvicorn"
elif command -v uvicorn > /dev/null 2>&1; then
  UVICORN_BIN="$(command -v uvicorn)"
fi

echo -e "Bound to: ${GREEN}http://0.0.0.0:8000${NC} (Local: http://127.0.0.1:8000)"
echo -e "Swagger Docs: ${BLUE}http://127.0.0.1:8000/docs${NC}"
echo -e "Health Check: ${BLUE}http://127.0.0.1:8000/api/health${NC}"
echo -e "${BLUE}---------------------------------------------------------------------${NC}"

if [ -n "$UVICORN_BIN" ]; then
  exec "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port 8000 --reload
elif [ -x "$HOME/myenv/bin/python" ]; then
  exec "$HOME/myenv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
