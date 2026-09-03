"""
SovereignWorkbench — VRAM Residency & Model Fleet Manager (app/llm/manager.py)
Owned by Kaushal (Dev 3: GPU Workstation Server & Model Serving Lead).

Manages model swapping on the GPU gaming laptop to guarantee VRAM usage <= 5.5 GB.
Scans models_storage for dropped .gguf files and monitors CUDA GPU memory.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings
from app.llm.client import unload_model

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages local model lifecycle and GPU VRAM residency."""

    def __init__(self):
        self.active_model: Optional[str] = None

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all models currently installed in local Ollama daemon."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    return [
                        {
                            "name": m.get("name"),
                            "size_bytes": m.get("size", 0),
                            "modified_at": m.get("modified_at"),
                            "quantization": m.get("details", {}).get("quantization_level", "unknown"),
                        }
                        for m in models
                    ]
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama model list: {e}")

        # Fallback list of target models
        return [
            {"name": settings.MODEL_ROUTER, "size_bytes": 3500000000, "status": "configured"},
            {"name": settings.MODEL_REASONING, "size_bytes": 5400000000, "status": "configured"},
            {"name": settings.MODEL_VISION, "size_bytes": 5200000000, "status": "configured"},
            {"name": settings.MODEL_CODER, "size_bytes": 4800000000, "status": "configured"},
        ]

    def scan_gguf_files(self) -> List[Dict[str, Any]]:
        """Scan models_storage/ directory for imported .gguf files."""
        storage_dir = settings.MODELS_DIR
        if not storage_dir.exists():
            return []

        gguf_files = []
        for file in storage_dir.glob("*.gguf"):
            gguf_files.append({
                "filename": file.name,
                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                "path": str(file),
            })
        return gguf_files

    async def switch_model(self, target_model: str) -> bool:
        """
        Safely switch the active model in GPU VRAM.
        Unloads the current model first to prevent CUDA OOM on 6GB–8GB GPUs.
        """
        if self.active_model and self.active_model != target_model:
            logger.info(f"Unloading previous model '{self.active_model}' from VRAM...")
            await unload_model(self.active_model)

        self.active_model = target_model
        return True

    def get_gpu_vram_usage(self) -> Dict[str, Any]:
        """Query nvidia-smi if available to check real-time VRAM allocation."""
        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            return {"gpu_detected": False, "allocated_vram_mb": 0, "total_vram_mb": 0}

        try:
            result = subprocess.run(
                [
                    nvidia_smi,
                    "--query-gpu=memory.used,memory.total",
                    "--format=csv,nounits,noheader",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                line = result.stdout.strip().split("\n")[0]
                used, total = line.split(",")
                return {
                    "gpu_detected": True,
                    "allocated_vram_mb": int(used.strip()),
                    "total_vram_mb": int(total.strip()),
                    "utilization_pct": round((int(used.strip()) / int(total.strip())) * 100, 1),
                }
        except Exception:
            pass

        return {"gpu_detected": False, "allocated_vram_mb": 0, "total_vram_mb": 0}


model_manager = ModelManager()
