# 🧠 SovereignWorkbench — Developer 1 Implementation Specification
> **Lead Developer 1:** **Rajat** (`@Rajatjyoti-arch`) & AI Coding Assistant  
> **Role:** Agentic Brain, LangGraph State Machine, Ollama Gateway & API Lead  
> **Team Structure:** Rajat (Dev 1: Orchestration/API) | Anand (Dev 2: Sandbox/Tools/Security) | Kaushal (Dev 3: GPU/Ollama)  
> **Project:** SovereignWorkbench (SIH 2026, PS 117 — MRPL)  
> **Shared Contract:** [`backend/app/schemas.py`](backend/app/schemas.py)  
> **Rule #1:** Build your modules to consume the shared contract. While Anand builds the tools, you mock them first to assemble the LangGraph flow.

---

## 🎯 1. Your Mission as Rajat (Developer 1)

You are building the **agentic brain and communication gateway** of SovereignWorkbench:

1. **Ollama Client & VRAM Management:** Connect asynchronously to local Ollama (`:11434`), manage model switching, and enforce explicit offloading (`keep_alive: 0`) so models never exceed the 5.5GB GPU VRAM ceiling.
2. **LangGraph State Machine:** Build the cyclic `StateGraph` linking Intent Routing $\rightarrow$ Vision Extraction $\rightarrow$ Math Generation $\rightarrow$ Sandbox Execution $\rightarrow$ Deliverable Compilation.
3. **The Self-Healing Loop:** Wire up the conditional retry edge in LangGraph. If the sandbox returns an error, pass the distilled error back to `DeepSeek-R1` to self-heal (capped at 3 retries).
4. **FastAPI Endpoints with SSE Streaming:** Expose `POST /api/chat` with Server-Sent Events (SSE) so the desktop client receives real-time thought traces (`"Analyzing P&ID..."`, `"Running API 570 in sandbox..."`, `"Generating Word report..."`).

---

## 🚫 2. File Ownership & Boundary Rules

### 🟢 Files YOU Own & Create:
```
backend/
├── app/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py               # Async Ollama HTTP wrapper (with keep_alive: 0)
│   │   ├── router.py               # Intent classifier (SOP vs P&ID vs Math)
│   │   └── prompts.py              # System prompts for Qwen, DeepSeek-R1, Qwen2-VL
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── nodes.py                # Graph node functions
│   │   ├── edges.py                # Conditional routing & retry logic
│   │   └── builder.py              # StateGraph assembly & compilation
│   └── api/
│       ├── __init__.py
│       ├── chat.py                 # POST /api/chat with SSE streaming
│       ├── admin.py                # GET/POST /api/admin/models, /api/admin/rbac
│       └── health.py               # GET /api/health
└── tests/
    └── test_dev1_graph.py          # Unit test proving LangGraph executes with mocks
```

### 🔴 Files You MUST NOT Touch:
* **Owned by Anand (Dev 2 — Tools, Sandbox, Deliverables, Security):**
  * `app/sandbox/*` (`runner.py`, `error_parser.py`)
  * `app/compilers/*` (`docx_builder.py`, `xlsx_builder.py`)
  * `app/rag/*` (`ingest.py`, `retriever.py`)
  * `app/security/*` (`network_monitor.py`, `audit_chain.py`)
  * `app/api/files.py`
  * `app/api/telemetry.py`
* **Owned by Kaushal (Dev 3 — GPU, Ollama Daemon & Models):**
  * `app/llm/*` (`client.py`, `router.py`, `prompts.py`)
  * Local Ollama setup, GGUF models, and VRAM management

### 🟡 Shared Files:
* `app/config.py`
* `app/schemas.py`

---

## 🧩 3. How to Develop Before Dev 2 Finishes (The Mocking Pattern)

You do **not** have to wait for Developer 2 to finish the sandbox or compilers. In `app/graph/nodes.py`, write mock implementations returning objects matching [`app/schemas.py`](backend/app/schemas.py):

```python
# Temporary Mocks inside app/graph/nodes.py (Replaced during final handshake)
from app.schemas import SandboxResult, ApprovalNotePayload, PipeInspectionData
from pathlib import Path

async def mock_execute_sandbox(code: str) -> SandboxResult:
    # Simulates successful execution or deliberate retry
    return SandboxResult(
        success=True,
        exit_code=0,
        stdout="Calculation complete: remaining_life = 3.14 years",
        parsed_output={"remaining_life": 3.14, "corrosion_rate": 0.35}
    )

def mock_compile_approval_note(payload: ApprovalNotePayload, out_path: Path) -> Path:
    out_path.write_text("Mock Word Doc")
    return out_path
```

Once Dev 2 finishes, you simply swap the imports from your mock functions to Dev 2's real functions:
```python
from app.sandbox.runner import execute_in_sandbox
from app.compilers.docx_builder import compile_approval_note
```

---

## 🔄 4. The LangGraph State Machine Architecture

```
                 ┌─────────────┐
                 │  route_node │
                 └──────┬──────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌───────────┐ ┌───────────┐ ┌──────────┐
    │  vision   │ │ rag_query │ │ general  │
    │  _node    │ │ _node     │ │ _chat    │
    └─────┬─────┘ └─────┬─────┘ └────┬─────┘
          │             │            │
          ▼             ▼            │
    ┌───────────┐ ┌───────────┐      │
    │  math     │ │ format    │      │
    │ _generate │ │ _rag_out  │      │
    └─────┬─────┘ └─────┬─────┘      │
          │             │            │
          ▼             │            ▼
    ┌───────────┐       │       ┌──────────┐
    │  sandbox  │       │       │   END    │
    │ _execute  │       │       └──────────┘
    └─────┬─────┘       │
          │             │
    [conditional]       │
    is_success?         │
     /        \         │
 [YES]        [NO, retry < 3]
   │            │
   │      ┌─────▼─────┐
   │      │ distill   │
   │      │ _error    │
   │      └─────┬─────┘
   │            │ (cycle back to math_generate)
   │            ▼
   │      ┌───────────┐
   │      │  math     │
   │      │ _generate │
   │      └───────────┘
   ▼
┌───────────┐
│ compile   │
│ _deliver  │
└─────┬─────┘
      ▼
┌───────────┐
│   END     │
└───────────┘
```

---

## 🤝 5. Handshake Verification with Dev 2
When merging with Dev 2:
1. Ensure both developers have committed to their respective feature branches.
2. Dev 1 merges `feature/dev2-tools-engine` into `feature/dev1-agent-brain`.
3. In `app/graph/nodes.py`, replace mocks with Dev 2's real tool functions.
4. Run an end-to-end test script: P&ID image $\rightarrow$ LangGraph $\rightarrow$ `bwrap` sandbox $\rightarrow$ output `.docx` file created on disk.
