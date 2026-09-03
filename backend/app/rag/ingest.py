"""
SovereignWorkbench — Sovereign RAG Ingestion (app/rag/ingest.py)
Ingests refinery SOPs, API standards, and inspection dossiers into a local,
air-gapped CPU vector database.
"""

import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.config import settings

logger = logging.getLogger(__name__)

# Fallback SQLite DB path when ChromaDB is not installed
FALLBACK_DB_PATH = settings.CHROMA_PERSIST_DIR / "rag_chunks.sqlite"


def _init_fallback_db():
    """Initialize fallback SQLite database for resilient vector/text search."""
    settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(FALLBACK_DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                doc_name TEXT,
                clause_reference TEXT,
                text_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def _extract_text_from_file(file_path: Path) -> str:
    """Extract raw text from PDF, DOCX, TXT, or MD documents."""
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        text_parts = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(file_path))
            for page in doc:
                text_parts.append(page.get_text())
            return "\n\n".join(text_parts)
        except Exception:
            pass
            
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Failed to read PDF with pypdf: {e}")
            
    elif suffix == ".docx":
        try:
            from docx import Document
            doc = Document(str(file_path))
            return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            logger.error(f"Failed to read DOCX: {e}")
            
    # Default to plain text / markdown
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Failed to read text file: {e}")
        return ""


def _chunk_text(text: str, chunk_size: int = 1500, overlap: int = 150) -> List[Tuple[str, str]]:
    """
    Split text into overlapping chunks with identified clause references.
    Returns list of (clause_ref, chunk_text).
    """
    if not text.strip():
        return []
        
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0
    current_clause = "General Specifications"
    
    clause_regex = re.compile(r"(?:Clause|Section|Article|Standard)\s+([0-9]+(?:\.[0-9]+)*[:\s\w-]*)", re.IGNORECASE)
    
    for p in paragraphs:
        # Check if paragraph introduces a new clause
        match = clause_regex.search(p[:100])
        if match:
            current_clause = match.group(0).strip()
            
        p_len = len(p)
        if current_length + p_len > chunk_size and current_chunk:
            chunk_str = "\n\n".join(current_chunk)
            chunks.append((current_clause, chunk_str))
            
            # Keep tail for overlap
            overlap_content = current_chunk[-1] if len(current_chunk[-1]) <= overlap else current_chunk[-1][-overlap:]
            current_chunk = [overlap_content, p]
            current_length = len(overlap_content) + p_len
        else:
            current_chunk.append(p)
            current_length += p_len
            
    if current_chunk:
        chunk_str = "\n\n".join(current_chunk)
        chunks.append((current_clause, chunk_str))
        
    return chunks


def ingest_document_to_rag(file_path: Path) -> int:
    """
    Chunk and embed a document into the local Sovereign RAG vector store.
    
    Args:
        file_path: Absolute or relative Path to the document.
        
    Returns:
        int: Number of chunks successfully ingested.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document not found at {file_path}")
        
    raw_text = _extract_text_from_file(file_path)
    if not raw_text.strip():
        logger.warning(f"No text extracted from {file_path}")
        return 0
        
    chunks = _chunk_text(raw_text)
    if not chunks:
        return 0
        
    doc_name = file_path.name
    
    # Try using ChromaDB & FastEmbed if available
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
        collection = client.get_or_create_collection(name="mrpl_standards")
        
        # Try FastEmbed
        try:
            from fastembed import TextEmbedding
            embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            texts = [c[1] for c in chunks]
            embeddings = list(embedder.embed(texts))
            embeddings_list = [emb.tolist() for emb in embeddings]
        except Exception:
            embeddings_list = None
            
        ids = [f"{doc_name}_chunk_{idx}" for idx in range(len(chunks))]
        metadatas = [{"source_doc": doc_name, "clause": c[0]} for c in chunks]
        documents = [c[1] for c in chunks]
        
        if embeddings_list is not None:
            collection.upsert(ids=ids, embeddings=embeddings_list, metadatas=metadatas, documents=documents)
        else:
            collection.upsert(ids=ids, metadatas=metadatas, documents=documents)
            
        logger.info(f"Ingested {len(chunks)} chunks into ChromaDB from {doc_name}")
        return len(chunks)
        
    except Exception as e:
        logger.warning(f"ChromaDB ingestion unavailable ({e}), using resilient local fallback index.")
        
    # Resilient Fallback to SQLite store
    _init_fallback_db()
    with sqlite3.connect(str(FALLBACK_DB_PATH)) as conn:
        for idx, (clause, content) in enumerate(chunks):
            chunk_id = f"{doc_name}_chunk_{idx}"
            conn.execute("""
                INSERT OR REPLACE INTO document_chunks (id, doc_name, clause_reference, text_content)
                VALUES (?, ?, ?, ?)
            """, (chunk_id, doc_name, clause, content))
        conn.commit()
        
    logger.info(f"Ingested {len(chunks)} chunks into fallback SQLite RAG store from {doc_name}")
    return len(chunks)
