"""
SovereignWorkbench — Omni-Modal Industrial Deliverable Compilers
Generates:
1. Executive Word approval notes (.docx)
2. Financial cost & risk workbooks (.xlsx)
3. Board-level presentation decks (.pptx)
4. Engineering piping spool CAD drawings (.dxf)
5. Visual inspection markup & corrosion heatmaps (.png)
"""

from .docx_builder import compile_approval_note
from .xlsx_builder import compile_cost_matrix
from .pptx_builder import build_executive_presentation_pptx, build_executive_presentation_pptx as compile_executive_presentation
from .cad_builder import build_piping_spool_cad_dxf, build_piping_spool_cad_dxf as compile_piping_spool_cad
from .image_builder import build_inspection_heatmap_image, build_inspection_heatmap_image as compile_inspection_heatmap
from .pdf_builder import compile_inspection_certificate_pdf
from .stl_builder import compile_piping_spool_stl_3d
from .csv_builder import compile_ndt_survey_csv

__all__ = [
    "compile_approval_note",
    "compile_cost_matrix",
    "build_executive_presentation_pptx",
    "compile_executive_presentation",
    "build_piping_spool_cad_dxf",
    "compile_piping_spool_cad",
    "build_inspection_heatmap_image",
    "compile_inspection_heatmap",
    "compile_inspection_certificate_pdf",
    "compile_piping_spool_stl_3d",
    "compile_ndt_survey_csv",
]

