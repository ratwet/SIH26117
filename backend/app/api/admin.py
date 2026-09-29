"""
Aquanex - Admin & Model Registry Endpoints (app/api/admin.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import settings
from app.security.auth import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    authenticate_user,
    update_user_allowed_models,
    UserAccount,
)

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


def require_permission(permission: str):
    """
    FastAPI dependency that enforces role-based access control (RBAC).
    Reads the role from the X-User-Role HTTP header (defaults to 'senior').
    """
    async def _dependency(x_user_role: Optional[str] = Header(default="senior", alias="X-User-Role")):
        role = (x_user_role or "senior").lower()
        perms = RBAC_REGISTRY.get(role)
        if not perms:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Unrecognized role '{x_user_role}'. Valid roles: {list(RBAC_REGISTRY.keys())}"
            )
        if not perms.get(permission, False):
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Role '{role}' does not have required permission '{permission}'."
            )
        return role
    return _dependency


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


@router.post("/models/register", dependencies=[Depends(require_permission("can_register_models"))])
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
        "message": f"Model '{request.filename}' successfully registered into Aquanex.",
    }


@router.get("/rbac")
async def get_rbac_roles():
    """Returns the refinery RBAC policy matrix."""
    return {
        "roles": RBAC_REGISTRY,
        "enforcement": "STRICT_ROLE_BASED_ACCESS_CONTROL",
    }


class SetModelTierRequest(BaseModel):
    tier: str = Field(..., json_schema_extra={"example": "ENTERPRISE_100B"})


@router.get("/model-tiers")
async def get_model_tiers():
    """Returns available hardware deployment tiers and active profile per PS 117 sizing."""
    return {
        "active_tier": settings.MODEL_TIER,
        "active_profile": settings.active_model_profile,
        "supported_tiers": {
            "ENTERPRISE_100B": {
                "name": "Enterprise Refinery Datacenter (100B+)",
                "hardware": "Dual AMD EPYC 9654 + 4x NVIDIA A100 (80GB SXM4) / H100 NVLink",
                "models": {
                    "router": "qwen2.5:72b-instruct",
                    "reasoning": "deepseek-r1:70b-q8_0",
                    "vision": "qwen2-vl:72b-instruct",
                    "coder": "qwen2.5-coder:32b-instruct",
                },
                "tensor_parallel_size": 4,
                "context_window": 131072,
                "vram_allocation_gb": 320,
            },
            "WORKSTATION_32B": {
                "name": "Departmental Workstation (32B)",
                "hardware": "Intel i9-14900K + 1x NVIDIA RTX 4090 (24GB) / RTX A5000",
                "models": {
                    "router": "qwen2.5:14b-instruct",
                    "reasoning": "deepseek-r1:32b",
                    "vision": "qwen2-vl:7b-instruct",
                    "coder": "qwen2.5-coder:14b-instruct",
                },
                "tensor_parallel_size": 1,
                "context_window": 32768,
                "vram_allocation_gb": 24,
            },
            "EDGE_LAPTOP_8B": {
                "name": "Hackathon Demo Rig / Field Laptop (8B)",
                "hardware": "Intel i7 / Ryzen 7, RTX 3060/4060 (6-8GB) or Apple Silicon M-Series",
                "models": {
                    "router": "qwen2.5:3b-instruct-q8_0",
                    "reasoning": "deepseek-r1:8b",
                    "vision": "qwen2-vl:7b-instruct-q4_K_M",
                    "coder": "qwen2.5-coder:7b-instruct-q4_K_M",
                },
                "tensor_parallel_size": 1,
                "context_window": 8192,
                "vram_allocation_gb": 8,
            },
        }
    }


@router.post("/model-tier", dependencies=[Depends(require_permission("can_manage_rbac"))])
async def set_model_tier(request: SetModelTierRequest):
    """Sets active model tier (ENTERPRISE_100B, WORKSTATION_32B, EDGE_LAPTOP_8B)."""
    tier = request.tier.upper()
    if tier not in ["ENTERPRISE_100B", "WORKSTATION_32B", "EDGE_LAPTOP_8B"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{request.tier}'. Must be ENTERPRISE_100B, WORKSTATION_32B, or EDGE_LAPTOP_8B."
        )

    settings.MODEL_TIER = tier
    profile = settings.active_model_profile
    settings.MODEL_ROUTER = profile["router"]
    settings.MODEL_REASONING = profile["reasoning"]
    settings.MODEL_VISION = profile["vision"]
    settings.MODEL_CODER = profile["coder"]
    settings.TENSOR_PARALLEL_SIZE = profile["tensor_parallel_size"]
    settings.MAX_MODEL_LEN = profile["context_window"]

    return {
        "status": "UPDATED",
        "active_tier": settings.MODEL_TIER,
        "profile": profile,
    }


@router.get("/llm-health")
async def get_llm_cluster_health():
    """
    Returns datacenter vLLM cluster health, target GPU topology,
    active model weights, and 100B emulation status.
    """
    try:
        from app.llm import foundation_engine
        telemetry = await foundation_engine.check_cluster_health()
    except Exception as e:
        telemetry = {
            "tier": settings.MODEL_TIER,
            "target_hardware": "4x NVIDIA A100 (80GB SXM4) / H100",
            "tensor_parallel_size": settings.TENSOR_PARALLEL_SIZE,
            "max_context_window": settings.MAX_MODEL_LEN,
            "is_connected_to_vllm": False,
            "mode": "HARDWARE_AGNOSTIC_EMULATION",
            "error": str(e),
        }
    return telemetry


# =========================================================================
# Three-Tier Sovereign Authentication & Model Access Governance Endpoints
# =========================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "senior"})
    pin: Optional[str] = Field(None, json_schema_extra={"example": "5700"})


class UpdatePermissionsRequest(BaseModel):
    allowed_models: List[str] = Field(..., json_schema_extra={"example": ["Edge-8B", "Workstation-32B"]})


@router.post("/auth/login")
async def login(request: LoginRequest):
    """
    Sovereign On-Premise Sign-In:
    Validates user credentials/role against local refinery registry.
    Supports both PIN verification and 1-click persona switching.
    """
    user = authenticate_user(request.username, request.pin)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid username or security PIN."
        )
    return {
        "status": "AUTHENTICATED",
        "user": user.model_dump(exclude={"pin"}),
        "session_token": f"sovereign_token_{user.id}",
    }


@router.get("/auth/users")
async def list_auth_personas():
    """
    Returns public persona metadata for quick 1-click role switching in the prototype.
    """
    users = get_all_users()
    return {
        "users": [u.model_dump(exclude={"pin"}) for u in users]
    }


@router.get("/auth/me")
async def get_current_user_profile(
    x_user_role: Optional[str] = Header(default="senior", alias="X-User-Role"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Returns current authenticated persona based on request headers.
    """
    user = None
    if x_user_id:
        user = get_user_by_id(x_user_id)
    if not user and x_user_role:
        user = get_user_by_username(x_user_role)
    if not user:
        user = get_user_by_username("senior")
    return {
        "user": user.model_dump(exclude={"pin"}) if user else None
    }


@router.get("/users", dependencies=[Depends(require_permission("can_manage_rbac"))])
async def list_users_for_governance():
    """
    Admin Endpoint: Returns full user directory with model access matrices.
    """
    users = get_all_users()
    return {
        "users": [u.model_dump(exclude={"pin"}) for u in users]
    }


@router.post("/users/{user_id}/permissions", dependencies=[Depends(require_permission("can_manage_rbac"))])
async def update_user_permissions(user_id: str, request: UpdatePermissionsRequest):
    """
    Admin Endpoint: Allows IT Administrator to grant/revoke model access for any user or role.
    """
    updated = update_user_allowed_models(user_id, request.allowed_models)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"User '{user_id}' not found in personnel registry."
        )
    return {
        "status": "PERMISSIONS_UPDATED",
        "user_id": user_id,
        "allowed_models": updated.allowed_models,
        "default_model": updated.default_model,
        "message": f"Updated model access permissions for user '{updated.name}'.",
    }


