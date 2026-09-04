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
)
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


def test_cad_dxf_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_spool.dxf"
    result = compile_piping_spool_cad(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 5000  # Valid DXF R2010 structure with ASME entities


def test_image_heatmap_compiler(tmp_path, sample_payload):
    out = tmp_path / "test_heatmap.png"
    result = compile_inspection_heatmap(sample_payload, out)
    assert result.exists()
    assert result.stat().st_size > 5000  # 1600x900 high-res P&ID heatmap image


def test_admin_model_tiers_api():
    client = TestClient(app)
    # Test GET /api/admin/model-tiers
    resp = client.get("/api/admin/model-tiers")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_tier" in data
    assert "supported_tiers" in data
    assert "ENTERPRISE_100B" in data["supported_tiers"]
    assert "WORKSTATION_32B" in data["supported_tiers"]
    assert "EDGE_LAPTOP_8B" in data["supported_tiers"]

    # Test POST /api/admin/model-tier
    post_resp = client.post("/api/admin/model-tier", json={"tier": "WORKSTATION_32B"})
    assert post_resp.status_code == 200
    assert post_resp.json()["active_tier"] == "WORKSTATION_32B"

    # Reset back to ENTERPRISE_100B
    reset_resp = client.post("/api/admin/model-tier", json={"tier": "ENTERPRISE_100B"})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["active_tier"] == "ENTERPRISE_100B"


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
        "cad_path": None,
        "image_path": None,
        "script_path": None,
        "manifest_path": None,
        "deliverables": None,
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    final_state = await sovereign_graph.ainvoke(initial_state)

    # Verify all 7 deliverables are present in state
    assert final_state.get("docx_path") is not None
    assert final_state.get("xlsx_path") is not None
    assert final_state.get("pptx_path") is not None
    assert final_state.get("cad_path") is not None
    assert final_state.get("image_path") is not None
    assert final_state.get("script_path") is not None
    assert final_state.get("manifest_path") is not None

    # Verify files physically exist on disk
    assert Path(final_state["docx_path"]).exists()
    assert Path(final_state["xlsx_path"]).exists()
    assert Path(final_state["pptx_path"]).exists()
    assert Path(final_state["cad_path"]).exists()
    assert Path(final_state["image_path"]).exists()
    assert Path(final_state["script_path"]).exists()
    assert Path(final_state["manifest_path"]).exists()

    # Verify deliverables list has all 7 items
    deliverables = final_state.get("deliverables", [])
    assert len(deliverables) == 7
    types = {d["type"] for d in deliverables}
    assert types == {"docx", "xlsx", "pptx", "dxf", "png", "py", "json"}
