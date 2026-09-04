#!/usr/bin/env bash
# =====================================================================
# SovereignWorkbench — Service Launcher (scripts/start_workbench.sh)
# Starts local Ollama model engine and FastAPI/LangGraph backend server
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}🛡️  STARTING SOVEREIGNWORKBENCH (MRPL PS 117) — SERVER NODE        ${NC}"
echo -e "${BLUE}=====================================================================${NC}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

# 1. Check Ollama Daemon
echo -e "\n[1/3] Checking Local Ollama Model Engine..."
if curl -s -f http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Ollama is running on http://127.0.0.1:11434${NC}"
else
  echo -e "${YELLOW}⚠️  Ollama not responding on 127.0.0.1:11434.${NC}"
  echo -e "Attempting to start Ollama daemon..."
  if command -v ollama > /dev/null 2>&1; then
    OLLAMA_NO_UPDATE=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve > /dev/null 2>&1 &
    sleep 3
    echo -e "${GREEN}✅ Ollama daemon launched in background.${NC}"
  else
    echo -e "${RED}❌ Ollama binary not found. Running with mock models fallback.${NC}"
  fi
fi

# 2. Check Directory Infrastructure
echo -e "\n[2/3] Verifying Local Storage Infrastructure..."
mkdir -p data/uploads data/deliverables data/chromadb models_storage
echo -e "${GREEN}✅ Storage directories verified: data/ & models_storage/${NC}"

# 3. Launch FastAPI / LangGraph Backend
echo -e "\n[3/3] Launching FastAPI Gateway & LangGraph State Engine..."
echo -e "Bound to: ${GREEN}http://0.0.0.0:8000${NC} (Accessible at http://192.168.1.100:8000)"
echo -e "Swagger Docs: ${BLUE}http://192.168.1.100:8000/docs${NC}"
echo -e "Health Check: ${BLUE}http://192.168.1.100:8000/api/health${NC}"
echo -e "${BLUE}---------------------------------------------------------------------${NC}"

# Check virtualenv if present
if [ -d "$HOME/myenv" ]; then
  source "$HOME/myenv/bin/activate"
elif [ -d ".venv" ]; then
  source .venv/bin/activate
elif [ -d "../myenv" ]; then
  source ../myenv/bin/activate
fi

exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
