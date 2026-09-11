"""
SovereignWorkbench — Cryptographic Action Approval Tokens (app/policy/approval_tokens.py)
Enforces Human-in-the-Loop authorization gates for all consequential operations
(internal email dispatch, file commits, vault transfers).
"""

import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from app.config import settings
from app.schemas import ActionApprovalRequest, ActionApprovalReceipt

logger = logging.getLogger(__name__)


def compute_payload_hash(data: Any) -> str:
    """
    Generate deterministic SHA-256 hash for any arbitrary string, dict, or bytes.
    """
    if isinstance(data, bytes):
        raw_bytes = data
    elif isinstance(data, str):
        raw_bytes = data.encode("utf-8")
    else:
        # Canonical JSON encoding with sorted keys
        raw_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw_bytes).hexdigest()


def generate_approval_token(req: ActionApprovalRequest) -> ActionApprovalReceipt:
    """
    Issues a cryptographically signed one-time approval token binding human consent
    to the exact action, target recipient, and payload hash.
    
    Roles allowed: 'senior', 'admin'. Junior technicians cannot sign off.
    """
    # Enforce RBAC on approval issuance
    if req.user_role.lower() not in ("senior", "admin"):
        logger.warning(f"Unauthorized token request attempt by user={req.user_id} role={req.user_role}")
        raise PermissionError(
            f"Role '{req.user_role}' is not authorized to grant consequential action approval tokens. "
            "Senior Engineering Lead or Administrator sign-off required."
        )

    now = datetime.now(timezone.utc)
    expires_dt = now + timedelta(seconds=settings.APPROVAL_TOKEN_TTL_SECONDS)
    issued_iso = now.isoformat()
    expires_iso = expires_dt.isoformat()

    token_payload = {
        "action_type": req.action_type,
        "target": req.target,
        "payload_hash": req.payload_hash,
        "user_id": req.user_id,
        "user_role": req.user_role,
        "issued_at": issued_iso,
        "expires_at": expires_iso,
    }

    payload_json = json.dumps(token_payload, sort_keys=True, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8")

    sig = hmac.new(
        settings.APPROVAL_TOKEN_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    approval_token = f"{payload_b64}.{sig}"

    logger.info(
        f"Generated approval token for action={req.action_type} target={req.target} "
        f"user={req.user_id} expires={expires_iso}"
    )

    return ActionApprovalReceipt(
        approval_token=approval_token,
        action_type=req.action_type,
        target=req.target,
        payload_hash=req.payload_hash,
        status="APPROVED",
        issued_at=issued_iso,
        expires_at=expires_iso,
    )


def verify_approval_token(
    token_str: str,
    expected_action: str,
    expected_target: str,
    expected_payload_hash: str,
) -> bool:
    """
    Verifies that the approval token:
    1. Has a valid HMAC-SHA256 signature signed by this Sovereign instance.
    2. Has not expired.
    3. Exactly matches expected action_type, target, and payload_hash.
    
    Returns True if valid and untampered; False otherwise.
    """
    if not token_str or "." not in token_str:
        logger.error("Token verification failed: Malformed token format.")
        return False

    parts = token_str.split(".", 1)
    payload_b64, provided_sig = parts[0], parts[1]

    # 1. Verify HMAC
    expected_sig = hmac.new(
        settings.APPROVAL_TOKEN_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(provided_sig, expected_sig):
        logger.error("Token verification failed: Cryptographic signature mismatch (tampered token).")
        return False

    # 2. Parse claims
    try:
        payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
        claims = json.loads(payload_json)
    except Exception as exc:
        logger.error(f"Token verification failed: Could not decode token claims: {exc}")
        return False

    # 3. Check expiration
    expires_str = claims.get("expires_at", "")
    try:
        expires_dt = datetime.fromisoformat(expires_str)
        if datetime.now(timezone.utc) > expires_dt:
            logger.error(f"Token verification failed: Token expired at {expires_str}.")
            return False
    except Exception as exc:
        logger.error(f"Token verification failed: Invalid expiration timestamp format: {exc}")
        return False

    # 4. Check action binding
    if claims.get("action_type") != expected_action:
        logger.error(
            f"Token action mismatch: expected '{expected_action}', got '{claims.get('action_type')}'"
        )
        return False

    # 5. Check target binding (case-insensitive for emails)
    if claims.get("target", "").strip().lower() != expected_target.strip().lower():
        logger.error(
            f"Token target mismatch: expected '{expected_target}', got '{claims.get('target')}'"
        )
        return False

    # 6. Check payload hash binding
    if claims.get("payload_hash") != expected_payload_hash:
        logger.error(
            f"Token payload hash mismatch: expected '{expected_payload_hash}', got '{claims.get('payload_hash')}'. "
            "Payload has been altered after approval."
        )
        return False

    return True
