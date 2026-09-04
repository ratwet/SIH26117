"""
SovereignWorkbench Backend Configuration.

All settings are loaded from environment variables with sensible defaults
for local development. In production/Docker, override via .env or compose env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration with env-var overrides."""

    # --- 3-Node Physical Offline LAN Topology ---
    SERVER_NODE_IP: str = "192.168.1.100"
    ADMIN_NODE_IP: str = "192.168.1.101"
    USER_NODE_IP: str = "192.168.1.102"

    # --- Ollama Model Engine (Bound strictly to local loopback per ADR-007) ---
    OLLAMA_HOST: str = "http://127.0.0.1:11434"

    # Model tags (must match `ollama list` output)
    MODEL_ROUTER: str = "qwen2.5:3b-instruct-q8_0"
    MODEL_REASONING: str = "deepseek-r1:8b"
    MODEL_VISION: str = "qwen2-vl:7b-instruct-q4_K_M"
    MODEL_CODER: str = "qwen2.5-coder:7b-instruct-q4_K_M"

    # --- Paths ---
    DATA_DIR: Path = Path("data")
    MODELS_DIR: Path = Path("models_storage")
    RAG_DOCS_DIR: Path = Path("rag_docs")

    # --- Sandbox ---
    SANDBOX_TIMEOUT_SECONDS: int = 5
    SANDBOX_MEMORY_LIMIT_MB: int = 256
    SANDBOX_MAX_RETRIES: int = 3

    # --- RAG ---
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    CHROMA_PERSIST_DIR: Path = Path("data/chromadb")
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5

    # --- Security ---
    AUDIT_DB_PATH: Path = Path("data/mrpl_audit.db")
    NETWORK_POLL_INTERVAL_SECONDS: float = 2.0

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure critical directories exist at import time
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "uploads").mkdir(exist_ok=True)
(settings.DATA_DIR / "deliverables").mkdir(exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.RAG_DOCS_DIR.mkdir(parents=True, exist_ok=True)
