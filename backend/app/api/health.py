"""
SovereignWorkbench — Health & Telemetry Endpoint (app/api/health.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).
"""

import time
from fastapi import APIRouter
from app.config import settings
from app.security.network_monitor import read_network_stats

router = APIRouter(prefix="/api", tags=["Health"])

START_TIME = time.time()


@router.get("/health")
async def get_health_status():
    """
    Returns real-time health metrics, active models, and air-gap verification.
    """
    uptime_seconds = round(time.time() - START_TIME, 1)
    net_stats = read_network_stats()

    return {
        "status": "OPERATIONAL",
        "system": "SovereignWorkbench Server Node (Node 1: 192.168.1.100)",
        "air_gap_verified": net_stats.is_air_gapped,
        "wan_connection": "DISABLED_ISOLATED_SUBNET" if net_stats.is_air_gapped else "EXTERNAL_GATEWAY_DETECTED",
        "outbound_wan_bytes_delta": net_stats.outbound_wan_bytes_delta,
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
