"""
SovereignWorkbench — Omni-Modal & 100B Model Architecture Test Suite
(backend/tests/test_omni_modal_100b.py)
"""

import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.schemas import PipeInspectionData, ApprovalNotePayload, CostMatrixPayload
from app.compilers import (
    compile_approval_note,
    compile_cost_matrix,
    compile_executive_presentation,
    compile_piping_spool_cad,
    compile_inspection_heatmap,
    compile_inspection_certificate_pdf,
    compile_piping_spool_stl_3d,
    compile_ndt_survey_csv,
)
from app.llm import foundation_engine
from app.graph.builder import sovereign_graph
from app.graph.state import AgentState


@pytest.fixture
def sample_payload():
    pipe_data = PipeInspectionData(
        line_tag="CDU-2-04-150-A1A",
        service_description="Crude Distillation Overhead Vapour",
        material_spec="ASTM A106 Grade B Carbon Steel",
        design_pressure_psi=150.0,
        design_temp_celsius=135.0,
        nominal_thickness_mm=4.8,
        actual_thickness_mm=3.2,
        minimum_required_thickness_mm=2.1,
        corrosion_rate_mm_year=0.35,
        remaining_life_years=3.14,
        mandatory_action="MANDATORY SHUTDOWN REPLACEMENT REQUIRED (< 5 YRS)",
    )
    return ApprovalNotePayload(inspection_data=pipe_data)


def test_docx_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_note.docx"
    result = compile_approval_note(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_xlsx_compiler(tmp_path):
    out = tmp_path / "test_matrix.xlsx"
    cost_payload = CostMatrixPayload(line_tag="CDU-2-04-150-A1A")
    result = compile_cost_matrix(cost_payload, out)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_pptx_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_deck.pptx"
    result = compile_executive_presentation(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 5000  # Multi-slide executive deck


def test_pdf_certificate_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_cert.pdf"
    result = compile_inspection_certificate_pdf(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 2000  # Official ReportLab PDF certificate


def test_cad_dxf_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_spool.dxf"
    result = compile_piping_spool_cad(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 5000  # Valid DXF R2010 structure with ASME entities


def test_stl_3d_mesh_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_spool_3d.stl"
    result = compile_piping_spool_stl_3d(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 10000  # 3D printable ASCII STL facet geometry
    text = result.read_text(encoding="utf-8")
    assert "solid ASME_B31_3_Piping_Spool" in text
    assert "endsolid" in text


def test_image_heatmap_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_heatmap.png"
    result = compile_inspection_heatmap(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 5000  # 1600x900 high-res P&ID heatmap image


def test_csv_ndt_survey_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_survey.csv"
    result = compile_ndt_survey_csv(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 500
    content = result.read_text(encoding="utf-8")
    assert "CML_TAG" in content
    assert "CDU-2-04-150-A1A" in content


@pytest.mark.asyncio
async def test_100b_foundation_model_engine(monkeypatch):
    # 1. Test cluster health reports accurate hardware target and offline status
    telemetry = await foundation_engine.check_cluster_health()
    assert "target_hardware" in telemetry
    assert "tensor_parallel_size" in telemetry
    assert telemetry["tensor_parallel_size"] == 4
    assert telemetry["max_context_window"] == 131072
    assert telemetry["mode"] == "DISCONNECTED"
    assert telemetry["is_connected"] is False

    # 2. Strict Air-Gapped Contract: Refuse to run when no model is connected
    monkeypatch.setattr(settings, "ALLOW_EMULATION", False)
    with pytest.raises(ConnectionError, match="NO LLM MODEL CONNECTED"):
        await foundation_engine.generate_response(
            prompt="Audit CDU-2-04-150-A1A ultrasonic log",
            system_prompt="You are DeepSeek-R1 100B Vision Auditor",
            model_type="vision",
        )

    # 3. Explicit test synthetic fallback when ALLOW_EMULATION is enabled
    monkeypatch.setattr(settings, "ALLOW_EMULATION", True)
    content, thought = await foundation_engine.generate_response(
        prompt="Audit CDU-2-04-150-A1A ultrasonic log",
        system_prompt="You are DeepSeek-R1 100B Vision Auditor",
        model_type="vision",
    )
    assert content is not None
    assert "CDU-2-04-150-A1A" in content
    assert thought is not None
    assert "DeepSeek-R1" in thought


def test_admin_model_tiers_and_health_api():
    client = TestClient(app)
    # Test GET /api/admin/model-tiers
    resp = client.get("/api/admin/model-tiers")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_tier" in data
    assert "supported_tiers" in data
    assert "ENTERPRISE_100B" in data["supported_tiers"]

    # Test GET /api/admin/llm-health
    health_resp = client.get("/api/admin/llm-health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["tensor_parallel_size"] == 4
    assert "target_hardware" in health_data


@pytest.mark.asyncio
async def test_langgraph_full_omni_modal_execution(tmp_path):
    initial_state: AgentState = {
        "session_id": "test-omni-100b",
        "user_prompt": "Audit line CDU-2-04-150-A1A and generate complete engineering deliverables suite.",
        "uploaded_files": [],
        "user_role": "senior",
        "task_type": None,
        "active_model": None,
        "model_tier": None,
        "extracted_specs": None,
        "pipe_data": None,
        "rag_chunks": None,
        "rag_context": None,
        "generated_code": None,
        "sandbox_result": None,
        "retry_count": 0,
        "calc_result": None,
        "docx_path": None,
        "xlsx_path": None,
        "pptx_path": None,
        "pdf_path": None,
        "cad_path": None,
        "stl_path": None,
        "image_path": None,
        "csv_path": None,
        "script_path": None,
        "manifest_path": None,
        "deliverables": None,
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    final_state = await sovereign_graph.ainvoke(initial_state)

    # Verify all 10 deliverables are present in state
    assert final_state.get("docx_path") is not None
    assert final_state.get("xlsx_path") is not None
    assert final_state.get("pptx_path") is not None
    assert final_state.get("pdf_path") is not None
    assert final_state.get("cad_path") is not None
    assert final_state.get("stl_path") is not None
    assert final_state.get("image_path") is not None
    assert final_state.get("csv_path") is not None
    assert final_state.get("script_path") is not None
    assert final_state.get("manifest_path") is not None

    # Verify files physically exist on disk
    assert Path(final_state["docx_path"]).exists()
    assert Path(final_state["xlsx_path"]).exists()
    assert Path(final_state["pptx_path"]).exists()
    assert Path(final_state["pdf_path"]).exists()
    assert Path(final_state["cad_path"]).exists()
    assert Path(final_state["stl_path"]).exists()
    assert Path(final_state["image_path"]).exists()
    assert Path(final_state["csv_path"]).exists()
    assert Path(final_state["script_path"]).exists()
    assert Path(final_state["manifest_path"]).exists()

    # Verify deliverables list has all 10 items
    deliverables = final_state.get("deliverables", [])
    assert len(deliverables) == 10
    types = {d["type"] for d in deliverables}
    assert types == {"docx", "xlsx", "pptx", "pdf", "dxf", "stl", "png", "csv", "py", "json"}


def test_chat_refuses_to_run_without_model(monkeypatch):
    """Verifies that API strictly rejects requests with HTTP 503 when no model is connected."""
    client = TestClient(app)
    monkeypatch.setattr(settings, "ALLOW_EMULATION", False)

    # 1. Sync endpoint returns 503 Service Unavailable
    resp = client.post("/api/chat/sync", json={"prompt": "Audit line CDU-2-04-150-A1A"})
    assert resp.status_code == 503
    assert "NO LLM MODEL CONNECTED" in resp.json()["detail"]

    # 2. SSE streaming endpoint emits event: error with FAILED_NO_MODEL
    stream_resp = client.post("/api/chat", data={"prompt": "Audit line CDU-2-04-150-A1A"})
    assert stream_resp.status_code == 200
    body = stream_resp.text
    assert "event: error" in body
    assert "FAILED_NO_MODEL" in body

