# 🛠️ SovereignWorkbench — Developer 2 Implementation Specification
> **Lead Developer 2:** **Anand** & AI Coding Assistant  
> **Role:** Deterministic Tools, Sandboxing, Deliverables & Security Lead  
> **Team Structure:** Rajat (Dev 1: Orchestration/API) | Anand (Dev 2: Sandbox/Tools/Security) | Kaushal (Dev 3: GPU/Ollama)  
> **Project:** SovereignWorkbench (SIH 2026, PS 117 — MRPL)  
> **Shared Contract:** [`backend/app/schemas.py`](backend/app/schemas.py)  
> **Rule #1:** Build your modules to conform **strictly** to the shared contract. DO NOT alter field names or types in `app/schemas.py`.

---

## 🎯 1. Your Mission as Anand (Developer 2)

You are building the **deterministic muscle** of SovereignWorkbench. While Rajat (Dev 1) focuses on the LLMs, LangGraph state machine, and intent routing, **you build the high-stakes execution tools**:

1. **Linux Bubblewrap Sandbox (`bwrap`):** Safely execute Python math scripts in a 100% non-networked, restricted Linux namespace with strict 5-second timeouts and memory limits.
2. **Traceback Error Distiller:** When a script crashes, distill noisy 50-line Python tracebacks into clean 2-line root-cause summaries so the LLM can self-heal.
3. **Office Deliverable Compilers:** Take calculated inspection data and compile formal **`MRPL_Approval_Note.docx`** and **`Cost_Matrix.xlsx`** files with corporate letterhead, formulas, and signature blocks.
4. **Sovereign RAG:** Embed refinery SOPs and OISD standards into a local vector database (**ChromaDB**) using **FastEmbed CPU embeddings** (`bge-small-en-v1.5`), preserving 100% of GPU VRAM for the LLMs.
5. **Air-Gap Security & Cryptographic Audit:** Read `/proc/net/dev` to report real-time zero-packet telemetry, and maintain an immutable SHA-256 SQLite hash chain (`mrpl_audit.db`).

> 💡 **Key Advantage:** You **do not need a GPU or Ollama** to build and test your modules! You can write and unit-test 100% of your code with standard Python on any laptop.

---

## 🚫 2. File Ownership & Boundary Rules (Zero Merge Conflicts)

To guarantee that you and Developer 1 never experience git merge conflicts, observe these strict boundaries:

### 🟢 Files YOU Own & Create:
```
backend/
├── app/
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── runner.py               # bwrap execution wrapper
│   │   └── error_parser.py         # stderr cleaner for self-healing
│   ├── compilers/
│   │   ├── __init__.py
│   │   ├── docx_builder.py         # python-docx template engine
│   │   └── xlsx_builder.py         # openpyxl cost matrix generator
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py               # PDF/DOCX chunker + FastEmbed embedder
│   │   └── retriever.py            # ChromaDB similarity search
│   ├── security/
│   │   ├── __init__.py
│   │   ├── network_monitor.py      # /proc/net/dev reader
│   │   └── audit_chain.py          # SQLite SHA-256 append-only log
│   └── api/
│       ├── files.py                # Upload & deliverable download routes
│       └── telemetry.py            # /api/telemetry/network SSE route
└── tests/
    └── test_dev2_tools.py          # Unit tests proving all your tools work
```

### 🔴 Files You MUST NOT Touch:
* **Owned by Rajat (Dev 1 — LangGraph, Routing, FastAPI):**
  * `app/graph/*` (`state.py`, `nodes.py`, `edges.py`, `builder.py`)
  * `app/api/chat.py`
  * `app/api/admin.py`
* **Owned by Kaushal (Dev 3 — GPU, Ollama Daemon & Models):**
  * `app/llm/*` (`client.py`, `prompts.py`, `router.py`)

### 🟡 Shared Files (Consult Rajat & Kaushal Before Modifying):
* `app/config.py` (System settings & paths)
* `app/schemas.py` (The frozen contract)

---

## 🤝 3. The Exact Handshake Signatures (What Rajat Will Call)

Rajat's LangGraph nodes will directly import and call the following functions from your modules. **Ensure your function names, parameters, and return types match this table exactly:**

| Function to Expose | Module File | Input Parameters | Return Type (from `app.schemas`) |
| :--- | :--- | :--- | :--- |
| `execute_in_sandbox(code, timeout, mem_limit)` | `app.sandbox.runner` | `code: str, timeout: int = 5, mem_limit_mb: int = 256` | `SandboxResult` |
| `distill_python_traceback(raw_stderr)` | `app.sandbox.error_parser` | `raw_stderr: str` | `str` |
| `compile_approval_note(payload, output_path)` | `app.compilers.docx_builder` | `payload: ApprovalNotePayload, output_path: Path` | `Path` (saved file path) |
| `compile_cost_matrix(payload, output_path)` | `app.compilers.xlsx_builder` | `payload: CostMatrixPayload, output_path: Path` | `Path` (saved file path) |
| `query_sovereign_rag(query, top_k)` | `app.rag.retriever` | `query: str, top_k: int = 5` | `RagQueryResponse` |
| `ingest_document_to_rag(file_path)` | `app.rag.ingest` | `file_path: Path` | `int` (chunks added count) |
| `read_network_stats()` | `app.security.network_monitor` | *(none)* | `NetworkStats` |
| `record_audit_event(event)` | `app.security.audit_chain` | `event: AuditEvent` | `str` (entry_hash) |

---

## 📋 4. Detailed Component Implementation Specs

### Module 1: The Sandbox Runner (`app/sandbox/runner.py`)
* **Core Command:** Wrap execution in Linux `bwrap` (Bubblewrap) with the following flags:
  ```bash
  bwrap \
    --unshare-net \
    --unshare-pid \
    --ro-bind / / \
    --tmpfs /tmp \
    --proc /proc \
    --dev /dev \
    python3 -c "<code_to_execute>"
  ```
* **Fallback for Non-Linux/Local Dev:** If `bwrap` is not installed on the dev machine (e.g. testing on Windows/macOS without Docker), fall back gracefully to `subprocess.run([sys.executable, "-c", code], timeout=timeout, capture_output=True)` while logging a warning: `[WARNING] bwrap not found, running with standard subprocess`.
* **Output Parsing:**
  * If the script prints JSON to stdout (e.g., `print(json.dumps({"remaining_life": 3.1}))`), parse it into `SandboxResult.parsed_output`.
  * If exit code $\ne 0$, pass `stderr` through `distill_python_traceback` and populate `SandboxResult.distilled_error`.

---

### Module 2: The Error Distiller (`app/sandbox/error_parser.py`)
* **Problem:** Raw Python tracebacks can be 40+ lines long with internal file paths. If passed directly to an LLM, it gets confused by system paths.
* **Logic:**
  1. Scan `stderr` for lines matching: `File "<string>", line (\d+)` or `line (\d+), in <module>`.
  2. Extract the actual exception type and message: `ZeroDivisionError: float division by zero` or `KeyError: 'operating_years'`.
  3. Extract the offending line of code if present.
  4. Return a structured 2-line string:
     ```
     Runtime Error on line 18: ZeroDivisionError: float division by zero.
     Offending code: remaining_life = (t_actual - t_min) / corrosion_rate
     Root cause: corrosion_rate is 0.0. Add a safety check before dividing.
     ```

---

### Module 3: Word Approval Note Compiler (`app/compilers/docx_builder.py`)
* **Library:** `python-docx`
* **Visual Standards:**
  * Header: Bold dark blue (`#123456`) title: **MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)**
  * Subtitle: *Process Maintenance & Reliability Engineering Division — Technical Evaluation & Approval Note*
  * Metadata Table: Reference number, Line Tag, Unit Name, Inspection Date.
  * Ultrasonic Data Table: Nominal thickness ($4.8\text{ mm}$), Actual thickness ($3.2\text{ mm}$), Minimum required ($2.1\text{ mm}$), Corrosion rate ($0.35\text{ mm/yr}$), Remaining Life ($3.14\text{ years}$).
  * Formula Derivations: Bulleted step-by-step mathematical steps per API 570 / ASME B31.3.
  * Recommendation Box: Shaded table with bold recommendation text.
  * Signatory Block: Lines for Inspector signature, Maintenance Superintendent, and Chief Plant Manager.

---

### Module 4: Excel Cost Matrix Compiler (`app/compilers/xlsx_builder.py`)
* **Library:** `openpyxl`
* **Visual Standards:**
  * Header row: Navy blue background (`#1B365D`) with white bold text.
  * Columns: `Item Code`, `Description`, `Quantity`, `Unit`, `Unit Rate (INR)`, `Total Cost (INR)`.
  * Active Formulas: The `Total Cost` column must use an Excel formula: `=C4*E4` (Quantity $\times$ Unit Rate).
  * Subtotal & Grand Total: `=SUM(F4:F8)` with bold double-bottom border.
  * Contingency: `=F9*0.10` (10% contingency).
  * Risk Flag: Cell with conditional formatting — if Remaining Life $< 5$ years, cell highlights in Light Red with text: `MANDATORY REPLACEMENT REQUIRED`.

---

### Module 5: Sovereign RAG (`app/rag/ingest.py` & `app/rag/retriever.py`)
* **Vector Store:** `chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))`
* **Embedding Model:** `FastEmbed` using `BAAI/bge-small-en-v1.5` (runs on CPU via ONNX, exactly 0 GPU VRAM used).
* **Ingestion:**
  * Chunk text into 500-token passages with 50-token overlap.
  * Store metadata: `{"source_doc": "OISD-STD-118.pdf", "clause": "Clause 4.2"}`.
* **Retrieval:**
  * `query_sovereign_rag(query, top_k=5)` returns formatted `RagQueryResponse` with combined context string and source references.

---

### Module 6: Security & Audit (`app/security/`)
* **Network Monitor (`network_monitor.py`):**
  * Read `/proc/net/dev` on Linux. Sum `bytes_sent` across external network interfaces.
  * If non-Linux, read mock interface counters.
  * Expose `read_network_stats()` returning `NetworkStats`.
* **Cryptographic Audit Chain (`audit_chain.py`):**
  * SQLite database at `settings.AUDIT_DB_PATH` (`data/mrpl_audit.db`).
  * Table: `audit_ledger (id, timestamp, user_role, model_id, task_type, prompt_hash, tool_exit_code, output_hash, previous_hash, entry_hash)`.
  * `entry_hash = SHA256(previous_hash + timestamp + user_role + prompt_hash + output_hash)`.
  * If table is empty, `previous_hash = "0" * 64` (Genesis block).

---

## 🧪 5. Self-Contained Verification Suite for Dev 2

Create `backend/tests/test_dev2_tools.py` to verify all your tools work before handing them to Dev 1:

```python
import pytest
from pathlib import Path
from app.schemas import ApprovalNotePayload, PipeInspectionData, CostMatrixPayload
from app.sandbox.runner import execute_in_sandbox
from app.sandbox.error_parser import distill_python_traceback
from app.compilers.docx_builder import compile_approval_note
from app.compilers.xlsx_builder import compile_cost_matrix

def test_sandbox_success():
    code = 'import json; print(json.dumps({"result": 42}))'
    res = execute_in_sandbox(code)
    assert res.success is True
    assert res.exit_code == 0
    assert res.parsed_output["result"] == 42

def test_sandbox_self_healing_error_distillation():
    code = 'x = 10 / 0'
    res = execute_in_sandbox(code)
    assert res.success is False
    assert res.exit_code != 0
    assert "ZeroDivisionError" in res.distilled_error

def test_docx_generation(tmp_path):
    payload = ApprovalNotePayload(
        inspection_data=PipeInspectionData(
            line_tag="CDU-2-04-150-A1A",
            nominal_thickness_mm=4.8,
            actual_thickness_mm=3.2,
            remaining_life_years=3.1,
            mandatory_action="REPLACE"
        )
    )
    out_file = tmp_path / "test_note.docx"
    saved = compile_approval_note(payload, out_file)
    assert saved.exists()
    assert saved.stat().st_size > 1000  # Non-empty Word document

def test_xlsx_generation(tmp_path):
    payload = CostMatrixPayload()
    out_file = tmp_path / "test_matrix.xlsx"
    saved = compile_cost_matrix(payload, out_file)
    assert saved.exists()
    assert saved.stat().st_size > 1000  # Non-empty Excel workbook
```

Run tests with:
```bash
python -m pytest tests/test_dev2_tools.py -v
```

---

## 🤝 6. The Final Handshake Protocol

When Anand and Rajat are ready to integrate:

1. **Anand checks in code:** All functions under `app/sandbox/`, `app/compilers/`, `app/rag/`, and `app/security/` are committed to branch `feature/dev2-tools-engine`.
2. **Anand runs pytest:** All tests in `test_dev2_tools.py` pass with 100% green.
3. **Rajat pulls Anand's branch:** In `app/graph/nodes.py`, Rajat simply replaces his temporary mock functions with:
   ```python
   from app.sandbox.runner import execute_in_sandbox
   from app.compilers.docx_builder import compile_approval_note
   from app.compilers.xlsx_builder import compile_cost_matrix
   from app.rag.retriever import query_sovereign_rag
   from app.security.audit_chain import record_audit_event
   ```
4. **Zero Refactoring Needed:** Because both of you adhered strictly to `app/schemas.py`, the entire agentic pipeline will plug in and run on the very first try!
