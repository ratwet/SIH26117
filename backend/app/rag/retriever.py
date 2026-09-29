"""
SovereignWorkbench - Sovereign RAG Retriever (app/rag/retriever.py)
Queries the local CPU-embedded vector database for refinery engineering standards,
OISD procedures, and API specifications.
"""

import math
import re
import sqlite3
from typing import List, Dict, Any, Optional

from app.config import settings
from app.schemas import RagChunk, RagQueryResponse
from app.rag.ingest import FALLBACK_DB_PATH, _init_fallback_db


CLEARANCE_RANK = {
    "UNCLASSIFIED": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}

# Built-in Baseline Industrial Standards Knowledge Base with Statutory ABAC Metadata
BASELINE_KNOWLEDGE = [
    {
        "doc_name": "API-570-Piping-Inspection.pdf",
        "clause_reference": "Section 7.1: Corrosion Rate and Remaining Life Assessment",
        "classification": "CONFIDENTIAL",
        "department": "Reliability",
        "authorized_roles": ["senior", "admin"],
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
        "classification": "INTERNAL",
        "department": "Inspection",
        "authorized_roles": ["senior", "admin", "junior"],
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
        "classification": "INTERNAL",
        "department": "Engineering",
        "authorized_roles": ["senior", "admin", "junior"],
        "text_content": (
            "Under ASME B31.3 Clause 304.1.2, the minimum design wall thickness t_min for internal design "
            "gage pressure is given by: t_min = (P * D) / (2 * (S * E + P * Y)), where P is internal design "
            "pressure (psi or bar), D is outside pipe diameter (mm), S is allowable stress value for the "
            "material spec (e.g. ASTM A106 Grade B), E is quality factor, and Y is coefficient from Table 304.1.1."
        )
    },
    {
        "doc_name": "MRPL-UNIT-3-BOARD-AUDIT-RESTRICTED.pdf",
        "clause_reference": "Clause 9.4: Turnaround Capital Procurement & Strategic Allocations",
        "classification": "RESTRICTED",
        "department": "Executive Leadership",
        "authorized_roles": ["admin", "senior"],
        "text_content": (
            "CONFIDENTIAL STATUTORY PSU DIRECTIVE: Strategic capital expenditure allocations and vendor bid "
            "reserves for MRPL Phase III CDU and Hydrocracker turnaround replacements are classified RESTRICTED. "
            "Access is limited strictly to Senior Inspection Leads and Level-1 Systems Administrators."
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


def _is_authorized(
    chunk_classification: str,
    chunk_roles: List[str],
    user_role: str,
    clearance: str,
) -> bool:
    """Pre-retrieval ABAC filter checking classification rank and authorized roles."""
    user_rank = CLEARANCE_RANK.get((clearance or "CONFIDENTIAL").upper(), 2)
    doc_rank = CLEARANCE_RANK.get((chunk_classification or "INTERNAL").upper(), 2)
    if doc_rank > user_rank:
        return False
    if chunk_roles:
        norm_roles = [r.lower() for r in chunk_roles]
        if user_role.lower() not in norm_roles and "all" not in norm_roles and user_role.lower() != "admin":
            return False
    return True


def query_sovereign_rag(
    query: str,
    top_k: int = 5,
    user_role: str = "senior",
    user_department: Optional[str] = "Reliability",
    clearance: str = "CONFIDENTIAL",
) -> RagQueryResponse:
    """
    Query the local Sovereign RAG vector store with pre-retrieval ABAC enforcement.
    
    Args:
        query: Engineering or statutory compliance question.
        top_k: Maximum number of relevant chunks to retrieve.
        user_role: Caller role (e.g. 'senior', 'junior', 'admin').
        user_department: Departmental affiliation (e.g. 'Reliability', 'Inspection').
        clearance: Highest clearance level possessed (UNCLASSIFIED, INTERNAL, CONFIDENTIAL, RESTRICTED).
        
    Returns:
        RagQueryResponse: Formatted response with chunks and concatenated context.
    """
    candidate_chunks: List[RagChunk] = []

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
                    n_results=min(top_k * 3, collection.count())
                )
            else:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(top_k * 3, collection.count())
                )
                
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
                distances = results["distances"][0] if "distances" in results and results["distances"] else []
                
                for idx, doc_text in enumerate(docs):
                    meta = metas[idx] if idx < len(metas) else {}
                    doc_classification = meta.get("classification", "INTERNAL")
                    doc_dept = meta.get("department", "Reliability")
                    raw_roles = meta.get("authorized_roles", ["senior", "admin", "junior"])
                    if isinstance(raw_roles, str):
                        doc_roles = [r.strip() for r in raw_roles.split(",")]
                    else:
                        doc_roles = list(raw_roles)
                        
                    if not _is_authorized(doc_classification, doc_roles, user_role, clearance):
                        continue
                        
                    dist = distances[idx] if idx < len(distances) else 0.5
                    score = round(max(0.1, 1.0 - (dist / 2.0)), 2)
                    
                    candidate_chunks.append(RagChunk(
                        doc_name=meta.get("source_doc", "MRPL_Document.pdf"),
                        clause_reference=meta.get("clause", "Section General"),
                        text_content=doc_text,
                        relevance_score=score,
                        classification=doc_classification,
                        department=doc_dept,
                        authorized_roles=doc_roles,
                    ))
    except Exception:
        pass
        
    # 2. Check fallback SQLite database if available
    if FALLBACK_DB_PATH.exists():
        _init_fallback_db()
        try:
            with sqlite3.connect(str(FALLBACK_DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT doc_name, clause_reference, text_content FROM document_chunks")
                rows = cursor.fetchall()
                
                for doc_name, clause, content in rows:
                    if not _is_authorized("INTERNAL", ["senior", "admin", "junior"], user_role, clearance):
                        continue
                    score = _compute_relevance(query, content)
                    candidate_chunks.append(RagChunk(
                        doc_name=doc_name,
                        clause_reference=clause,
                        text_content=content,
                        relevance_score=score,
                        classification="INTERNAL",
                        department=user_department or "Reliability",
                        authorized_roles=["senior", "admin", "junior"],
                    ))
        except Exception:
            pass
            
    # 3. Always include curated baseline standards filtered by ABAC
    for item in BASELINE_KNOWLEDGE:
        if not _is_authorized(
            item.get("classification", "INTERNAL"),
            item.get("authorized_roles", ["senior", "admin", "junior"]),
            user_role,
            clearance,
        ):
            continue
        # Avoid duplicate documents if already retrieved from Chroma
        if any(c.doc_name == item["doc_name"] for c in candidate_chunks):
            continue
        score = _compute_relevance(query, item["text_content"])
        candidate_chunks.append(RagChunk(
            doc_name=item["doc_name"],
            clause_reference=item["clause_reference"],
            text_content=item["text_content"],
            relevance_score=score,
            classification=item.get("classification", "INTERNAL"),
            department=item.get("department", "Reliability"),
            authorized_roles=item.get("authorized_roles", ["senior", "admin", "junior"]),
        ))
            
    # 4. Sort all candidate chunks by relevance score descending and take top_k
    candidate_chunks.sort(key=lambda c: c.relevance_score, reverse=True)
    chunks = candidate_chunks[:top_k]

    # 5. Assemble combined context
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"--- [DOCUMENT: {chunk.doc_name} | {chunk.clause_reference} | Classification: {chunk.classification} | Score: {chunk.relevance_score}] ---\n"
            f"{chunk.text_content}"
        )
    combined_context = "\n\n".join(context_parts)
    
    return RagQueryResponse(
        query=query,
        chunks=chunks,
        combined_context=combined_context
    )
