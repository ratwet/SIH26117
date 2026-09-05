# 📐 Architecture & LangGraph State Machine

Aquanex is architected around a stateful, cyclic **LangGraph** execution graph designed to eliminate mathematical hallucinations, enforce statutory standards, and guarantee autonomous recovery in safety-critical industrial environments.

---

## 🏛️ System Architecture Overview

Unlike monolithic chatbots that stream unstructured markdown text, Aquanex treats every engineering query as a formal state transition.

```text
                                  +-------------------+
                                  |   Incoming User   |
                                  |  Query / Diagram  |
                                  +-------------------+
                                            │
                                            ▼
                                   [ router_node ]
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │ (vision_audit)        │ (sop_lookup)          │ (general_chat)
                    ▼                       ▼                       ▼
       [ vision_extraction_node ]   [ sop_lookup_node ]     [ general_chat_node ]
                    │                       │                       │
                    ▼                       └───────────────┬───────┘
        [ math_generation_node ]                            │
                    │                                       │
                    ▼                                       │
        [ sandbox_runner_node ] <───────────┐               │
                    │                       │               │
        ┌───────────┴───────────┐           │               │
        │ Success               │ Failure   │               │
        ▼                       ▼           │               │
  [ compiler_node ]    [ error_distiller ]  │ (retry < 3)   │
        │                       │           │               │
        ▼                       └───────────┘               │
 [ audit_ledger_node ]                                      │
        │                                                   │
        └───────────────────────────┬───────────────────────┘
                                    │
                                    ▼
                         +--------------------+
                         | Final Stream & SSE |
                         | Artifact Delivery  |
                         +--------------------+
```

---

## 📋 The `WorkbenchState` Schema

All nodes in the graph read from and write to a centralized, typed state container defined in [`backend/app/graph/state.py`](backend/app/graph/state.py):

```python
class WorkbenchState(TypedDict):
    user_prompt: str                      # User's raw text prompt
    session_id: str                       # Unique session identifier
    node_history: List[str]               # Ordered history of executed nodes
    raw_vision_output: Optional[str]      # Extracted text from blueprints/diagrams
    pipe_data: Optional[Dict[str, Any]]   # Structured engineering parameters (P, T, Schedule)
    generated_code: Optional[str]         # Deterministic Python calculation script
    sandbox_stdout: Optional[str]         # Output stream from Bubblewrap sandbox
    sandbox_stderr: Optional[str]         # Error stream from Bubblewrap sandbox
    execution_success: bool               # Sandbox exit code boolean
    retry_count: int                      # Current self-healing retry attempt (0..3)
    distilled_error: Optional[str]        # Root-cause error message for self-healing
    deliverables: Dict[str, str]          # Mapping of deliverable types to file paths
    audit_entry: Optional[Dict[str, Any]] # Cryptographic ledger entry
    final_response: str                   # Clean response formatted for conversational client
    thought_stream: List[str]             # Natural conversational status updates
```

---

## ⚙️ The 8 Core Graph Nodes

### 1. `router_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py)
* **Purpose:** Inspects user query intent and attached artifacts. Routes automatically to:
  * `vision_audit`: When P&ID blueprints, ultrasonic reports, or line tags (`CDU`, `HGU`, `VDU`) are present.
  * `sop_lookup`: When statutory guidelines, OISD standards, or refinery procedures are queried.
  * `general_chat`: When conversational guidance or tool usage assistance is requested.

### 2. `vision_extraction_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py)
* **Purpose:** Interfaces with the local Vision OCR Engine (e.g. Qwen2-VL or private weights) to extract line numbers, nominal thickness ($t_{\text{nom}}$), actual measured wall thickness ($t_{\text{act}}$), design pressure ($P$), and operating temperature ($T$) from raster scans and isometric drawings.
* **Resilience:** Dynamically extracts parameters from user prompts and documents, falling back gracefully to validated industrial benchmarks (e.g. `CDU-2-04-150-A1A`).

### 3. `math_generation_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py)
* **Purpose:** Implements Program-Aided Language (PAL). Rather than calculating math directly in LLM weights, this node synthesizes a standalone, deterministic Python calculation script implementing:
  * ASME B31.3 Minimum Required Wall Thickness ($t_{\text{min}}$).
  * API 570 Short-term and Long-term Corrosion Rates ($CR$).
  * API 570 Remaining Safe Operating Life ($RL$).
  * Refinery turnaround mandatory shutdown triggers ($RL \le 5.0\text{ years}$).

### 4. `sandbox_runner_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py) & [`backend/app/sandbox/runner.py`](backend/app/sandbox/runner.py)
* **Purpose:** Spawns an isolated Linux Bubblewrap container (`bwrap`) with zero network access (`--unshare-net`).
* **Enforcements:** 5-second execution timeout, 256MB memory ceiling (`RLIMIT_AS`), and read-only host mounts (`/usr`, `/lib`, `/bin`).

### 5. `error_distiller_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py) & [`backend/app/sandbox/error_parser.py`](backend/app/sandbox/error_parser.py)
* **Purpose:** When a sandbox script fails (e.g., `ZeroDivisionError`, `KeyError`, `SyntaxError`), this node parses `stderr`, isolates the failing line number and exception name, and prepares a prompt for the reasoning engine.

### 6. `compiler_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py) & [`backend/app/compilers/`](backend/app/compilers/)
* **Purpose:** Takes structured math outputs and generates 10 publication-ready enterprise deliverables simultaneously (Word, Excel, AutoCAD DXF, 3D STL, PDF certificate, etc.).

### 7. `audit_ledger_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py) & [`backend/app/security/audit_chain.py`](backend/app/security/audit_chain.py)
* **Purpose:** Calculates cryptographic SHA-256 hashes of all generated deliverables, chains the record to the previous audit hash, and persists the immutable ledger entry to disk.

### 8. `sop_lookup_node`
* **File:** [`backend/app/graph/nodes.py`](backend/app/graph/nodes.py) & [`backend/app/rag/retriever.py`](backend/app/rag/retriever.py)
* **Purpose:** Queries local ChromaDB vector store powered by CPU FastEmbed embeddings (`bge-small-en-v1.5`). Returns grounded answers with exact section and page citations.

---

## 🔄 The 3-Cycle Autonomous Self-Healing Recovery Loop

In real-world refinery automation, generated code can fail due to malformed edge cases or syntax variations. Traditional LLM pipelines crash or emit apologies. Aquanex implements a **cyclic self-healing graph loop**:

```text
   +──────────────────────────────────────────────────────+
   |             math_generation_node                     |
   +──────────────────────────────────────────────────────+
                              │
                              ▼
   +──────────────────────────────────────────────────────+
   |             sandbox_runner_node                      |
   +──────────────────────────────────────────────────────+
                              │
                    Script Exit Code == 0?
                   /                      \
             [YES]                         [NO]
               │                             │
               ▼                             ▼
       +---------------+             +--------------------+
       | compiler_node |             |  error_distiller   |
       +---------------+             +--------------------+
                                             │
                                   retry_count < 3?
                                  /                \
                            [YES]                   [NO]
                              │                       │
               (retry_count += 1)                     ▼
                              │              +-----------------+
                              └────────────> | Graceful Failure |
                                             | & Operator Alert|
                                             +-----------------+
```

### Self-Healing Cycle Walkthrough:
1. **Initial Execution:** Code executes in Bubblewrap sandbox. If it triggers `ZeroDivisionError: division by zero`, the sandbox runner captures exit code `1` and captures `stderr`.
2. **Distillation:** `error_distiller_node` extracts: `Failed at line 14: ZeroDivisionError in calculation of short-term corrosion rate`.
3. **Targeted Correction:** State increments `retry_count = 1` and routes back to `math_generation_node`. The reasoning model receives the failure context and regenerates the script with defensive checks (`if delta_years > 0: ... else: ...`).
4. **Autonomous Resolution:** On retry 1, the script succeeds with exit code `0` and proceeds cleanly to compilation.
