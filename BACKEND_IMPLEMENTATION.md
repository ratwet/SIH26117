# 🏗️ SovereignWorkbench — Backend Implementation Guide (`BACKEND_IMPLEMENTATION.md`)
> **Project:** SovereignWorkbench  
> **Target System:** Node 2 (Central GPU Server / Gaming Laptop)  
> **Framework:** FastAPI + LangGraph + Ollama  
> **Repository Root:** `/home/cyanide/SIH/`  
> **Status:** Implementation Blueprint  

---

## 📌 1. Architecture Overview

The SovereignWorkbench backend is the central computational engine of the 3-tier air-gapped system. It operates on an isolated local subnetwork with **zero external internet connectivity**.

### Core Responsibilities:
1. **Multi-Model Orchestration (LangGraph):** Routes tasks dynamically between specialized open-weight models (`Qwen-2.5-3B`, `DeepSeek-R1-8B`, `Qwen2-VL-7B`, `Qwen-2.5-Coder-7B`).
2. **Deterministic Linux Sandboxing (`bwrap`):** Offloads safety-critical engineering calculations (API 570 / ASME) into an isolated, non-networked Linux namespace.
3. **Autonomous Self-Healing Loop:** Automatically intercepts runtime errors (`stderr`), distills root causes, and re-prompts the model for up to 3 self-correction iterations.
4. **Office Deliverables Compiler:** Directly generates signable executive Word notes (`MRPL_Approval_Note.docx`) and financial spreadsheets (`Cost_Matrix.xlsx`).
5. **Sovereign RAG (Zero-GPU VRAM):** Searches plant manuals, OISD standards, and SOPs using CPU-based embeddings (`bge-small-en-v1.5`) via FastEmbed and ChromaDB.
6. **Air-Gap Telemetry & Cryptographic Audit:** Exposes live socket telemetry proving 0 outbound WAN packets and maintains an append-only SHA-256 SQLite ledger (`mrpl_audit.db`).

---

## 👥 2. Three-Way Developer Division of Labor

The backend is cleanly partitioned among three developers using **Contract-First Architecture** to eliminate git merge conflicts and blocking dependencies:

```
                          ┌───────────────────────────┐
                          │    THE SHARED CONTRACT    │
                          │   `backend/app/schemas.py`│
                          └─────────────┬─────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
      RAJAT                           ANAND                          KAUSHAL
[Dev 1: Orchestrator & API]    [Dev 2: Tools & Security]      [Dev 3: Model & GPU Lead]
• LangGraph State Machine      • Bubblewrap Sandbox (`bwrap`)  • Local Ollama Daemon
• Cyclic Self-Healing Edges    • Traceback Error Distiller     • Model Ingestion & GGUF
• System Prompts & Intent Route• Word (`.docx`) Compiler       • VRAM Residency Offloader
• FastAPI & SSE Streaming      • Excel (`.xlsx`) Compiler      • Hardware Benchmarking
• Admin / RBAC endpoints       • CPU ChromaDB Sovereign RAG    • Async LLM Gateway (`call_llm`)
                               • `/proc/net` & SHA-256 Audit   
```

---

## 📁 3. Complete Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point, CORS, lifespan
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── schemas.py                  # FROZEN SHARED CONTRACT (Pydantic models)
│   │
│   ├── graph/                      # [OWNED BY RAJAT - DEV 1] LangGraph State Machine
│   │   ├── __init__.py
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── nodes.py                # Vision, Math, Sandbox, Compiler nodes
│   │   ├── edges.py                # Conditional routing & retry logic
│   │   └── builder.py              # StateGraph assembly & compilation
│   │
│   ├── api/                        # [OWNED BY RAJAT & ANAND] REST / SSE Endpoints
│   │   ├── __init__.py
│   │   ├── chat.py                 # POST /api/chat with SSE streaming (Rajat)
│   │   ├── files.py                # File upload & download endpoints (Anand)
│   │   ├── admin.py                # Model registry & RBAC endpoints (Rajat)
│   │   ├── telemetry.py            # /api/telemetry/network SSE stream (Anand)
│   │   └── health.py               # GET /api/health (Rajat)
│   │
│   ├── llm/                        # [OWNED BY KAUSHAL - DEV 3] Model Serving & Gateway
│   │   ├── __init__.py
│   │   ├── client.py               # Async Ollama HTTP wrapper (`call_llm`)
│   │   ├── manager.py              # VRAM offloader (`keep_alive: 0`)
│   │   └── prompts.py              # System prompt templates
│   │
│   ├── sandbox/                    # [OWNED BY DEV 2] Sandboxed Execution
│   │   ├── __init__.py
│   │   ├── runner.py               # Linux `bwrap` execution wrapper
│   │   └── error_parser.py         # Traceback distillation for self-healing
│   │
│   ├── compilers/                  # [OWNED BY DEV 2] Document Generators
│   │   ├── __init__.py
│   │   ├── docx_builder.py         # python-docx template engine
│   │   └── xlsx_builder.py         # openpyxl cost matrix generator
│   │
│   ├── rag/                        # [OWNED BY DEV 2] Sovereign RAG
│   │   ├── __init__.py
│   │   ├── ingest.py               # Chunking & FastEmbed CPU pipeline
│   │   └── retriever.py            # ChromaDB similarity search
│   │
│   └── security/                   # [OWNED BY DEV 2] Air-Gap & Governance
│       ├── __init__.py
│       ├── network_monitor.py      # /proc/net/dev socket reader
│       └── audit_chain.py          # SQLite SHA-256 append-only ledger
│
├── data/                           # Runtime storage (gitignored)
│   ├── uploads/                    # Ingested PDFs & drawings
│   ├── deliverables/               # Generated .docx and .xlsx
│   ├── chromadb/                   # Persistent vector database
│   └── mrpl_audit.db               # Tamper-evident SQLite audit log
│
├── requirements.txt                # Python package manifest
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Local multi-container orchestrator
└── tests/
    ├── test_dev1_graph.py          # Dev 1 LangGraph unit test suite
    └── test_dev2_tools.py          # Dev 2 Sandbox/Compiler unit test suite
```

---

## 🔄 4. The LangGraph State Machine Architecture

The agent execution pipeline is modeled as a **StateGraph** with a **cyclic self-healing feedback loop**:

```
                       ┌────────────────┐
                       │  ENTRY: ROUTE  │
                       └───────┬────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
     │ VISION NODE │    │  RAG QUERY  │    │ GENERAL CHAT│
     │  (Qwen2-VL) │    │  (ChromaDB) │    │  (Qwen-3B)  │
     └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
            │                  │                  │
            ▼                  ▼                  │
     ┌─────────────┐    ┌─────────────┐           │
     │  MATH NODE  │    │ FORMAT RAG  │           │
     │(DeepSeek-R1)│    │   OUTPUT    │           │
     └──────┬──────┘    └──────┬──────┘           │
            │                  │                  │
            ▼                  │                  ▼
     ┌─────────────┐           │            ┌───────────┐
     │SANDBOX EXEC │           │            │    END    │
     │   (bwrap)   │           │            └───────────┘
     └──────┬──────┘           │
            │                  │
    [CONDITIONAL EDGE]         │
     Is Exit Code 0?           │
       /         \             │
   [YES]        [NO]           │
     │            │            │
     │      (Retries < 3)      │
     │            │            │
     │     ┌──────▼──────┐     │
     │     │DISTILL ERROR│     │
     │     │ (Parser)    │     │
     │     └──────┬──────┘     │
     │            │ (Cycle)    │
     │            ▼            │
     │     ┌─────────────┐     │
     │     │  MATH NODE  │     │
     │     │(DeepSeek-R1)│◄────┘
     │     └─────────────┘
     ▼
┌──────────────────┐
│COMPILE DELIVER   │
│  (.docx / .xlsx) │
└────────┬─────────┘
         ▼
┌──────────────────┐
│       END        │
└──────────────────┘
```

### Key LangGraph State Nodes:
1. **`route_node`:** Classifies intent using `Qwen-2.5-3B` into `"vision_audit"`, `"rag_lookup"`, or `"general"`.
2. **`vision_node`:** Uses `Qwen2-VL-7B` to extract line tags, nominal thickness, valve types from drawings. Calls `unload_model()` immediately after.
3. **`math_generate_node`:** Uses `DeepSeek-R1-8B` to write a self-contained Python calculation script implementing API 570 / ASME formulas.
4. **`sandbox_node`:** Calls `execute_in_sandbox()` via `bwrap --unshare-net`. Captures `stdout`, `stderr`, and `exit_code`.
5. **`distill_error_node`:** Parses raw `stderr` into a concise 2-line root cause and increments `retry_count`. Cycles back to `math_generate_node`.
6. **`compile_deliverable_node`:** Calls `compile_approval_note()` and `compile_cost_matrix()`, writing files to disk.

---

## 📡 5. REST & SSE Streaming API Endpoints

| Endpoint | Method | Owner | Description |
| :--- | :---: | :---: | :--- |
| `/api/chat` | `POST` | Rajat (Dev 1) | Main streaming agentic pipeline. Accepts multipart form (prompt + files). Streams SSE events. |
| `/api/health` | `GET` | Rajat (Dev 1) | Health check returning status, uptime, active model, and GPU VRAM usage. |
| `/api/admin/models` | `GET/POST` | Rajat (Dev 1) | Lists available `.gguf` models in `/models_storage/` and triggers manual offload. |
| `/api/admin/rbac` | `GET/POST` | Rajat (Dev 1) | Queries or updates user role permissions (`admin`, `senior`, `junior`). |
| `/api/files/upload` | `POST` | Anand (Dev 2) | Saves uploaded PDFs and PNG drawings to `/data/uploads/`. |
| `/api/deliverables/{id}` | `GET` | Anand (Dev 2) | Downloads generated `.docx` or `.xlsx` files. |
| `/api/telemetry/network` | `GET` | Anand (Dev 2) | Server-Sent Events (SSE) stream broadcasting real-time `/proc/net/dev` socket bytes. |
| `/api/admin/audit` | `GET` | Anand (Dev 2) | Returns paginated entries from the SHA-256 SQLite audit ledger. |

---

## 🛡️ 6. Handshake Contract Summary

All data flowing between Dev 1, Dev 2, and Dev 3 is defined in [`backend/app/schemas.py`](backend/app/schemas.py):
* `SandboxResult`: Returned by Dev 2's sandbox runner to Dev 1's LangGraph node.
* `ApprovalNotePayload`: Provided by Dev 1 to Dev 2's Word document generator.
* `CostMatrixPayload`: Provided by Dev 1 to Dev 2's Excel generator.
* `RagQueryResponse`: Returned by Dev 2's vector search to Dev 1's RAG node.
* `NetworkStats`: Returned by Dev 2's socket monitor to the UI telemetry stream.
* `AuditEvent`: Written to Dev 2's SQLite hash chain on every major agent transaction.

---

## 🧪 7. Phased Verification & Testing Plan

1. **Dev 2 Standalone Test:**
   ```bash
   python -m pytest tests/test_dev2_tools.py -v
   ```
   *Verifies sandbox isolation, traceback distillation, Word document generation, and Excel formatting.*
2. **Dev 1 Standalone Test:**
   ```bash
   python -m pytest tests/test_dev1_graph.py -v
   ```
   *Verifies LangGraph state transitions, mock tool execution, and the 3-retry self-healing edge.*
3. **Integration Test:**
   Swap Dev 1 mocks with Dev 2 real imports. Run end-to-end P&ID audit script:
   ```bash
   python -m pytest tests/test_integration.py -v
   ```
