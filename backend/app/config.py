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

    # --- Ollama & vLLM Model Serving Engine (Strict Loopback Isolation per ADR-007) ---
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    VLLM_HOST: str = "http://127.0.0.1:8001/v1"

    # Strict Air-Gapped / No-Emulation Policy:
    # When False (default), the system refuses to run if no live model (Ollama / vLLM) is connected.
    ALLOW_EMULATION: bool = False

    # Model Deployment Tier (PS 117 Sizing: ENTERPRISE_100B, WORKSTATION_32B, EDGE_LAPTOP_8B)
    MODEL_TIER: str = "ENTERPRISE_100B"
    TENSOR_PARALLEL_SIZE: int = 4
    MAX_MODEL_LEN: int = 131072

    # Model tags (Defaults configured for 100B+ Enterprise Refinery Datacenter Tier)
    MODEL_ROUTER: str = "qwen2.5:72b-instruct"
    MODEL_REASONING: str = "deepseek-r1:70b-q8_0"
    MODEL_VISION: str = "qwen2-vl:72b-instruct"
    MODEL_CODER: str = "qwen2.5-coder:32b-instruct"

    @property
    def active_model_profile(self) -> dict:
        """Returns the hardware profile, model tags, and context windows for active tier."""
        profiles = {
            "ENTERPRISE_100B": {
                "tier_name": "Enterprise Refinery Datacenter (100B+)",
                "hardware_spec": "Dual AMD EPYC 9654 + 4x NVIDIA A100 (80GB SXM4) / H100 NVLink",
                "router": "qwen2.5:72b-instruct",
                "reasoning": "deepseek-r1:70b-q8_0",
                "vision": "qwen2-vl:72b-instruct",
                "coder": "qwen2.5-coder:32b-instruct",
                "tensor_parallel_size": 4,
                "context_window": 131072,
                "vram_allocation_gb": 320,
            },
            "WORKSTATION_32B": {
                "tier_name": "Departmental Workstation (32B)",
                "hardware_spec": "Intel i9-14900K + 1x NVIDIA RTX 4090 (24GB) / RTX A5000",
                "router": "qwen2.5:14b-instruct",
                "reasoning": "deepseek-r1:32b",
                "vision": "qwen2-vl:7b-instruct",
                "coder": "qwen2.5-coder:14b-instruct",
                "tensor_parallel_size": 1,
                "context_window": 32768,
                "vram_allocation_gb": 24,
            },
            "EDGE_LAPTOP_8B": {
                "tier_name": "Hackathon Demo Rig / Field Laptop (8B)",
                "hardware_spec": "Intel i7 / Ryzen 7, RTX 3060/4060 (6-8GB) or Apple Silicon M-Series",
                "router": "qwen2.5:3b-instruct-q8_0",
                "reasoning": "deepseek-r1:8b",
                "vision": "qwen2-vl:7b-instruct-q4_K_M",
                "coder": "qwen2.5-coder:7b-instruct-q4_K_M",
                "tensor_parallel_size": 1,
                "context_window": 8192,
                "vram_allocation_gb": 8,
            },
        }
        return profiles.get(self.MODEL_TIER, profiles["ENTERPRISE_100B"])

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
    AIR_GAP_STRICT: bool = True
    SIMULATE_AIR_GAP_BREACH: bool = False
    WAN_INTERFACE_OVERRIDE: str = ""
    ALLOW_UNSANDBOXED_FALLBACK: bool = False

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://192.168.1.100:8000",
        "http://192.168.1.101:8000",
        "http://192.168.1.102:8000",
        "http://192.168.1.100:5173",
        "http://192.168.1.101:5173",
        "http://192.168.1.102:5173",
    ]

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
