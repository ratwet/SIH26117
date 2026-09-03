"""
SovereignWorkbench — Unified Async Ollama Model Gateway (app/llm/client.py)
Owned by Kaushal (Dev 3: GPU Workstation Server & Model Serving Lead).

Provides an asynchronous HTTP client connecting to local Ollama (127.0.0.1:11434).
Supports sequential VRAM offloading (keep_alive: 0), image inputs for vision LLMs,
and graceful fallback to simulated responses if Ollama is not yet started.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _encode_image_to_base64(image_path: str) -> Optional[str]:
    """Convert an image file to base64 for Ollama vision API."""
    path = Path(image_path)
    if not path.exists():
        return None
    try:
        data = path.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to encode image {image_path}: {e}")
        return None


async def is_ollama_available() -> bool:
    """Check if the local Ollama daemon is reachable on loopback."""
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


async def unload_model(model_name: str) -> bool:
    """
    Explicitly purge a model from GPU VRAM by sending keep_alive: 0.
    Essential for running on a 6GB–8GB gaming laptop to prevent CUDA OOM.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json={"model": model_name, "keep_alive": 0},
            )
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Could not purge model {model_name} from VRAM: {e}")
        return False


async def call_llm(
    model: str,
    prompt: str,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
    keep_alive: str = "0s",
    temperature: float = 0.2,
) -> str:
    """
    Unified asynchronous LLM inference call.
    
    Args:
        model: Ollama model tag (e.g., deepseek-r1:8b, qwen2-vl:7b, or 100B+ models).
        prompt: User or task prompt.
        system: Optional system instruction prompt.
        images: Optional list of local filepaths for multimodal vision models.
        keep_alive: Ollama VRAM residency flag ("0s" purges model immediately after generation).
        temperature: Sampling temperature (default 0.2 for strict technical derivation).
        
    Returns:
        str: Model response text.
    """
    # 1. Attempt real inference via local Ollama daemon
    try:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": keep_alive,
            "options": {
                "temperature": temperature,
                "num_ctx": 8192,
            },
        }

        if system:
            payload["system"] = system

        if images:
            base64_images = []
            for img in images:
                encoded = _encode_image_to_base64(img)
                if encoded:
                    base64_images.append(encoded)
            if base64_images:
                payload["images"] = base64_images

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.warning(f"Ollama returned status {response.status_code}: {response.text}")

    except httpx.ConnectError:
        logger.info(f"Ollama not running on {settings.OLLAMA_HOST}. Using graceful fallback mock.")
    except Exception as e:
        logger.warning(f"Ollama inference error: {e}. Falling back to simulation.")

    # 2. Graceful Fallback Mock (enables tests & UI development without GPU)
    if "SIMULATE_ERROR" in prompt:
        return """```python
import json
corrosion_rate = 0.0
remaining_life = 1.1 / corrosion_rate
print(json.dumps({"remaining_life": remaining_life}))
```"""

    if "math" in prompt.lower() or "calculation" in prompt.lower() or "cdu" in prompt.lower():
        return """```python
import json

line_tag = "CDU-2-04-150-A1A"
t_nominal = 4.8      # mm
t_actual = 3.2       # mm
t_minimum = 2.1      # mm (calculated per ASME B31.3)
operating_years = 4.57  # years in service

# API 570 Rate Calculation
corrosion_rate = (t_nominal - t_actual) / operating_years  # 0.35 mm/yr
remaining_life = (t_actual - t_minimum) / corrosion_rate    # 3.14 years

action = "SCHEDULE SHUTDOWN REPLACEMENT (< 5 YRS)" if remaining_life < 5.0 else "NORMAL MONITORING"

result = {
    "line_tag": line_tag,
    "t_nominal": t_nominal,
    "t_actual": t_actual,
    "t_minimum": t_minimum,
    "corrosion_rate": round(corrosion_rate, 3),
    "remaining_life_years": round(remaining_life, 2),
    "mandatory_action": action,
    "replacement_cost_inr": 1154400.0
}
print(json.dumps(result))
```"""

    return f"SovereignWorkbench local model response for request: {prompt[:80]}..."
