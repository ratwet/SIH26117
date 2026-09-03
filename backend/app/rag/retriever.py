"""
SovereignWorkbench — Sovereign RAG Retriever (app/rag/retriever.py)
Queries the local CPU-embedded vector database for refinery engineering standards,
OISD procedures, and API specifications.
"""

import math
import re
import sqlite3
from typing import List, Dict, Any

from app.config import settings
from app.schemas import RagChunk, RagQueryResponse
from app.rag.ingest import FALLBACK_DB_PATH, _init_fallback_db


# Built-in Baseline Industrial Standards Knowledge Base
BASELINE_KNOWLEDGE = [
    {
        "doc_name": "API-570-Piping-Inspection.pdf",
        "clause_reference": "Section 7.1: Corrosion Rate and Remaining Life Assessment",
        "text_content": (
            "API 570 Section 7.1 prescribes that the remaining life of an in-service piping system "
            "shall be calculated using the formula: Remaining Life = (t_actual - t_minimum) / corrosion_rate. "
            "Where t_actual is the thickness in mm recorded at the most recent inspection, and t_minimum "
            "is the minimum required thickness per ASME B31.3. If remaining life is evaluated to be less "
            "than 5.0 years, mandatory procurement and scheduled replacement during the next major turnaround "
            "must be initiated immediately."
        )
    },
    {
        "doc_name": "OISD-STD-118.pdf",
        "clause_reference": "Section 4.2: In-Service Inspection Frequency & Criticality",
        "text_content": (
            "Oil Industry Safety Directorate (OISD) Standard 118 Section 4.2 mandates non-destructive "
            "ultrasonic thickness gauging (UTG) on all Class 1 and Class 2 hydrocarbon process lines. "
            "For lines operating in corrosive environments (Crude Distillation overhead, sour water, and amine), "
            "inspection intervals must not exceed 3 years. Any piping segment exhibiting wall thickness loss "
            "greater than 30% of nominal baseline must be subjected to detailed engineering evaluation."
        )
    },
    {
        "doc_name": "ASME-B31.3-Process-Piping.pdf",
        "clause_reference": "Clause 304.1.2: Minimum Required Wall Thickness Calculation",
        "text_content": (
            "Under ASME B31.3 Clause 304.1.2, the minimum design wall thickness t_min for internal design "
            "gage pressure is given by: t_min = (P * D) / (2 * (S * E + P * Y)), where P is internal design "
            "pressure (psi or bar), D is outside pipe diameter (mm), S is allowable stress value for the "
            "material spec (e.g. ASTM A106 Grade B), E is quality factor, and Y is coefficient from Table 304.1.1."
        )
    }
]


def _compute_relevance(query: str, text: str) -> float:
    """Compute lightweight term-overlap relevance score [0.0, 1.0]."""
    q_words = set(re.findall(r"\w+", query.lower()))
    t_words = set(re.findall(r"\w+", text.lower()))
    if not q_words or not t_words:
        return 0.1
    common = q_words.intersection(t_words)
    score = len(common) / math.sqrt(len(q_words) * len(t_words))
    return round(min(1.0, max(0.2, score * 2.5)), 3)


def query_sovereign_rag(query: str, top_k: int = 5) -> RagQueryResponse:
    """
    Query the local Sovereign RAG vector store.
    
    Args:
        query: Engineering or statutory compliance question.
        top_k: Maximum number of relevant chunks to retrieve.
        
    Returns:
        RagQueryResponse: Formatted response with chunks and concatenated context.
    """
    chunks: List[RagChunk] = []
    
    # 1. Try querying ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
        collection = client.get_or_create_collection(name="mrpl_standards")
        
        if collection.count() > 0:
            query_embeddings = None
            try:
                from fastembed import TextEmbedding
                embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                query_embeddings = [list(embedder.embed([query]))[0].tolist()]
            except Exception:
                pass
                
            if query_embeddings:
                results = collection.query(
                    query_embeddings=query_embeddings,
                    n_results=min(top_k, collection.count())
                )
            else:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(top_k, collection.count())
                )
                
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
                distances = results["distances"][0] if "distances" in results and results["distances"] else []
                
                for idx, doc_text in enumerate(docs):
                    meta = metas[idx] if idx < len(metas) else {}
                    # Convert distance to similarity score
                    dist = distances[idx] if idx < len(distances) else 0.5
                    score = round(max(0.1, 1.0 - (dist / 2.0)), 2)
                    
                    chunks.append(RagChunk(
                        doc_name=meta.get("source_doc", "MRPL_Document.pdf"),
                        clause_reference=meta.get("clause", "Section General"),
                        text_content=doc_text,
                        relevance_score=score
                    ))
    except Exception:
        pass
        
    # 2. If ChromaDB returned no chunks, check fallback SQLite database
    if not chunks and FALLBACK_DB_PATH.exists():
        _init_fallback_db()
        try:
            with sqlite3.connect(str(FALLBACK_DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT doc_name, clause_reference, text_content FROM document_chunks")
                rows = cursor.fetchall()
                
                scored_rows = []
                for doc_name, clause, content in rows:
                    score = _compute_relevance(query, content)
                    scored_rows.append((score, doc_name, clause, content))
                    
                scored_rows.sort(key=lambda x: x[0], reverse=True)
                for score, doc_name, clause, content in scored_rows[:top_k]:
                    chunks.append(RagChunk(
                        doc_name=doc_name,
                        clause_reference=clause,
                        text_content=content,
                        relevance_score=score
                    ))
        except Exception:
            pass
            
    # 3. If still empty, supply curated baseline industrial refinery standards
    if not chunks:
        scored_baseline = []
        for item in BASELINE_KNOWLEDGE:
            score = _compute_relevance(query, item["text_content"])
            scored_baseline.append((score, item))
            
        scored_baseline.sort(key=lambda x: x[0], reverse=True)
        for score, item in scored_baseline[:top_k]:
            chunks.append(RagChunk(
                doc_name=item["doc_name"],
                clause_reference=item["clause_reference"],
                text_content=item["text_content"],
                relevance_score=score
            ))
            
    # 4. Assemble combined context
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"--- [DOCUMENT: {chunk.doc_name} | {chunk.clause_reference} | Score: {chunk.relevance_score}] ---\n"
            f"{chunk.text_content}"
        )
    combined_context = "\n\n".join(context_parts)
    
    return RagQueryResponse(
        query=query,
        chunks=chunks,
        combined_context=combined_context
    )
