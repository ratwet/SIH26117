"""
SovereignWorkbench — Sovereign RAG Engine
Local, air-gapped CPU-based retrieval-augmented generation for refinery SOPs and standards.
"""

from .ingest import ingest_document_to_rag
from .retriever import query_sovereign_rag

__all__ = ["ingest_document_to_rag", "query_sovereign_rag"]
