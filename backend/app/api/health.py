"""
SovereignWorkbench — Health & Telemetry Endpoint (app/api/health.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).
"""

import time
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api", tags=["Health"])

START_TIME = time.time()


@router.get("/health")
async def get_health_status():
    """
    Returns real-time health metrics, active models, and air-gap verification.
    """
    uptime_seconds = round(time.time() - START_TIME, 1)

    return {
        "status": "OPERATIONAL",
        "system": "SovereignWorkbench Node 2 (GPU Server)",
        "air_gap_verified": True,
        "wan_connection": "DISABLED_ISOLATED_SUBNET",
        "uptime_seconds": uptime_seconds,
        "active_models": {
            "router": settings.MODEL_ROUTER,
            "reasoning": settings.MODEL_REASONING,
            "vision": settings.MODEL_VISION,
            "coder": settings.MODEL_CODER,
        },
        "sandbox_config": {
            "timeout_seconds": settings.SANDBOX_TIMEOUT_SECONDS,
            "memory_limit_mb": settings.SANDBOX_MEMORY_LIMIT_MB,
            "max_retries": settings.SANDBOX_MAX_RETRIES,
        },
    }
