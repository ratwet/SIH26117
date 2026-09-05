"""
SovereignWorkbench — LangGraph StateGraph Assembly & Compilation (app/graph/builder.py)
Owned by Rajat (Dev 1: Orchestration & API Lead).

This file connects all nodes and conditional edges into a compiled, runnable
LangGraph workflow with cyclic self-healing recovery.
"""

from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    route_task_node,
    vision_extraction_node,
    rag_retrieval_node,
    math_generation_node,
    sandbox_execution_node,
    distill_error_node,
    compile_deliverables_node,
    general_chat_node,
)
from app.graph.edges import (
    route_intent,
    should_retry_or_complete,
    escalate_human_node,
)


def build_sovereign_graph():
    """
    Constructs and compiles the complete SovereignWorkbench agentic state machine.

    Topology:
    1. ENTRY -> route_task
    2. route_task -> [vision_extraction | rag_retrieval | general_chat]
    3. vision_extraction -> math_generation
    4. rag_retrieval -> compile_deliverables
    5. math_generation -> sandbox_execution
    6. sandbox_execution -> [compile_deliverables (success) | distill_error (retry<3) | escalate_human (retry>=3)]
    7. distill_error -> math_generation  (THE CYCLIC SELF-HEALING LOOP)
    8. compile_deliverables -> END
    9. general_chat -> END
    10. escalate_human -> END
    """
    workflow = StateGraph(AgentState)

    # 1. Register All Nodes
    workflow.add_node("route_task", route_task_node)
    workflow.add_node("vision_extraction", vision_extraction_node)
    workflow.add_node("rag_retrieval", rag_retrieval_node)
    workflow.add_node("math_generation", math_generation_node)
    workflow.add_node("sandbox_execution", sandbox_execution_node)
    workflow.add_node("distill_error", distill_error_node)
    workflow.add_node("compile_deliverables", compile_deliverables_node)
    workflow.add_node("general_chat", general_chat_node)
    workflow.add_node("escalate_human", escalate_human_node)

    # 2. Set Entry Point
    workflow.set_entry_point("route_task")

    # 3. Add Conditional Routing from Route Task
    workflow.add_conditional_edges(
        "route_task",
        route_intent,
        {
            "vision_extraction": "vision_extraction",
            "rag_retrieval": "rag_retrieval",
            "general_chat": "general_chat",
        },
    )

    # 4. Standard Forward Transitions
    workflow.add_edge("vision_extraction", "math_generation")
    workflow.add_edge("rag_retrieval", "general_chat")
    workflow.add_edge("math_generation", "sandbox_execution")

    # 5. Add Conditional Decision from Sandbox Execution (Self-Healing Loop)
    workflow.add_conditional_edges(
        "sandbox_execution",
        should_retry_or_complete,
        {
            "compile_deliverables": "compile_deliverables",
            "distill_error": "distill_error",
            "escalate_human": "escalate_human",
        },
    )

    # 6. THE CYCLIC RECOVERY EDGE: Error Distiller routes back to Math Generator
    workflow.add_edge("distill_error", "math_generation")

    # 7. Terminal Transitions
    workflow.add_edge("compile_deliverables", END)
    workflow.add_edge("general_chat", END)
    workflow.add_edge("escalate_human", END)

    # Compile into executable runnable
    return workflow.compile()


# Singleton compiled graph instance for application import
sovereign_graph = build_sovereign_graph()
aquanex_graph = sovereign_graph
build_aquanex_graph = build_sovereign_graph
