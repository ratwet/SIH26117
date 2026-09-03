"""
SovereignWorkbench — Dev 1 LangGraph Unit Verification Suite (backend/tests/test_dev1_graph.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).

Validates:
1. End-to-end P&ID visual audit flow (Route -> Vision -> Math -> Sandbox -> Deliverables)
2. Cyclic self-healing error recovery loop (Sandbox Error -> Distill -> Math Re-prompt -> Success)
3. SOP grounding RAG flow
4. General chat query flow
"""

import pytest
import asyncio
from app.graph.builder import sovereign_graph
from app.graph.state import AgentState


@pytest.mark.asyncio
async def test_full_vision_audit_flow():
    """Verifies standard successful P&ID audit pipeline."""
    initial_state: AgentState = {
        "session_id": "test_session_001",
        "user_prompt": "Audit line CDU-2-04-150-A1A from P&ID drawing",
        "uploaded_files": ["sample_cdu2_drawing.png"],
        "user_role": "senior",
        "task_type": None,
        "active_model": None,
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
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    # Run LangGraph workflow asynchronously
    final_state = await sovereign_graph.ainvoke(initial_state)

    # Assertions
    assert final_state["task_type"] == "VISION_AUDIT"
    assert final_state["extracted_specs"] is not None
    assert final_state["extracted_specs"]["line_tag"] == "CDU-2-04-150-A1A"
    assert final_state["sandbox_result"].success is True
    assert final_state["calc_result"]["remaining_life_years"] == 3.14
    assert final_state["docx_path"] is not None
    assert final_state["xlsx_path"] is not None
    assert "MANDATORY SHUTDOWN REPLACEMENT" in final_state["final_response"]
    assert len(final_state["thought_stream"]) >= 5


@pytest.mark.asyncio
async def test_self_healing_error_recovery():
    """
    Verifies that when a sandbox error occurs, the conditional edge routes to
    distill_error, increments retry_count, and cycles back to recover.
    """
    initial_state: AgentState = {
        "session_id": "test_self_heal_002",
        "user_prompt": "Audit line CDU-2-04-150-A1A [SIMULATE_ERROR]",
        "uploaded_files": ["drawing.png"],
        "user_role": "senior",
        "task_type": None,
        "active_model": None,
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
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    final_state = await sovereign_graph.ainvoke(initial_state)

    # In our mock, SIMULATE_ERROR fails on attempt 0, but recovers on attempt 1
    assert final_state["retry_count"] >= 1
    assert final_state["docx_path"] is not None
    # Verify thought stream contains the self-healing log
    has_self_healing_log = any("Self-Healing" in t or "Error Distiller" in t for t in final_state["thought_stream"])
    assert has_self_healing_log is True


@pytest.mark.asyncio
async def test_sop_lookup_flow():
    """Verifies that queries referencing SOP/OISD standards route to RAG branch."""
    initial_state: AgentState = {
        "session_id": "test_sop_003",
        "user_prompt": "What are the statutory OISD inspection rules for crude distillation lines?",
        "uploaded_files": [],
        "user_role": "junior",
        "task_type": None,
        "active_model": None,
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
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    final_state = await sovereign_graph.ainvoke(initial_state)

    assert final_state["task_type"] == "SOP_LOOKUP"
    assert final_state["rag_chunks"] is not None
    assert len(final_state["rag_chunks"]) >= 1


@pytest.mark.asyncio
async def test_general_chat_flow():
    """Verifies generic non-engineering queries route to general_chat branch."""
    initial_state: AgentState = {
        "session_id": "test_general_004",
        "user_prompt": "Hello, how does SovereignWorkbench work?",
        "uploaded_files": [],
        "user_role": "junior",
        "task_type": None,
        "active_model": None,
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
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    final_state = await sovereign_graph.ainvoke(initial_state)

    assert final_state["task_type"] == "GENERAL_QUERY"
    assert "SovereignWorkbench Assistant" in final_state["final_response"]
