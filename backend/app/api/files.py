"""
SovereignWorkbench — Files & Deliverables API (app/api/files.py)
Handles file uploads (inspection PDFs, P&ID blueprints) and deliverable downloads
(.docx approval notes, .xlsx cost matrices).
"""

import shutil
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.rag.ingest import ingest_document_to_rag

router = APIRouter(prefix="/api/files", tags=["Files & Deliverables"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload any industrial artifact (P&ID drawings, UTG reports, CAD DWG/DXF, 3D models, CCTV videos).
    Automatically categorizes artifacts and indexes textual/tabular documents into Sovereign RAG.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
        
    safe_filename = Path(file.filename).name
    uploads_dir = getattr(settings, "UPLOADS_DIR", settings.DATA_DIR / "uploads")
    destination = uploads_dir / safe_filename
    
    # Save uploaded file to disk
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = destination.stat().st_size
    chunks_ingested = 0
    suffix = destination.suffix.lower()

    # Determine artifact category
    if suffix in [".pdf", ".docx", ".txt", ".md"]:
        category = "DOCUMENT_SPEC"
        try:
            chunks_ingested = ingest_document_to_rag(destination)
        except Exception:
            pass
    elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".svg"]:
        category = "VISION_BLUEPRINT"
    elif suffix in [".dxf", ".dwg"]:
        category = "CAD_DRAWING"
    elif suffix in [".blend", ".step", ".stp", ".iges", ".igs", ".stl", ".obj"]:
        category = "3D_MODEL"
    elif suffix in [".mp4", ".avi", ".mov", ".mkv"]:
        category = "INSPECTION_VIDEO"
    elif suffix in [".xlsx", ".xls", ".csv"]:
        category = "DATA_WORKBOOK"
    else:
        category = "GENERAL_ARTIFACT"
            
    return {
        "status": "success",
        "filename": safe_filename,
        "category": category,
        "size_bytes": file_size,
        "chunks_indexed": chunks_ingested,
        "file_path": str(destination)
    }


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a compiled deliverable (.docx, .xlsx, .pptx, .dxf, .png) or uploaded document.
    """
    safe_name = Path(filename).name
    deliverables_dir = getattr(settings, "DELIVERABLES_DIR", settings.DATA_DIR / "deliverables")
    uploads_dir = getattr(settings, "UPLOADS_DIR", settings.DATA_DIR / "uploads")
    target_path = deliverables_dir / safe_name
    
    if not target_path.exists():
        # Fallback to uploads dir if user requests uploaded document
        fallback_path = uploads_dir / safe_name
        if fallback_path.exists():
            target_path = fallback_path
        else:
            raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found")
            
    # Determine appropriate MIME media type
    media_type = "application/octet-stream"
    if safe_name.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif safe_name.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif safe_name.endswith(".pptx"):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif safe_name.endswith(".dxf"):
        media_type = "application/dxf"
    elif safe_name.endswith(".png"):
        media_type = "image/png"
    elif safe_name.endswith(".jpg") or safe_name.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif safe_name.endswith(".pdf"):
        media_type = "application/pdf"
    elif safe_name.endswith(".py"):
        media_type = "text/x-python"
    elif safe_name.endswith(".json"):
        media_type = "application/json"
        
    return FileResponse(
        path=target_path,
        filename=safe_name,
        media_type=media_type
    )


@router.get("/list")
async def list_files() -> Dict[str, List[Dict[str, Any]]]:
    """List all available deliverables and uploaded files."""
    deliverables_dir = getattr(settings, "DELIVERABLES_DIR", settings.DATA_DIR / "deliverables")
    uploads_dir = getattr(settings, "UPLOADS_DIR", settings.DATA_DIR / "uploads")
    
    deliverables = []
    for p in deliverables_dir.glob("*"):
        if p.is_file() and not p.name.startswith("."):
            deliverables.append({
                "name": p.name,
                "size_bytes": p.stat().st_size,
                "created_at": p.stat().st_ctime
            })
            
    uploads = []
    for p in uploads_dir.glob("*"):
        if p.is_file() and not p.name.startswith("."):
            uploads.append({
                "name": p.name,
                "size_bytes": p.stat().st_size,
                "created_at": p.stat().st_ctime
            })
            
    return {
        "deliverables": deliverables,
        "uploads": uploads
    }
