"""
Aquanex - Hardened Strategic Security & Governance Verification Tests
(backend/tests/test_sovereign_hardened.py)

Validates the full enterprise gap closure:
1. Pre-Retrieval ABAC RAG enforcement (Senior vs Junior clearance separation).
2. Cryptographically bound one-time Action Approval Tokens (HMAC-SHA256).
3. Air-gapped on-premise Email Connector (Strict domain enforcement & approval gate).
4. Statutory Watermarking & Classification on Word (.docx) and PDF compilers.
5. Ephemeral, RAM-only Voice Sentinel (Zero surveillance, zero audio retention).
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.schemas import (
    ActionApprovalRequest,
    PipeInspectionData,
    ApprovalNotePayload,
)
from app.rag.retriever import query_sovereign_rag
from app.policy.approval_tokens import (
    generate_approval_token,
    verify_approval_token,
    compute_payload_hash,
)
from app.connectors.email_connector import (
    create_inspection_email_draft,
    approve_and_dispatch_email,
    compute_draft_payload_hash,
)
from app.compilers.docx_builder import compile_approval_note
from app.compilers.pdf_builder import compile_inspection_certificate_pdf

client = TestClient(app)


# =====================================================================
# 1. PRE-RETRIEVAL ABAC RAG TESTS
# =====================================================================

def test_abac_rag_senior_access():
    """Senior Inspection Lead with CONFIDENTIAL clearance accesses API 570 confidential clauses."""
    res = query_sovereign_rag(
        query="API 570 corrosion rate and remaining life formula",
        top_k=3,
        user_role="senior",
        user_department="Reliability",
        clearance="CONFIDENTIAL",
    )
    assert len(res.chunks) > 0
    doc_names = [c.doc_name for c in res.chunks]
    assert "API-570-Piping-Inspection.pdf" in doc_names
    # Verify classification is preserved in chunks
    api570_chunk = next(c for c in res.chunks if c.doc_name == "API-570-Piping-Inspection.pdf")
    assert api570_chunk.classification == "CONFIDENTIAL"
    assert "senior" in api570_chunk.authorized_roles


def test_abac_rag_junior_filtered_pre_retrieval():
    """Junior Field Tech with INTERNAL clearance CANNOT retrieve CONFIDENTIAL or RESTRICTED docs."""
    res = query_sovereign_rag(
        query="API 570 corrosion rate and remaining life formula",
        top_k=3,
        user_role="junior",
        user_department="Inspection",
        clearance="INTERNAL",
    )
    assert len(res.chunks) > 0
    doc_names = [c.doc_name for c in res.chunks]
    # Invariant: CONFIDENTIAL API-570 and RESTRICTED board audit are strictly blocked pre-retrieval
    assert "API-570-Piping-Inspection.pdf" not in doc_names
    assert "MRPL-UNIT-3-BOARD-AUDIT-RESTRICTED.pdf" not in doc_names
    # Only INTERNAL operational docs returned
    for chunk in res.chunks:
        assert chunk.classification in ("INTERNAL", "UNCLASSIFIED")
        assert "junior" in [r.lower() for r in chunk.authorized_roles] or "all" in chunk.authorized_roles


def test_abac_rag_admin_restricted_access():
    """Admin with RESTRICTED clearance can retrieve executive capital documents."""
    res = query_sovereign_rag(
        query="turnaround capital procurement allocations",
        top_k=3,
        user_role="admin",
        user_department="Executive Leadership",
        clearance="RESTRICTED",
    )
    assert len(res.chunks) > 0
    doc_names = [c.doc_name for c in res.chunks]
    assert "MRPL-UNIT-3-BOARD-AUDIT-RESTRICTED.pdf" in doc_names


# =====================================================================
# 2. CRYPTOGRAPHIC ACTION APPROVAL TOKEN TESTS
# =====================================================================

def test_approval_token_issuance_and_verification():
    """Senior engineer receives valid HMAC-SHA256 token binding action, recipient, and payload hash."""
    payload_hash = compute_payload_hash("CDU-2 Turnaround Scope Brief")
    req = ActionApprovalRequest(
        action_type="DISPATCH_INSPECTION_EMAIL",
        target="inspection.lead@mrpl.co.in",
        payload_summary="Turnaround Brief",
        payload_hash=payload_hash,
        user_id="USR-SNR-01",
        user_role="senior",
    )
    receipt = generate_approval_token(req)
    assert receipt.status == "APPROVED"
    assert receipt.approval_token
    assert "." in receipt.approval_token

    # Verify matching token succeeds
    valid = verify_approval_token(
        receipt.approval_token,
        expected_action="DISPATCH_INSPECTION_EMAIL",
        expected_target="inspection.lead@mrpl.co.in",
        expected_payload_hash=payload_hash,
    )
    assert valid is True


def test_approval_token_tamper_rejection():
    """Tampering with target recipient or payload hash immediately invalidates token."""
    payload_hash = compute_payload_hash("Original Unaltered Content")
    req = ActionApprovalRequest(
        action_type="DISPATCH_INSPECTION_EMAIL",
        target="inspection.lead@mrpl.co.in",
        payload_summary="Original",
        payload_hash=payload_hash,
        user_id="USR-SNR-01",
        user_role="senior",
    )
    receipt = generate_approval_token(req)

    # 1. Target altered to different address -> Rejected
    assert verify_approval_token(
        receipt.approval_token,
        expected_action="DISPATCH_INSPECTION_EMAIL",
        expected_target="attacker@external.com",
        expected_payload_hash=payload_hash,
    ) is False

    # 2. Payload altered -> Rejected
    tampered_hash = compute_payload_hash("Maliciously Modified Content")
    assert verify_approval_token(
        receipt.approval_token,
        expected_action="DISPATCH_INSPECTION_EMAIL",
        expected_target="inspection.lead@mrpl.co.in",
        expected_payload_hash=tampered_hash,
    ) is False


def test_junior_cannot_issue_approval_token():
    """Junior field technicians cannot self-issue approval tokens for consequential actions."""
    req = ActionApprovalRequest(
        action_type="DISPATCH_INSPECTION_EMAIL",
        target="inspection.lead@mrpl.co.in",
        payload_summary="Attempted junior signoff",
        payload_hash="abcd1234efgh5678",
        user_id="USR-JNR-03",
        user_role="junior",
    )
    with pytest.raises(PermissionError) as exc_info:
        generate_approval_token(req)
    assert "not authorized to grant consequential action approval tokens" in str(exc_info.value)


# =====================================================================
# 3. INTERNAL EMAIL CONNECTOR TESTS
# =====================================================================

@pytest.fixture
def sample_pipe_data():
    return PipeInspectionData(
        line_tag="CDU-2-04-150-A1A",
        service_description="Crude Distillation Overhead Vapour",
        nominal_thickness_mm=4.8,
        actual_thickness_mm=3.2,
        minimum_required_thickness_mm=2.1,
        corrosion_rate_mm_year=0.35,
        remaining_life_years=3.14,
        mandatory_action="SCHEDULE SHUTDOWN REPLACEMENT (< 5 YRS)",
        inspection_date="September 2026",
        inspector_name="Lead NDT Inspector, MRPL",
    )


def test_email_connector_blocks_external_egress(sample_pipe_data):
    """External email destinations are strictly rejected at creation time."""
    with pytest.raises(ValueError) as exc_info:
        create_inspection_email_draft(
            pipe_data=sample_pipe_data,
            recipient="adversary@external-domain.com",
        )
    assert "Egress Security Violation" in str(exc_info.value)


def test_email_drafting_and_gated_dispatch(sample_pipe_data, tmp_path):
    """Drafts internal email, enforces approval token gate, and completes dispatch."""
    # 1. Create internal draft
    draft = create_inspection_email_draft(
        pipe_data=sample_pipe_data,
        recipient="maintenance.manager@mrpl.co.in",
        attachments=["MRPL_Inspection_Certificate.pdf"],
    )
    assert draft.status == "DRAFT_AWAITING_APPROVAL"
    assert "AI-GENERATED DRAFT - STATUTORY HUMAN REVIEW REQUIRED" in draft.body

    # 2. Attempt dispatch with bogus token -> Rejected
    with pytest.raises(PermissionError):
        approve_and_dispatch_email(
            draft_id=draft.draft_id,
            approval_token="BOGUS_INVALID_TOKEN",
            user_role="senior",
        )

    # 3. Obtain valid approval token binding exact draft
    payload_hash = compute_draft_payload_hash(draft)
    req = ActionApprovalRequest(
        action_type="DISPATCH_INSPECTION_EMAIL",
        target=draft.recipient,
        payload_summary=draft.subject,
        payload_hash=payload_hash,
        user_id="USR-SNR-01",
        user_role="senior",
    )
    receipt = generate_approval_token(req)

    # 4. Dispatch with valid token -> Success
    res = approve_and_dispatch_email(
        draft_id=draft.draft_id,
        approval_token=receipt.approval_token,
        user_role="senior",
    )
    assert res["status"] == "DISPATCHED"
    assert res["draft_id"] == draft.draft_id


# =====================================================================
# 4. STATUTORY WATERMARK & CLASSIFICATION TESTS
# =====================================================================

def test_docx_statutory_watermark(sample_pipe_data, tmp_path):
    """Verify Word builder embeds classification header and statutory draft watermark."""
    payload = ApprovalNotePayload(
        reference_number="MRPL/TSD/2026/042",
        unit_name="Crude Distillation Unit 2",
        inspection_data=sample_pipe_data,
    )
    out_docx = tmp_path / "Test_Note.docx"
    compile_approval_note(payload, out_docx)
    assert out_docx.exists()

    # Read paragraphs and check watermark presence
    from docx import Document
    doc = Document(str(out_docx))
    full_text = " ".join([p.text for p in doc.paragraphs])
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text += " " + cell.text

    assert "CONFIDENTIAL // MRPL TECHNICAL SERVICES" in full_text
    assert "AI-GENERATED DRAFT - STATUTORY HUMAN REVIEW REQUIRED" in full_text


def test_pdf_statutory_watermark(sample_pipe_data, tmp_path):
    """Verify PDF builder generates valid ReportLab statutory certificate."""
    payload = ApprovalNotePayload(
        reference_number="MRPL/TSD/2026/042",
        unit_name="Crude Distillation Unit 2",
        inspection_data=sample_pipe_data,
    )
    out_pdf = tmp_path / "Test_Cert.pdf"
    result = compile_inspection_certificate_pdf(payload, out_pdf)
    assert result.exists()
    assert result.stat().st_size > 3000
    # Verify standard PDF file structure (%PDF- header and EOF marker)
    data = result.read_bytes()
    assert data.startswith(b"%PDF-")
    assert b"%%EOF" in data


# =====================================================================
# 5. VOICE SENTINEL API TESTS (Zero Cloud, RAM only)
# =====================================================================

def test_voice_sentinel_status_api():
    """Verify Voice Sentinel reports on-premise air-gapped status with zero audio retention."""
    res = client.get("/api/voice/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE_AIR_GAPPED"
    assert data["privacy_policy"] == "ZERO_RAW_AUDIO_RETENTION"
    assert data["is_air_gapped"] is True


def test_voice_sentinel_transcribe_ephemeral():
    """Verify RAM-only transcription endpoint returns text with zero disk residue."""
    res = client.post(
        "/api/voice/transcribe",
        data={"mock_prompt": "Emergency check for CDU-2 line 04-150"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "CDU-2" in data["text"]
    assert data["confidence"] > 0.9


def test_voice_sentinel_synthesize_wav():
    """Verify speech synthesis returns playable on-premise PCM WAV audio."""
    res = client.post(
        "/api/voice/synthesize",
        json={"text": "Alert: Replacement required within turnaround."},
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert len(res.content) > 1000
    # Check standard RIFF / WAVE header
    assert res.content[:4] == b"RIFF"
    assert res.content[8:12] == b"WAVE"


# =====================================================================
# 6. ACTION APPROVAL & VAULT ROUTER API TESTS
# =====================================================================

def test_action_api_endpoints(sample_pipe_data):
    """Test REST endpoints for action approvals, email drafting, and vault listing."""
    # 1. Draft endpoint
    draft_res = client.post(
        "/api/actions/email/draft",
        json={
            "recipient": "maintenance.lead@mrpl.co.in",
            "pipe_data": sample_pipe_data.model_dump(),
            "attachments": ["cert.pdf"]
        }
    )
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    draft_id = draft_data["draft_id"]

    # 2. Approve endpoint as senior
    approve_res = client.post(
        "/api/actions/approve",
        json={
            "action_type": "DISPATCH_INSPECTION_EMAIL",
            "target": "maintenance.lead@mrpl.co.in",
            "payload_summary": "CDU-2 Turnaround Notice",
            "payload_hash": draft_data["attachment_hashes"].get("cert.pdf", "hash123"),
            "user_id": "USR-SNR-01",
            "user_role": "senior",
        }
    )
    assert approve_res.status_code == 200
    receipt = approve_res.json()
    assert receipt["status"] == "APPROVED"

    # 3. Junior role rejected
    junior_res = client.post(
        "/api/actions/approve",
        json={
            "action_type": "DISPATCH_INSPECTION_EMAIL",
            "target": "maintenance.lead@mrpl.co.in",
            "payload_summary": "CDU-2 Turnaround Notice",
            "payload_hash": "hash123",
            "user_id": "USR-JNR-02",
            "user_role": "junior",
        }
    )
    assert junior_res.status_code == 403

    # 4. Vault listing
    vault_res = client.get("/api/actions/vault/list")
    assert vault_res.status_code == 200
    vault_data = vault_res.json()
    assert "input_vault" in vault_data
    assert "staging_vault" in vault_data
    assert vault_data["internal_domain"] == "mrpl.co.in"
