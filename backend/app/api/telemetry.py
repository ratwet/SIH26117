"""
SovereignWorkbench — Telemetry & Security API (app/api/telemetry.py)
Provides network socket monitoring endpoints and SSE streaming proving 0 WAN packets,
plus cryptographic audit ledger verification routes.
"""

import asyncio
import json
from typing import Dict, Any, List
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import NetworkStats, AuditEvent
from app.security.network_monitor import read_network_stats
from app.security.audit_chain import verify_audit_chain, get_audit_ledger
from app.api.admin import require_permission
from fastapi import Depends

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry & Security"])


@router.get("/network", response_model=NetworkStats)
async def get_network_telemetry() -> NetworkStats:
    """
    Get current network telemetry stats proving zero outbound WAN bytes.
    """
    return read_network_stats()


@router.get("/network/stream")
async def stream_network_telemetry():
    """
    Server-Sent Events (SSE) stream broadcasting network stats every 1.5 seconds.
    Used by the frontend HUD gauge for real-time compliance visualization.
    """
    async def event_generator():
        while True:
            stats = read_network_stats()
            data_json = stats.model_dump_json()
            yield f"data: {data_json}\n\n"
            await asyncio.sleep(1.5)
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/audit", dependencies=[Depends(require_permission("can_view_audit_logs"))])
async def get_audit_status() -> Dict[str, Any]:
    """
    Verify the cryptographic integrity of the SHA-256 audit ledger
    and return the latest ledger records.
    """
    is_valid, msg, count = verify_audit_chain()
    recent_events = get_audit_ledger(limit=25)
    
    return {
        "chain_valid": is_valid,
        "verification_message": msg,
        "total_blocks": count,
        "recent_events": [e.model_dump() for e in recent_events]
    }
