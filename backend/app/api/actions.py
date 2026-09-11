"""
SovereignWorkbench — Action Approval & CoWork Connectors API Router (app/api/actions.py)
Implements Human-in-the-Loop governance gates for consequential actions,
email drafting to MRPL internal exchange, and scoped enterprise vaults.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings
from app.schemas import (
    ActionApprovalRequest,
    ActionApprovalReceipt,
    EmailDraftPayload,
    EmailSendRequest,
    PipeInspectionData,
)
from app.policy.approval_tokens import generate_approval_token
from app.connectors.email_connector import (
    create_inspection_email_draft,
    approve_and_dispatch_email,
    get_email_draft,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/actions", tags=["Action Approval & Connectors"])


class DraftCreationRequest(BaseModel):
    recipient: str = Field(default="maintenance.lead@mrpl.co.in")
    pipe_data: PipeInspectionData
    attachments: Optional[List[str]] = None


@router.post("/approve", response_model=ActionApprovalReceipt)
async def request_action_approval(req: ActionApprovalRequest):
    """
    Issue a cryptographically signed HMAC-SHA256 approval token.
    Strictly restricted to Senior Engineers and Administrators.
    """
    try:
        receipt = generate_approval_token(req)
        return receipt
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(pe),
        )
    except Exception as exc:
        logger.error(f"Error generating approval token: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cryptographic approval token.",
        )


@router.post("/email/draft", response_model=EmailDraftPayload)
async def draft_inspection_email(req: DraftCreationRequest):
    """
    Generate an inspection notification email draft to the internal MRPL exchange.
    Freezes payload hash and sets status to DRAFT_AWAITING_APPROVAL.
    """
    try:
        draft = create_inspection_email_draft(
            pipe_data=req.pipe_data,
            recipient=req.recipient,
            attachments=req.attachments or [],
        )
        return draft
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as exc:
        logger.error(f"Failed to create email draft: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not compile inspection email draft.",
        )


@router.get("/email/draft/{draft_id}", response_model=EmailDraftPayload)
async def fetch_draft(draft_id: str):
    """Fetch an existing frozen email draft."""
    draft = get_email_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail=f"Draft '{draft_id}' not found.")
    return draft


@router.post("/email/dispatch")
async def dispatch_email(req: EmailSendRequest):
    """
    Dispatches an approved email draft to the internal on-premise mail spool.
    Requires a valid, unexpired, cryptographic approval token binding the draft.
    """
    try:
        result = approve_and_dispatch_email(
            draft_id=req.draft_id,
            approval_token=req.approval_token,
            user_role=req.user_role,
        )
        return result
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.error(f"Failed to dispatch approved email: {exc}")
        raise HTTPException(status_code=500, detail="Internal email dispatch failure.")


@router.get("/vault/list")
async def list_vault_files():
    """
    Lists documents in the scoped enterprise vaults (input vault and staging outbox).
    Air-gap boundary: Accessible only from local on-premise network.
    """
    input_files = []
    staging_files = []

    if settings.VAULT_INPUT_DIR.exists():
        for f in settings.VAULT_INPUT_DIR.iterdir():
            if f.is_file():
                input_files.append({
                    "name": f.name,
                    "size_bytes": f.stat().st_size,
                    "vault": "INPUT_VAULT",
                })

    if settings.VAULT_STAGING_DIR.exists():
        for f in settings.VAULT_STAGING_DIR.iterdir():
            if f.is_file():
                staging_files.append({
                    "name": f.name,
                    "size_bytes": f.stat().st_size,
                    "vault": "STAGING_VAULT",
                })

    return {
        "input_vault": input_files,
        "staging_vault": staging_files,
        "internal_domain": settings.INTERNAL_MAIL_DOMAIN,
    }
