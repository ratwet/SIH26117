"""
SovereignWorkbench — LangGraph Conditional Routing & Edges (app/graph/edges.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).

This file defines the conditional routing logic that steers the agent through the
execution pipeline, including the cyclic self-healing recovery edge.
"""

from typing import Dict, Any, Literal
from app.graph.state import AgentState
from app.config import settings


def route_intent(state: AgentState) -> Literal["vision_extraction", "rag_retrieval", "general_chat"]:
    """
    Conditional Edge 1: Routes from initial intent classification to the appropriate branch.
    """
    task_type = state.get("task_type", "GENERAL_QUERY")

    if task_type == "VISION_AUDIT":
        return "vision_extraction"
    elif task_type == "SOP_LOOKUP":
        return "rag_retrieval"
    else:
        return "general_chat"


def should_retry_or_complete(
    state: AgentState
) -> Literal["compile_deliverables", "distill_error", "escalate_human"]:
    """
    Conditional Edge 2: The Core Self-Healing Decision Gateway.

    Inspects sandbox exit status:
    - If Success (exit code 0) -> proceed to compile Word & Excel deliverables.
    - If Error & retries < 3  -> route to distill_error, which cycles back to math_generation.
    - If Error & retries >= 3 -> trigger Human-In-The-Loop escalation.
    """
    sandbox_result = state.get("sandbox_result")
    retry_count = state.get("retry_count", 0)

    if not sandbox_result:
        return "escalate_human"

    if sandbox_result.success:
        return "compile_deliverables"

    # Self-healing retry threshold check
    max_retries = settings.SANDBOX_MAX_RETRIES  # Default 3
    if retry_count < max_retries:
        return "distill_error"
    else:
        return "escalate_human"


async def escalate_human_node(state: AgentState) -> Dict[str, Any]:
    """
    Terminal Node for Safety Circuit Breaker:
    Triggered when the self-healing loop exhausts all 3 automatic attempts.
    Halts execution and alerts the Senior Plant Engineer for manual verification.
    """
    current_thoughts = state.get("thought_stream", [])
    retry_count = state.get("retry_count", 0)
    sandbox_res = state.get("sandbox_result")

    error_detail = sandbox_res.distilled_error if sandbox_res else "Unresolved calculation failure"
    thought = f"🚨 Circuit Breaker: Self-healing exhausted {retry_count} attempts. Escalating to Senior Inspection Engineer."

    escalation_msg = f"""### ⚠️ Manual Engineering Review Required (Circuit Breaker Tripped)

The SovereignWorkbench autonomous calculation engine encountered persistent sandbox execution issues after **{retry_count} self-healing attempts**.

**Last Error Captured:**
```
{error_detail}
```

**Recommended Action:**
1. Manually verify the P&ID drawing nominal thickness and line tag parameters.
2. Check ASME B31.3 allowable stress values for material `{state.get('extracted_specs', {}).get('material_spec', 'Unknown')}`.
3. Review audit log transaction ID `{state.get('session_id')}`.
"""

    return {
        "error_message": error_detail,
        "final_response": escalation_msg,
        "thought_stream": current_thoughts + [thought],
    }
