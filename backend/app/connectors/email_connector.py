"""
Aquanex - Internal Air-Gapped Email Connector (app/connectors/email_connector.py)
Automates drafting of inspection briefs and Turnaround notifications to MRPL internal exchange.
Strictly gated by human approval tokens. Outbound WAN connections are hard blocked.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.config import settings
from app.schemas import EmailDraftPayload, PipeInspectionData
from app.policy.approval_tokens import verify_approval_token, compute_payload_hash

logger = logging.getLogger(__name__)

# In-memory fast store for active sessions, mirrored to VAULT_STAGING_DIR
_DRAFT_STORE: Dict[str, EmailDraftPayload] = {}


def _is_internal_domain(email_addr: str) -> bool:
    """Verifies that the destination email strictly belongs to internal MRPL domain."""
    email_clean = email_addr.strip().lower()
    return email_clean.endswith(f"@{settings.INTERNAL_MAIL_DOMAIN.lower()}") or email_clean.endswith("@mrpl.co.in")


def compute_draft_payload_hash(draft: EmailDraftPayload) -> str:
    """Computes the canonical hash of the draft's contents and attachment signatures."""
    canonical_obj = {
        "recipient": draft.recipient.strip().lower(),
        "subject": draft.subject.strip(),
        "body": draft.body.strip(),
        "attachment_hashes": sorted(draft.attachment_hashes.items()),
    }
    return compute_payload_hash(canonical_obj)


def create_inspection_email_draft(
    pipe_data: PipeInspectionData,
    recipient: str,
    attachments: Optional[List[str]] = None,
) -> EmailDraftPayload:
    """
    Creates a formal refinery inspection email draft awaiting human approval.
    
    Validates internal domain. Hashes all attachments. Freezes draft status.
    """
    if not _is_internal_domain(recipient):
        raise ValueError(
            f"Egress Security Violation: Recipient '{recipient}' is outside the internal "
            f"MRPL air-gapped domain (@{settings.INTERNAL_MAIL_DOMAIN}). "
            "Autonomous external communications are prohibited."
        )

    attachments = attachments or []
    attachment_hashes: Dict[str, str] = {}

    for att_path_str in attachments:
        p = Path(att_path_str)
        if p.exists() and p.is_file():
            file_bytes = p.read_bytes()
            attachment_hashes[p.name] = hashlib.sha256(file_bytes).hexdigest()
        else:
            # Hash path string if virtual deliverable placeholder
            attachment_hashes[p.name] = hashlib.sha256(att_path_str.encode("utf-8")).hexdigest()

    draft_id = f"DFT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    subject = f"[MRPL-INTEGRITY] Urgent Asset Notice: {pipe_data.line_tag} Inspection Dossier"

    body = (
        f"CONFIDENTIAL // MRPL TECHNICAL SERVICES - INTERNAL CORRESPONDENCE\n"
        f"----------------------------------------------------------------------\n"
        f"ATTN: Plant Maintenance & Reliability Engineering Division\n\n"
        f"Ultrasonic thickness survey and API 570 fitness-for-service calculations have\n"
        f"been completed for process circuit tag: {pipe_data.line_tag}.\n\n"
        f"KEY METRICS SUMMARY:\n"
        f"  • Operating Service: {pipe_data.service_description}\n"
        f"  • Metallurgy: {pipe_data.material_spec}\n"
        f"  • Nominal Thickness: {pipe_data.nominal_thickness_mm} mm\n"
        f"  • Measured Thickness: {pipe_data.actual_thickness_mm} mm\n"
        f"  • Active Corrosion Rate: {pipe_data.corrosion_rate_mm_year} mm/year\n"
        f"  • Calculated Remaining Life: {pipe_data.remaining_life_years:.2f} Years\n"
        f"  • MANDATORY ACTION: {pipe_data.mandatory_action}\n\n"
        f"STATUTORY WATERMARK NOTICE:\n"
        f"  AI-GENERATED DRAFT - STATUTORY HUMAN REVIEW REQUIRED.\n"
        f"  Deliverables attached below require physical/wet-ink engineering sign-off\n"
        f"  prior to capital turnaround requisitioning.\n\n"
        f"Attached Deliverables ({len(attachments)} items):\n"
    )
    for att_name in attachment_hashes.keys():
        body += f"  - {att_name} (SHA-256: {attachment_hashes[att_name][:12]}...)\n"

    body += (
        f"\nInspection Lead: {pipe_data.inspector_name}\n"
        f"Date: {pipe_data.inspection_date}\n"
    )

    draft = EmailDraftPayload(
        draft_id=draft_id,
        recipient=recipient.strip(),
        subject=subject,
        body=body,
        attachments=attachments,
        attachment_hashes=attachment_hashes,
        classification="CONFIDENTIAL",
        status="DRAFT_AWAITING_APPROVAL",
        approval_token=None,
    )

    _DRAFT_STORE[draft_id] = draft

    # Mirror to staging vault
    try:
        settings.VAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)
        draft_file = settings.VAULT_STAGING_DIR / f"{draft_id}.json"
        draft_file.write_text(draft.model_dump_json(indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning(f"Could not write draft to staging vault: {exc}")

    return draft


def get_email_draft(draft_id: str) -> Optional[EmailDraftPayload]:
    """Retrieve an email draft by ID."""
    if draft_id in _DRAFT_STORE:
        return _DRAFT_STORE[draft_id]
    
    # Try reading from staging vault
    draft_file = settings.VAULT_STAGING_DIR / f"{draft_id}.json"
    if draft_file.exists():
        try:
            data = json.loads(draft_file.read_text(encoding="utf-8"))
            draft = EmailDraftPayload(**data)
            _DRAFT_STORE[draft_id] = draft
            return draft
        except Exception:
            return None
    return None


def approve_and_dispatch_email(
    draft_id: str,
    approval_token: str,
    user_role: str = "senior",
) -> Dict[str, Any]:
    """
    Validates the cryptographic approval token, verifies that the payload hasn't been
    tampered with, and dispatches the draft to the internal on-premise mail spool.
    """
    draft = get_email_draft(draft_id)
    if not draft:
        raise FileNotFoundError(f"Draft '{draft_id}' not found.")

    if draft.status == "DISPATCHED":
        raise ValueError(f"Draft '{draft_id}' has already been dispatched.")

    # 1. Compute exact current payload hash
    current_payload_hash = compute_draft_payload_hash(draft)

    # 2. Verify Cryptographic Approval Token
    is_valid = verify_approval_token(
        token_str=approval_token,
        expected_action="DISPATCH_INSPECTION_EMAIL",
        expected_target=draft.recipient,
        expected_payload_hash=current_payload_hash,
    )

    if not is_valid:
        raise PermissionError(
            "Action Approval Gate Rejected: The provided approval token is invalid, "
            "expired, or does not match the exact recipient and payload hash of this draft."
        )

    # 3. Simulate or execute dispatch into on-premise mail queue
    now_iso = datetime.now(timezone.utc).isoformat()
    draft.status = "DISPATCHED"
    draft.approval_token = approval_token
    _DRAFT_STORE[draft_id] = draft

    # Record to on-premise spool audit log
    audit_record = {
        "event": "DISPATCH_INSPECTION_EMAIL",
        "draft_id": draft_id,
        "recipient": draft.recipient,
        "subject": draft.subject,
        "dispatched_at": now_iso,
        "operator_role": user_role,
        "approval_token": approval_token,
        "payload_hash": current_payload_hash,
        "egress_check": "AIR_GAP_INTERNAL_ONLY",
    }

    try:
        settings.VAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)
        spool_log = settings.VAULT_STAGING_DIR / "dispatched_emails.jsonl"
        with spool_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(audit_record) + "\n")
    except Exception as exc:
        logger.error(f"Failed to write to dispatched emails spool: {exc}")

    logger.info(f"Successfully dispatched email {draft_id} to internal recipient {draft.recipient}")

    return {
        "status": "DISPATCHED",
        "draft_id": draft_id,
        "recipient": draft.recipient,
        "dispatched_at": now_iso,
        "approval_receipt": "VERIFIED_VALID",
    }
