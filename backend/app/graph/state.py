"""
SovereignWorkbench — AgentState Definition.
Owned by Rajat (Dev 1: Orchestration & API Lead).

This TypedDict represents the state passed between all nodes in the LangGraph workflow.
Every node receives this state and returns a dictionary with updated fields.
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from app.schemas import SandboxResult, PipeInspectionData, RagChunk


class AgentState(TypedDict):
    """
    Central state dictionary for SovereignWorkbench LangGraph execution.
    Every node in the graph receives this state and returns a dictionary
    updating one or more fields.
    """

    # --- 1. User & Session Metadata ---
    session_id: str
    user_prompt: str
    uploaded_files: List[str]                  # Local file paths of uploaded PDFs or drawings
    user_role: Literal["admin", "senior", "junior"]

    # --- 2. Intent Routing & Model Architecture ---
    task_type: Optional[str]                   # "VISION_AUDIT", "SOP_LOOKUP", "GENERAL_QUERY"
    active_model: Optional[str]                # Model tag used for current operation
    model_tier: Optional[str]                  # "ENTERPRISE_100B", "WORKSTATION_32B", "EDGE_LAPTOP_8B"

    # --- 3. Multimodal & Vision Extraction ---
    extracted_specs: Optional[Dict[str, Any]]  # Extracted values (line_tag, t_nominal, t_actual, etc.)
    pipe_data: Optional[PipeInspectionData]    # Validated Pydantic inspection object

    # --- 4. RAG Retrieval ---
    rag_chunks: Optional[List[RagChunk]]       # Retrieved clauses from OISD / API standards
    rag_context: Optional[str]                 # Formatted retrieved text for prompt injection

    # --- 5. Code Generation & Sandbox Math Execution ---
    generated_code: Optional[str]              # Self-contained Python calculation script
    sandbox_result: Optional[SandboxResult]    # Execution output (exit code, stdout, stderr, etc.)
    retry_count: int                           # Number of self-healing attempts (0..3)
    calc_result: Optional[Dict[str, Any]]      # Parsed JSON metrics from sandbox execution

    # --- 6. Compiled Deliverables (Omni-Modal) ---
    docx_path: Optional[str]                   # Path to generated MRPL_Approval_Note.docx
    xlsx_path: Optional[str]                   # Path to generated Cost_Matrix.xlsx
    pptx_path: Optional[str]                   # Path to generated Executive_Pitch_Deck.pptx
    pdf_path: Optional[str]                    # Path to generated MRPL_Inspection_Certificate.pdf
    cad_path: Optional[str]                    # Path to generated Piping_Spool_Drawing.dxf
    stl_path: Optional[str]                    # Path to generated Piping_Spool_3D.stl
    image_path: Optional[str]                  # Path to generated Inspection_Heatmap.png
    csv_path: Optional[str]                    # Path to generated UT_Thickness_Survey.csv
    script_path: Optional[str]                 # Path to generated Standalone_Calculation_Script.py
    manifest_path: Optional[str]               # Path to generated MRPL_Audit_Manifest.json
    deliverables: Optional[List[Dict[str, Any]]] # Array of generated deliverable items

    # --- 7. Real-Time Telemetry & Chat Response ---
    thought_stream: List[str]                  # Real-time event log for UI streaming
    final_response: Optional[str]             # Final markdown answer presented to the user
    error_message: Optional[str]              # Human-readable failure description if fatal
