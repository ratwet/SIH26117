# ⚡ SovereignWorkbench — Developer 3 Implementation Specification
> **Lead Developer 3:** **Kaushal** & AI Coding Assistant  
> **Role:** GPU Workstation Server, Ollama Daemon, Model Weights & VRAM Gateway Lead  
> **Team Structure:** Rajat (Dev 1: Orchestrator/API) | Anand (Dev 2: Sandbox/Tools/Security) | Kaushal (Dev 3: GPU/Ollama)  
> **Project:** SovereignWorkbench (SIH 2026, PS 117 — MRPL)  
> **Shared Contract:** [`backend/app/schemas.py`](backend/app/schemas.py)  
> **Rule #1:** Expose clean async inference functions so Rajat's LangGraph state machine can invoke local models without dealing with raw Ollama sockets or VRAM crashes.

---

## 🎯 1. Your Mission as Kaushal (Developer 3)

You are the **Model & GPU Infrastructure Lead** for SovereignWorkbench. You manage the physical gaming laptop / GPU server (Node 2) and the open-weight models that power the entire platform:

1. **Local Ollama Daemon Management:** Configure and maintain local `Ollama` running on `:11434` with zero external WAN connectivity.
2. **Model Fleet Ingestion & Quantization:** Pull and verify the 4 baseline open-weight models in quantized form (4-bit / 8-bit) so they fit within a single 6GB–12GB VRAM budget.
3. **Sequential VRAM Offloading (The OOM Shield):** Implement the active residency manager. Before any model is loaded into GPU memory, explicitly unload the previous model via `keep_alive: 0` so peak VRAM never exceeds **5.5 GB**.
4. **The Unified Model Gateway (`app/llm/client.py`):** Expose a clean, async Python function `call_llm()` that Rajat's LangGraph nodes call directly.
5. **System Prompt Engineering (`app/llm/prompts.py`):** Write and tune the precise industrial system prompts for Qwen-3B, DeepSeek-R1, and Qwen2-VL.
6. **Pluggable `.gguf` Model Registry:** Allow the IT Admin to drop new `.gguf` files into `/models_storage/` and register them into Ollama without touching Python code.

---

## 🖥️ 2. The 4 Baseline Models You Must Pull & Maintain

Run these commands in terminal on the GPU server:

```bash
# 1. Router & Intent Classifier (Fast, low memory)
ollama pull qwen2.5:3b-instruct-q8_0

# 2. Engineering Reasoning & API 570 Math Engine
ollama pull deepseek-r1:8b

# 3. P&ID Blueprint Vision & Document Extraction
ollama pull qwen2-vl:7b-instruct-q4_K_M

# 4. Tool Code Generation Specialist
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
```

### VRAM Budget Breakdown (Single RTX 3060/4060 GPU):
| Model | Size on Disk | Active VRAM | Context Window | Role in SovereignWorkbench |
| :--- | :--- | :--- | :--- | :--- |
| `qwen2.5:3b-instruct-q8_0` | ~3.4 GB | ~3.5 GB | 8k | Instant intent classification (< 1 sec) |
| `deepseek-r1:8b` | ~4.9 GB | ~5.4 GB | 8k | Chain-of-Thought math & API 570 Python script generation |
| `qwen2-vl:7b-instruct-q4_K_M` | ~4.7 GB | ~5.2 GB | 4k | Reads P&ID blueprints, line tags, and scanned NDT reports |
| `qwen2.5-coder:7b-instruct-q4_K_M`| ~4.7 GB | ~4.8 GB | 8k | General automation scripts & JSON parsing |

> ⚠️ **CRITICAL RULE:** Never allow `deepseek-r1:8b` and `qwen2-vl:7b` to sit in VRAM at the same time. The total ($5.4 + 5.2 = 10.6\text{ GB}$) will trigger CUDA OOM on a 6GB laptop! You must call `unload_model()` between transitions.

---

## 🚫 3. File Ownership & Boundary Rules

### 🟢 Files YOU Own & Create:
```
backend/
├── app/
│   └── llm/
│       ├── __init__.py
│       ├── client.py               # Async Ollama HTTP wrapper (`call_llm`, `unload_model`)
│       ├── manager.py              # Dynamic VRAM swapper & model registry
│       └── prompts.py              # Industrial prompt templates for all 4 models
└── tests/
    └── test_kaushal_llm.py         # Standalone tests verifying Ollama calls & VRAM unloading
```

### 🔴 Files You MUST NOT Touch:
* **Owned by Rajat (Dev 1 — LangGraph & API):**
  * `app/graph/*` (`state.py`, `nodes.py`, `edges.py`, `builder.py`)
  * `app/api/chat.py`
  * `app/api/admin.py`
* **Owned by Anand (Dev 2 — Tools, Sandbox, Deliverables, Security):**
  * `app/sandbox/*` (`runner.py`, `error_parser.py`)
  * `app/compilers/*` (`docx_builder.py`, `xlsx_builder.py`)
  * `app/rag/*` (`ingest.py`, `retriever.py`)
  * `app/security/*` (`network_monitor.py`, `audit_chain.py`)

### 🟡 Shared Files (Consult Rajat & Anand Before Modifying):
* `app/config.py`
* `app/schemas.py`

---

## 🤝 4. The Exact Handshake Signatures (What Rajat Will Call)

Rajat's LangGraph nodes will directly import from your `app.llm.client` and `app.llm.prompts`:

```python
# Function 1: Core Async LLM Invocation
async def call_llm(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[list[str]] = None,    # Base64 strings or file paths for Qwen2-VL
    temperature: float = 0.2
) -> str:
    """Sends prompt to local Ollama. Returns generated text."""

# Function 2: Sequential VRAM Purging
async def unload_model(model_name: str) -> bool:
    """Forces Ollama to unload model from GPU memory by setting keep_alive: 0."""

# Function 3: Model Headroom Check
async def ensure_model_ready(model_name: str) -> bool:
    """Checks if model is downloaded and ready to load."""

# Function 4: Model Listing
async def list_installed_models() -> list[str]:
    """Returns list of all available model tags in local Ollama."""
```

---

## 📋 5. Implementation Guide

### 5.1 Async Ollama Client (`app/llm/client.py`)
Use `httpx.AsyncClient` with a 120-second timeout:

```python
import httpx
from typing import Optional, List
from app.config import settings

class OllamaClient:
    def __init__(self, base_url: str = settings.OLLAMA_HOST):
        self.base_url = base_url

    async def call_llm(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        images: Optional[List[str]] = None,
        temperature: float = 0.2
    ) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if system_prompt:
            payload["system"] = system_prompt
        if images:
            payload["images"] = images

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def unload_model(self, model_name: str) -> bool:
        """Explicitly unloads model from VRAM."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model_name, "keep_alive": 0}
            )
            return resp.status_code == 200
```

---

### 5.2 System Prompt Engineering (`app/llm/prompts.py`)

#### 1. Router Prompt (`qwen2.5:3b-instruct-q8_0`):
```python
ROUTER_SYSTEM_PROMPT = """You are the SovereignWorkbench Central Intent Router for Mangalore Refinery and Petrochemicals Limited (MRPL).
Given a user query and uploaded file list, classify the intent into EXACTLY one of these tokens:
- VISION_AUDIT: User uploaded an engineering drawing, P&ID schematic, or scanned inspection PDF requiring visual extraction and calculations.
- SOP_LOOKUP: User is asking about refinery operating procedures, OISD standards, safety codes, or maintenance guidelines.
- GENERAL_QUERY: Routine knowledge work, drafting correspondence, or simple calculations.

Output ONLY the category token, nothing else."""
```

#### 2. DeepSeek-R1 Math Prompt (`deepseek-r1:8b`):
```python
MATH_GENERATOR_SYSTEM_PROMPT = """You are the Senior Reliability & Mechanical Engineering Expert at MRPL.
Your task is to compute remaining equipment life and mandatory statutory actions strictly following API 570 and ASME B31.3 standards.

RULES:
1. NEVER do mental math. You must generate a self-contained, executable Python script.
2. The script must define all extracted input variables explicitly.
3. Use formulas:
   - Corrosion Rate (mm/yr) = (t_nominal - t_actual) / service_years
   - Remaining Life (years) = (t_actual - t_minimum) / corrosion_rate
4. If Remaining Life < 5.0 years, set statutory_action = "MANDATORY SHUTDOWN REPLACEMENT REQUIRED".
5. At the end, the script MUST output a JSON string using print(json.dumps(result_dict)).
6. Output ONLY executable Python code inside ```python ``` blocks."""
```

#### 3. P&ID Vision Prompt (`qwen2-vl:7b-instruct-q4_K_M`):
```python
VISION_EXTRACTION_SYSTEM_PROMPT = """You are an expert Piping and Instrumentation Diagram (P&ID) Inspector at MRPL.
Inspect the provided technical drawing carefully and extract:
1. Line Tag (e.g. CDU-2-04-150-A1A)
2. Pipe Material specification (e.g. ASTM A106 Grade B)
3. Nominal Wall Thickness in mm
4. Actual measured wall thickness in mm
5. Design pressure and temperature

Return the extracted values in structured JSON format with confidence scores."""
```

---

## 🧪 6. Standalone Verification Suite for Kaushal

Create `tests/test_kaushal_llm.py` to verify your Ollama connection and model switching before handing over to Rajat:

```python
import pytest
import asyncio
from app.llm.client import OllamaClient
from app.config import settings

@pytest.mark.asyncio
async def test_ollama_connectivity():
    client = OllamaClient(settings.OLLAMA_HOST)
    async with httpx.AsyncClient() as c:
        resp = await c.get(f"{settings.OLLAMA_HOST}/api/tags")
        assert resp.status_code == 200
        models = [m["name"] for m in resp.json().get("models", [])]
        print(f"\nInstalled models: {models}")

@pytest.mark.asyncio
async def test_router_inference():
    client = OllamaClient(settings.OLLAMA_HOST)
    response = await client.call_llm(
        model=settings.MODEL_ROUTER,
        prompt="Audit this P&ID drawing for line CDU-2-04-150-A1A",
        system_prompt="Classify intent into VISION_AUDIT, SOP_LOOKUP, or GENERAL_QUERY. Return token only."
    )
    print(f"\nRouter response: {response.strip()}")
    assert "VISION_AUDIT" in response.upper()

@pytest.mark.asyncio
async def test_vram_unloading():
    client = OllamaClient(settings.OLLAMA_HOST)
    unloaded = await client.unload_model(settings.MODEL_ROUTER)
    assert unloaded is True
```

Run tests with:
```bash
python -m pytest tests/test_kaushal_llm.py -v -s
```

---

## 🤝 7. Handshake Protocol with Rajat (Dev 1)

1. **Kaushal commits:** Push `app/llm/client.py`, `app/llm/manager.py`, and `app/llm/prompts.py` to branch `feature/kaushal-model-engine`.
2. **Kaushal verifies:** `test_kaushal_llm.py` passes 100% green against local Ollama.
3. **Rajat integrates:** In `app/graph/nodes.py`, Rajat imports `call_llm` and `unload_model` directly.
4. **Result:** LangGraph now drives the real GPU models with automated VRAM offloading!
