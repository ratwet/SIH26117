"""
SovereignWorkbench — Agentic Chat & Real-Time SSE Streaming Endpoint (app/api/chat.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).

Handles incoming user requests, manages conversation sessions, and streams
real-time thought logs and deliverables directly to the desktop UI via Server-Sent Events.
"""

import json
import uuid
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.graph.builder import sovereign_graph
from app.graph.state import AgentState
from app.config import settings

router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    """JSON payload for standard non-streaming or script invocation."""
    prompt: str = Field(..., json_schema_extra={"example": "Audit line CDU-2-04-150-A1A from P&ID drawing"})
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_role: str = Field(default="senior", json_schema_extra={"example": "senior"})
    uploaded_files: Optional[List[str]] = Field(default_factory=list)


@router.post("/chat/sync")
async def chat_sync(request: ChatRequest):
    """
    Synchronous / standard JSON endpoint.
    Executes the full LangGraph workflow and returns the final state in a single response.
    """
    tier = getattr(settings, "MODEL_TIER", "ENTERPRISE_100B")
    initial_state: AgentState = {
        "session_id": request.session_id,
        "user_prompt": request.prompt,
        "uploaded_files": request.uploaded_files or [],
        "user_role": request.user_role,
        "task_type": None,
        "active_model": None,
        "model_tier": tier,
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

    return {
        "session_id": final_state["session_id"],
        "task_type": final_state.get("task_type"),
        "active_model": final_state.get("active_model"),
        "model_tier": final_state.get("model_tier"),
        "thought_stream": final_state.get("thought_stream", []),
        "final_response": final_state.get("final_response"),
        "docx_path": final_state.get("docx_path"),
        "xlsx_path": final_state.get("xlsx_path"),
        "pptx_path": final_state.get("pptx_path"),
        "cad_path": final_state.get("cad_path"),
        "image_path": final_state.get("image_path"),
        "script_path": final_state.get("script_path"),
        "manifest_path": final_state.get("manifest_path"),
        "deliverables": final_state.get("deliverables", []),
        "calc_result": final_state.get("calc_result"),
        "retry_count": final_state.get("retry_count", 0),
        "error_message": final_state.get("error_message"),
    }


@router.post("/chat")
async def chat_stream(
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    user_role: Optional[str] = Form("senior"),
    files: Optional[List[UploadFile]] = File(None),
):
    """
    Flagship Streaming Endpoint:
    Accepts multipart-form data with prompt and optional uploaded files.
    Pipes LangGraph state machine node updates directly into an SSE text/event-stream.
    """
    active_session_id = session_id or str(uuid.uuid4())[:8]

    # Save any uploaded files to data/uploads
    saved_file_paths = []
    if files:
        uploads_dir = settings.DATA_DIR / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            dest = uploads_dir / f.filename
            content = await f.read()
            dest.write_bytes(content)
            saved_file_paths.append(str(dest))

    tier = getattr(settings, "MODEL_TIER", "ENTERPRISE_100B")
    initial_state: AgentState = {
        "session_id": active_session_id,
        "user_prompt": prompt,
        "uploaded_files": saved_file_paths,
        "user_role": user_role,
        "task_type": None,
        "active_model": None,
        "model_tier": tier,
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

    async def event_generator():
        # Yield initial connection event
        yield f"event: connected\ndata: {json.dumps({'session_id': active_session_id, 'status': 'PROCESSING', 'model_tier': tier})}\n\n"

        previous_thoughts_count = 0
        final_state = None

        # Stream LangGraph execution node by node
        async for output in sovereign_graph.astream(initial_state):
            for node_name, node_state_update in output.items():
                # Extract new thought stream entries
                new_thoughts = node_state_update.get("thought_stream", [])
                if len(new_thoughts) > previous_thoughts_count:
                    for thought in new_thoughts[previous_thoughts_count:]:
                        event_payload = {
                            "node": node_name,
                            "thought": thought,
                            "session_id": active_session_id,
                        }
                        yield f"event: thought\ndata: {json.dumps(event_payload)}\n\n"
                    previous_thoughts_count = len(new_thoughts)

                # Check if deliverables were generated
                if "docx_path" in node_state_update:
                    deliverable_payload = {
                        "docx_path": node_state_update.get("docx_path"),
                        "xlsx_path": node_state_update.get("xlsx_path"),
                        "pptx_path": node_state_update.get("pptx_path"),
                        "cad_path": node_state_update.get("cad_path"),
                        "image_path": node_state_update.get("image_path"),
                        "script_path": node_state_update.get("script_path"),
                        "manifest_path": node_state_update.get("manifest_path"),
                        "deliverables": node_state_update.get("deliverables", []),
                    }
                    yield f"event: deliverable\ndata: {json.dumps(deliverable_payload)}\n\n"

                final_state = node_state_update

        # Yield completion event with final markdown response
        completion_payload = {
            "session_id": active_session_id,
            "final_response": final_state.get("final_response") if final_state else "Completed.",
            "docx_path": final_state.get("docx_path") if final_state else None,
            "xlsx_path": final_state.get("xlsx_path") if final_state else None,
            "pptx_path": final_state.get("pptx_path") if final_state else None,
            "cad_path": final_state.get("cad_path") if final_state else None,
            "image_path": final_state.get("image_path") if final_state else None,
            "script_path": final_state.get("script_path") if final_state else None,
            "manifest_path": final_state.get("manifest_path") if final_state else None,
            "deliverables": final_state.get("deliverables") if final_state else None,
            "model_tier": tier,
            "status": "COMPLETED",
        }
        yield f"event: done\ndata: {json.dumps(completion_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
