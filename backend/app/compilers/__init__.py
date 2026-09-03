"""
SovereignWorkbench — Office Deliverable Compilers
Generates executive Word approval notes (.docx) and financial cost matrices (.xlsx).
"""

from .docx_builder import compile_approval_note
from .xlsx_builder import compile_cost_matrix

__all__ = ["compile_approval_note", "compile_cost_matrix"]
