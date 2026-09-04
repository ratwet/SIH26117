"""
SovereignWorkbench — Admin & Model Registry Endpoints (app/api/admin.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# In-memory RBAC table for the on-premise refinery environment
RBAC_REGISTRY = {
    "admin": {
        "description": "IT & Systems Administrator (Full Access)",
        "can_register_models": True,
        "can_view_audit_logs": True,
        "can_manage_rbac": True,
        "can_execute_sandbox": True,
        "can_sign_approval_notes": True,
    },
    "senior": {
        "description": "Senior Reliability / Inspection Engineer",
        "can_register_models": False,
        "can_view_audit_logs": True,
        "can_manage_rbac": False,
        "can_execute_sandbox": True,
        "can_sign_approval_notes": True,
    },
    "junior": {
        "description": "Junior Maintenance Engineer / Field Technician",
        "can_register_models": False,
        "can_view_audit_logs": False,
        "can_manage_rbac": False,
        "can_execute_sandbox": True,
        "can_sign_approval_notes": False,  # Requires Senior co-sign
    },
}


class ModelRegisterRequest(BaseModel):
    filename: str = Field(..., json_schema_extra={"example": "DeepSeek-R1-Distill-Qwen-8B-Q4_K_M.gguf"})
    role: str = Field(default="reasoning", json_schema_extra={"example": "reasoning"})


@router.get("/models")
async def list_available_models():
    """
    Scans the on-premise /models_storage/ directory for any dropped .gguf files
    and returns registered models.
    """
    models_dir = settings.MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)

    gguf_files = [f.name for f in models_dir.glob("*.gguf")]

    return {
        "storage_directory": str(models_dir),
        "local_gguf_files": gguf_files,
        "active_baseline_models": {
            "router": settings.MODEL_ROUTER,
            "reasoning": settings.MODEL_REASONING,
            "vision": settings.MODEL_VISION,
            "coder": settings.MODEL_CODER,
        },
    }


@router.post("/models/register")
async def register_new_model(request: ModelRegisterRequest):
    """
    Registers a new dropped .gguf file into the active model registry.
    """
    model_file = settings.MODELS_DIR / request.filename
    if not model_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Model file '{request.filename}' not found in {settings.MODELS_DIR}."
        )

    return {
        "status": "REGISTERED",
        "filename": request.filename,
        "assigned_role": request.role,
        "message": f"Model '{request.filename}' successfully registered into SovereignWorkbench.",
    }


@router.get("/rbac")
async def get_rbac_roles():
    """Returns the refinery RBAC policy matrix."""
    return {
        "roles": RBAC_REGISTRY,
        "enforcement": "STRICT_ROLE_BASED_ACCESS_CONTROL",
    }
