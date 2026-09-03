"""
SovereignWorkbench — Unified API Package (app/api/__init__.py)
Includes endpoints owned by Rajat (Chat, Health, Admin) and Anand (Files, Telemetry).
"""

from .chat import router as chat_router
from .health import router as health_router
from .admin import router as admin_router
from .files import router as files_router
from .telemetry import router as telemetry_router

__all__ = [
    "chat_router",
    "health_router",
    "admin_router",
    "files_router",
    "telemetry_router",
]
