"""
SovereignWorkbench — LLM Serving & Model Infrastructure Package (app/llm/__init__.py)
Owned by Kaushal (Dev 3: GPU Workstation Server & Model Serving Lead).
"""

from .client import call_llm, unload_model, is_ollama_available
from .manager import model_manager, ModelManager
from .prompts import (
    ROUTER_SYSTEM_PROMPT,
    VISION_EXTRACTION_SYSTEM_PROMPT,
    MATH_GENERATION_SYSTEM_PROMPT,
    SELF_HEALING_SYSTEM_PROMPT,
)

__all__ = [
    "call_llm",
    "unload_model",
    "is_ollama_available",
    "model_manager",
    "ModelManager",
    "ROUTER_SYSTEM_PROMPT",
    "VISION_EXTRACTION_SYSTEM_PROMPT",
    "MATH_GENERATION_SYSTEM_PROMPT",
    "SELF_HEALING_SYSTEM_PROMPT",
]
