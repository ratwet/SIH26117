"""
SovereignWorkbench — Main FastAPI Application Entry Point (app/main.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).

Runs on Node 2 (GPU Server / Gaming Laptop) on an isolated local subnet.
Connects the LangGraph state machine with the desktop client UI.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.health import router as health_router
from app.api.admin import router as admin_router
from app.api.chat import router as chat_router
from app.api.files import router as files_router
from app.api.telemetry import router as telemetry_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    # Ensure critical directory infrastructure exists
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    (settings.DATA_DIR / "uploads").mkdir(exist_ok=True)
    (settings.DATA_DIR / "deliverables").mkdir(exist_ok=True)
    settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(f"🛡️  SOVEREIGNWORKBENCH — NODE 1: SERVER WORKSTATION ({settings.SERVER_NODE_IP})")
    print("   Air-Gap Operational Mode: STRICT ZERO-WAN ISOLATION")
    print(f"   Listening on: http://{settings.HOST}:{settings.PORT} (LAN Target: http://{settings.SERVER_NODE_IP}:{settings.PORT})")
    print(f"   Ollama Host:  {settings.OLLAMA_HOST} (Strict Loopback Isolation)")
    print("=" * 65)

    yield

    print("\n🛑 SovereignWorkbench backend shutting down gracefully.")


# Create FastAPI application
app = FastAPI(
    title="SovereignWorkbench Backend",
    description="Sovereign On-Premise Agentic AI Workbench for Confidential Industrial Work (MRPL PS 117)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for desktop client & local LAN access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(telemetry_router)

# Mount Aquanex Frontend SPA if built in frontend/dist
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_aquanex_spa():
        """Serves compiled Aquanex UI to any browser on the isolated LAN."""
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    @app.get("/api/info")
    async def api_info():
        """Root API information endpoint."""
        return {
            "system": f"SovereignWorkbench Server Node (Node 1: {settings.SERVER_NODE_IP})",
            "organization": "Mangalore Refinery and Petrochemicals Limited (MRPL)",
            "security": "100% On-Premise Air-Gapped",
            "lan_topology": {
                "server_node_1": f"http://{settings.SERVER_NODE_IP}:{settings.PORT}",
                "admin_node_2": f"http://{settings.ADMIN_NODE_IP}",
                "user_node_3": f"http://{settings.USER_NODE_IP}",
            },
            "documentation": "/docs",
            "health_check": "/api/health",
        }

    @app.get("/{file_path:path}", include_in_schema=False)
    async def serve_static_or_spa(file_path: str):
        """Serves public assets (e.g. logos, favicon) or falls back to index.html."""
        target = FRONTEND_DIST / file_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    async def root():
        """Root landing endpoint providing system identity."""
        return {
            "system": f"SovereignWorkbench Server Node (Node 1: {settings.SERVER_NODE_IP})",
            "organization": "Mangalore Refinery and Petrochemicals Limited (MRPL)",
            "security": "100% On-Premise Air-Gapped",
            "lan_topology": {
                "server_node_1": f"http://{settings.SERVER_NODE_IP}:{settings.PORT}",
                "admin_node_2": f"http://{settings.ADMIN_NODE_IP}",
                "user_node_3": f"http://{settings.USER_NODE_IP}",
            },
            "documentation": "/docs",
            "health_check": "/api/health",
        }
