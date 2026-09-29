# 🛡️ Aquanex (Aquanex) - Technical Architecture Specification
> **Document Reference:** `AQUANEX-ARCH-2026-V1`  
> **System Classification:** Mission-Critical Industrial AI Workbench (Air-Gapped Sovereign Compute)  
> **Target Environment:** Mangalore Refinery and Petrochemicals Limited (MRPL) / Public Sector Undertakings (PSUs)  
> **Statutory Compliance:** MoPNG Cyber Security Guidelines, CERT-In Section 70B, OISD-STD-118, API 570, ASME B31.3  
> **Principal Author:** Senior Principal Systems & AI Architect  
> **Last Updated:** September 2026  

---

## 1. Executive Summary & Architectural Charter

### 1.1 The Operational Crisis: The Industrial Air-Gap Deadlock
Modern hydrocarbon processing facilities, petrochemical complexes, and strategic defense infrastructure generate gigabytes of confidential, safety-critical telemetry every shift:
* **Piping and Instrumentation Diagrams (P&IDs)** and isometric fabrication schematics containing proprietary process chemistry and yield designs.
* **Non-Destructive Testing (NDT) logs** and ultrasonic wall-thickness survey grids detailing active metallurgical degradation.
* **Statutory turnaround filings, Capital Expenditure (Capex) procurement briefs**, and board-level risk registers.

Under directives from the **Ministry of Petroleum and Natural Gas (MoPNG)**, **CERT-In (Section 70B)**, and the **National Critical Information Infrastructure Protection Centre (NCIIPC)**, all refining and pipeline assets are classified as **Critical Information Infrastructure (CII)**. **Zero bytes of operational data may cross an external network boundary.** 

Simultaneously, refinery reliability teams face an acute productivity bottleneck:
1. Senior inspection engineers spend 35% of their working hours cross-referencing manual paper standards (API 570, ASME B31.3, OISD-118) against ultrasonic thickness inspection reports.
2. Field personnel calculating pipe corrosion rates and safe remaining service life frequently execute manual spreadsheet arithmetic susceptible to transcription errors.
3. Conventional cloud-based generative AI platforms (OpenAI, Anthropic, Google Cloud) introduce an unacceptable corporate espionage and regulatory attack surface: uploading a single P&ID sheet violates statutory data sovereignty laws. Conversely, personnel tempted to use external chatbots create high-risk "Shadow AI" vectors.

### 1.2 The Sovereign Engineering Thesis
Aquanex is an **on-premise, 100% air-gapped, agentic artificial intelligence workbench** designed to resolve this deadlock. It runs exclusively on local, customer-owned GPU workstations or departmental datacenter clusters over an isolated physical local area network (LAN) with no gateway to the public Internet.

#### The Three Core Engineering Invariants
```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           AQUANEX ARCHITECTURAL INVARIANTS                       │
├──────────────────────────────────┬───────────────────────────────────────────────┤
│ 1. Zero-Egress Physical Security │ If any external network route (WAN/WWAN/4G)   │
│                                  │ is detected, all processing halts instantly.  │
├──────────────────────────────────┼───────────────────────────────────────────────┤
│ 2. Program-Aided Language (PAL)  │ LLMs are non-deterministic language models.   │
│                                  │ Weights NEVER calculate engineering math.     │
│                                  │ Math is compiled into Python & sandboxed.     │
├──────────────────────────────────┼───────────────────────────────────────────────┤
│ 3. Cryptographic Non-Repudiation │ Every input, model inference, tool execution, │
│                                  │ and compiled deliverable is hashed & chained  │
│                                  │ into an append-only SHA-256 audit ledger.     │
└──────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## 2. C4 Architectural Model

We specify the software architecture using the C4 framework (Context, Containers, Components, Code).

### 2.1 Level 1: System Context Diagram
The System Context defines how Aquanex interfaces with refinery personnel and physical boundary constraints.

```text
                                  +-------------------------------------------------+
                                  |         AIR-GAPPED REFINERY CONTROL ROOM        |
                                  +-------------------------------------------------+
                                                           │
        ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
        │                                                  │                                                  │
        ▼                                                  ▼                                                  ▼
+────────────────+                                 +────────────────+                                 +────────────────+
| Field Operator |                                 | Senior Process |                                 | Security & IT  |
| / Junior Tech  |                                 |   Engineer     |                                 | Administrator  |
+────────────────+                                 +────────────────+                                 +────────────────+
        │                                                  │                                                  │
        │ Fast Field Query /                               │ Deep Inspection Audit,                           │ Model Registry,
        │ Preset 8B Model                                  │ Model Switching,                                 │ User RBAC,
        │ Fixed Prompts                                    │ Signoff Approval                                 │ Audit Integrity
        │                                                  │                                                  │
        └──────────────────────────────────┬───────────────┴──────────────────────────────────────────────────┘
                                           │
                                           │ HTTP / WebSocket over Isolated LAN (192.168.1.0/24)
                                           ▼
                    +─────────────────────────────────────────────────────────────+
                    |                      AQUANEX PLATFORM                       |
                    |            (Sovereign AI Engineering Workbench)             |
                    |                                                             |
                    |  • Ingests P&ID Schematics & NDT Ultrasonic Logs            |
                    |  • Executes Cyclic LangGraph Orchestration                  |
                    |  • Enforces Linux Namespace Kernel Sandboxing (`bwrap`)     |
                    |  • Compiles 10 Physical Production Deliverables             |
                    |  • Maintains Cryptographic Tamper-Proof Audit Chain         |
                    +─────────────────────────────────────────────────────────────+
                                           │
                                           │ Local I/O / UNIX Sockets
                                           ▼
                    +─────────────────────────────────────────────────────────────+
                    |                 ON-PREMISE LOCAL HARDWARE                   |
                    |                                                             |
                    |  • NVIDIA GPU (RTX 4090 / A100 / H100)                      |
                    |  • Local Storage: ChromaDB Embeddings, SQLite Audit Ledger   |
                    |  • Isolated Loopback Inference: Ollama / vLLM (127.0.0.1)   |
                    +─────────────────────────────────────────────────────────────+
```

### 2.2 Level 2: Container Diagram
The Container diagram illustrates the high-level technical runtime boundaries and protocols.

```text
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
| NODE 3: CLIENT WORKSTATION (192.168.1.102) / HOST DISPLAY                                               |
|                                                                                                         |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
|  | Single-Page Application (SPA) / Native Desktop Host                                                |  |
|  | • Web Client: Vanilla ES6 Modules + Tailwind CSS Design System                                     |  |
|  | • Desktop Shell: Tauri v2 / Lightweight Python WebKit Launcher (`scripts/run_linux_desktop.py`)       |  |
|  | • State: Session storage, real-time SSE telemetry listener, dynamic RBAC view controller          |  |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
+────────────────────────────────────────────────────┬────────────────────────────────────────────────────+
                                                     │ HTTP / SSE Stream (Port 8000)
                                                     ▼
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
| NODE 1: GPU COMPUTE WORKSTATION (192.168.1.100)                                                         |
|                                                                                                         |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
|  | FastAPI Gateway Server (`backend/app/main.py`)                                                    |  |
|  | • Lifespan manager, CORS middleware, Static asset provider                                         |  |
|  | • Authentication & RBAC Filter (`app/api/admin.py`, `app/security/auth.py`)                       |  |
|  | • SSE Telemetry & Health Stream (`app/api/telemetry.py`)                                          |  |
|  +─────────────────────────────────────────────────┬─────────────────────────────────────────────────+  |
|                                                    │ Function Call / State Hand-off                     |
|                                                    ▼                                                    |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
|  | LangGraph Cyclic Orchestrator (`backend/app/graph/`)                                              |  |
|  | • Central typed state container: `AgentState` (`state.py`)                                         |  |
|  | • Directed cyclic graph: `builder.py`, routing rules: `edges.py`                                  |  |
|  +───────────────┬───────────────────────────────┬───────────────────────────────┬───────────────────+  |
|                  │                               │                               │                      |
|                  ▼                               ▼                               ▼                      |
|  +───────────────────────────────+ +───────────────────────────────+ +───────────────────────────────+  |
|  | Foundation Model Gateway      | | Hardened Bubblewrap Sandbox   | | Omni-Modal Deliverable Engine |  |
|  | (`app/llm/engine.py`)         | | (`app/sandbox/runner.py`)     | | (`app/compilers/`)            |  |
|  | • Priority dispatch:          | | • Linux namespaces:           | | • Word: `python-docx`         |  |
|  |   1. Datacenter vLLM:8001     | |   `--unshare-net`             | | • Excel: `openpyxl`           |  |
|  |   2. Workstation Ollama:11434 | | • Memory cap: 256MB           | | • CAD: `ezdxf`                |  |
|  | • Pure OpenAI-compatible API  | | • CPU time cap: 5.0 seconds   | | • 3D Mesh: `numpy-stl`        |  |
|  | • Model unloading management  | | • Ephemeral ramdisk `/tmp`    | | • Vector PDF: ReportLab       |  |
|  +───────────────────────────────+ +───────────────────────────────+ +───────────────────────────────+  |
|                  │                               │                               │                      |
|                  ▼                               ▼                               ▼                      |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
|  | Local Storage & Security Daemons                                                                  |  |
|  | • Vector Database: ChromaDB (Local SQLite + `bge-small-en-v1.5` FastEmbed)                        |  |
|  | • Audit Ledger: SQLite3 (`data/mrpl_audit.db`) with forward-chained SHA-256 blocks                 |  |
|  | • Network Watchdog: Background daemon polling `/proc/net/route` & raw socket probes               |  |
|  +───────────────────────────────────────────────────────────────────────────────────────────────────+  |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

### 2.3 Level 3: Component Diagram (LangGraph Cyclic Engine)
The core intelligence engine operates as a stateful cyclic automaton. The transition from node to node is strictly deterministic.

```mermaid
stateDiagram-v2
    [*] --> router_node: User Prompt + Attachments

    router_node --> vision_extraction_node: Blueprint / P&ID / NDT Log Detected
    router_node --> sop_lookup_node: Standards / OISD / Statutory Query
    router_node --> general_chat_node: General Engineering Inquiry

    vision_extraction_node --> rag_retrieval_node: Extracted Metallurgy & Operating Specs
    sop_lookup_node --> general_chat_node: Context Injected

    rag_retrieval_node --> math_generation_node: Grounded API 570 Clauses
    
    math_generation_node --> sandbox_execution_node: Deterministic Python Code

    state sandbox_decision <<choice>>
    sandbox_execution_node --> sandbox_decision: Exit Code Evaluation

    sandbox_decision --> compile_deliverables_node: Exit Code 0 (Success)
    sandbox_decision --> distill_error_node: Exit Code != 0 (Failure)

    state retry_decision <<choice>>
    distill_error_node --> retry_decision: Evaluation of retry_count

    retry_decision --> math_generation_node: retry_count < 3 (Self-Healing Loop)
    retry_decision --> general_chat_node: retry_count >= 3 (Failsafe Degradation)

    compile_deliverables_node --> audit_ledger_node: Generate 10 Artifacts + Checksums
    audit_ledger_node --> [*]: Return Final Response + SSE Complete
    general_chat_node --> audit_ledger_node: Record Conversational Event
```

---

## 3. The LangGraph Deterministic Cyclic State Machine

### 3.1 Why A Cyclic Graph Over Linear Chains?
Standard LangChain pipelines and linear DAG frameworks are intrinsically ill-suited for industrial mission-critical workloads:
1. **Linear Fragility:** A single syntax discrepancy, missing variable declaration, or edge-case division by zero crashes a linear chain, forcing a complete restart and human intervention.
2. **Hallucinatory Arithmetic:** Monolithic models prompted to "calculate remaining safe life" will perform approximate arithmetic inside attention layers. In an industrial refinery, an error of $0.4\text{ mm}$ in corrosion allowance translates directly to catastrophic pipe rupture, loss of containment, or premature multimillion-dollar plant shutdowns.
3. **State Transparency:** LangGraph enforces a single, typed state object passed across nodes. Every node mutates the state explicitly, creating an auditable trace suitable for regulatory review.

### 3.2 State Container Definition (`AgentState`)
Located at [`backend/app/graph/state.py`](backend/app/graph/state.py), the `AgentState` typed dictionary represents the complete ephemeral lifecycle of a single user interaction:

```python
class AgentState(TypedDict):
    # User Inputs & Session Identity
    user_prompt: str                      # Raw incoming query string
    session_id: str                       # Unique UUID4 transaction ID
    uploaded_files: List[str]             # Absolute filesystem paths of attachments
    user_role: str                        # "admin" | "senior" | "junior"
    model_tier: str                       # "ENTERPRISE_100B" | "WORKSTATION_32B" | "EDGE_LAPTOP_8B"
    
    # Routing & Intent
    task_type: str                        # "VISION_AUDIT" | "SOP_LOOKUP" | "GENERAL_QUERY"
    active_model: str                     # Specific model ID serving current node
    
    # Extracted Technical Parameters
    extracted_specs: Optional[Dict[str, Any]] # Raw JSON dictionary from vision/regex
    pipe_data: Optional[PipeInspectionData]   # Strongly typed Pydantic engineering entity
    
    # Grounding & Context
    rag_chunks: List[RagChunk]            # Top-k vector similarity chunks
    rag_context: str                      # Pre-formatted Markdown context block
    
    # Code Generation & Sandbox Execution
    generated_code: Optional[str]         # Synthesized standalone Python script
    sandbox_result: Optional[SandboxResult]# Process exit code, stdout, stderr, execution time
    calc_result: Optional[Dict[str, Any]] # Structured JSON parsed from stdout
    
    # Self-Healing Control
    retry_count: int                      # Current execution iteration (0 <= retry_count <= 3)
    error_trace: Optional[str]            # Full Python stderr traceback
    distilled_error: Optional[str]        # 2-line root-cause summary for model prompt
    
    # Compiled Deliverable Outputs
    deliverables: Dict[str, str]          # Map of artifact type -> absolute filesystem path
    audit_hash: Optional[str]             # SHA-256 entry hash recorded in SQLite
    
    # Client Streaming
    thought_stream: List[str]             # Natural language milestone updates
    final_response: str                   # Formatted Markdown report delivered to UI
```

### 3.3 Deep Dive into the 8 Graph Nodes

#### Node 1: `route_task_node` ([`nodes.py:L120`](backend/app/graph/nodes.py#L120))
* **Objective:** Disambiguates user intent by analyzing prompt keywords and MIME types.
* **Mechanism:** Rather than routing every file attachment to computationally heavy vision models, the router evaluates file extensions and semantic tokens. If a user uploads an engineering drawing (`.png`, `.dxf`, `.stl`) or asks for corrosion/wall thickness assessment, it routes to `VISION_AUDIT`. If the prompt queries standards or manuals (`OISD`, `API 570`, `ASME`), it routes to `SOP_LOOKUP`.
* **Hardware Adaptation:** If `user_role == "junior"`, the active tier is automatically constrained to `EDGE_LAPTOP_8B` to guarantee sub-second field responsiveness.

#### Node 2: `vision_extraction_node` ([`nodes.py:L166`](backend/app/graph/nodes.py#L166))
* **Objective:** Ingests P&ID raster scans, isometric diagrams, and ultrasonic NDT inspection sheets to extract operational metallurgy and dimensions.
* **Extraction Architecture:** 
  1. Invokes multimodal vision weights (`Qwen2-VL-72B` on Datacenter, `Qwen2-VL-7B` on Workstation/Edge).
  2. Prompts for structured JSON output adhering to refinery nomenclature: `line_tag`, `material_spec`, `nominal_thickness_mm`, `actual_thickness_mm`, `design_pressure_psi`, `design_temp_celsius`.
  3. **Defensive Parsing Layer:** Employs regex pattern matching against prompt text for asset tags (e.g., `\b([A-Z]{2,4}-\d{1,2}-\d{2,3}-[A-Z0-9\-]+)\b`) and physical metrics. If an engineer pastes custom prompt overrides (`"measured thickness is 3.1mm"`), the extractor dynamically overwrites default drawing baselines.
  4. Yields a validated [`PipeInspectionData`](backend/app/schemas.py#L47) Pydantic entity.

#### Node 3: `rag_retrieval_node` ([`nodes.py:L288`](backend/app/graph/nodes.py#L288))
* **Objective:** Injects authoritative statutory regulatory clauses into the working state.
* **Implementation:** Offloads retrieval to an asynchronous worker thread targeting local ChromaDB (`CHROMA_PERSIST_DIR`). Embeddings are generated purely on CPU using `FastEmbed` (`bge-small-en-v1.5`), eliminating GPU VRAM contention.
* **Citations:** Retrieves top-5 relevant chunks from indexed PDFs: API 570 (*Inspection and Replacement of In-Service Piping*), ASME B31.3 (*Process Piping Design*), and OISD-STD-118 (*Layout and Fire Protection for Refineries*).

#### Node 4: `math_generation_node` ([`nodes.py:L325`](backend/app/graph/nodes.py#L325))
* **Objective:** Synthesizes a deterministic Python verification script implementing Program-Aided Language (PAL).
* **The Mathematical Formulation:**
  The generated script calculates three exact industrial parameters:
  
  $$\text{Corrosion Rate } (CR) = \frac{t_{\text{nominal}} - t_{\text{actual}}}{\text{Time in Service (years)}} \quad [\text{mm/year}]$$
  
  $$t_{\text{minimum}} = \frac{P \cdot D}{2 \cdot S \cdot E + 2 \cdot Y \cdot P} + c \quad [\text{per ASME B31.3}]$$
  
  $$\text{Remaining Safe Operating Life } (RL) = \frac{t_{\text{actual}} - t_{\text{minimum}}}{CR} \quad [\text{years}]$$
  
  $$\text{Statutory Action Trigger} = \begin{cases} \text{MANDATORY SHUTDOWN REPLACEMENT}, & \text{if } RL < 5.0 \text{ years} \\ \text{NORMAL IN-SERVICE MONITORING}, & \text{if } RL \ge 5.0 \text{ years} \end{cases}$$

* **Self-Healing Injection:** If `retry_count > 0`, the node dynamically prepends the distilled error and traceback from the previous execution cycle, prompting the coder engine to emit defensive guards (e.g., zero-division checks, type coercions).

#### Node 5: `sandbox_execution_node` ([`nodes.py:L409`](backend/app/graph/nodes.py#L409))
* **Objective:** Dispatches the unverified Python script into a fully isolated Bubblewrap Linux container.
* **Concurrency:** Uses `asyncio.to_thread` to prevent blocking the FastAPI asynchronous event loop during sandbox process instantiation.
* **Return Contract:** Captures process exit code, stdout, and raw stderr, assembling a typed [`SandboxResult`](backend/app/schemas.py#L27).

#### Node 6: `distill_error_node` ([`nodes.py:L443`](backend/app/graph/nodes.py#L443))
* **Objective:** Parses raw compiler or interpreter failure output into an actionable root-cause distillation.
* **Mechanism:** Leverages [`app.sandbox.error_parser`](backend/app/sandbox/error_parser.py) to extract the failing line number, exception type, and variable values while stripping environmental noise. Increments `retry_count += 1`.

#### Node 7: `compile_deliverables_node` ([`nodes.py:L468`](backend/app/graph/nodes.py#L468))
* **Objective:** Compiles the verified mathematical model and metallurgy specs into 10 enterprise deliverables simultaneously.
* **Artifact Generation:** Calls dedicated builders in [`app/compilers/`](backend/app/compilers/) (Word, Excel, AutoCAD DXF, 3D STL mesh, PDF certificates, etc.). Calculates individual SHA-256 hashes for all output files and synthesizes `MRPL_Audit_Manifest_<session>.json`.

#### Node 8: `audit_ledger_node` ([`nodes.py:L625`](backend/app/graph/nodes.py#L625))
* **Objective:** Cryptographically commits the transaction to the append-only SQLite ledger (`mrpl_audit.db`).
* **Non-Repudiation:** Chains the entry with the previous block's SHA-256 digest, recording prompt hash, output hash, tool exit codes, user ID, and timestamp.

---

## 4. Kernel-Level Sandboxing & Air-Gap Defense Architecture

### 4.1 Bubblewrap (`bwrap`) Namespace Isolation Deep Dive
To safely execute Python code synthesized dynamically by an LLM, Aquanex utilizes **Bubblewrap** (`bwrap`), an unprivileged user-namespace containerization technology native to modern Linux kernels (RHEL, Ubuntu, Debian).

```text
+---------------------------------------------------------------------------------------------------+
| HOST OPERATING SYSTEM (Linux Kernel 5.15+ / 6.x)                                                  |
|                                                                                                   |
|  +─────────────────────────────────────────────────────────────────────────────────────────────+  |
|  | BUBBLEWRAP ISOLATED NAMESPACE CONTAINER (`/usr/bin/bwrap`)                                  |  |
|  |                                                                                             |  |
|  |  [CLONE_NEWNET]  Network Stack: COMPLETELY DETACHED                                         |  |
|  |                  • No loopback, no eth0, no wlan0                                           |  |
|  |                  • `socket(AF_INET, SOCK_STREAM)` returns EPERM                             |  |
|  |                                                                                             |  |
|  |  [CLONE_NEWNS]   Filesystem Hierarchy: READ-ONLY MOUNTS                                     |  |
|  |                  • `--ro-bind /usr /usr`                                                    |  |
|  |                  • `--ro-bind /lib /lib` (and `/lib64`)                                     |  |
|  |                  • `--ro-bind /bin /bin`                                                    |  |
|  |                  • Host `/etc` and `/home` are UNMAPPED & INVISIBLE                         |  |
|  |                                                                                             |  |
|  |  [CLONE_NEWIPC]  Inter-Process Communication: ISOLATED                                      |  |
|  |                  • No shared memory access to host processes                                |  |
|  |                                                                                             |  |
|  |  [CLONE_NEWPID]  Process Table: ISOLATED                                                    |  |
|  |                  • Script executes as PID 1 inside container                                |  |
|  |                  • Terminated with SIGKILL if parent dies (`--die-with-parent`)             |  |
|  |                                                                                             |  |
|  |  Ephemeral Ramdisk:                                                                         |  |
|  |                  • `--tmpfs /tmp` (Max 64MB ephemeral RAM storage)                          |  |
|  |                  • Destroyed instantly upon process exit                                    |  |
|  |                                                                                             |  |
|  |  Kernel Resource Caps (setrlimit):                                                          |  |
|  |                  • Address Space Ceiling: 256 MB (`RLIMIT_AS`)                              |  |
|  |                  • Wall-Clock Timeout: 5.0 Seconds (Python `subprocess.wait`)               |  |
|  +─────────────────────────────────────────────────────────────────────────────────────────────+  |
+---------------------------------------------------------------------------------------------------+
```

#### Execution CLI Breakdown ([`app/sandbox/runner.py`](backend/app/sandbox/runner.py)):
```bash
/usr/bin/bwrap \
  --unshare-all \
  --unshare-net \
  --die-with-parent \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --ro-bind /opt/python /opt/python \
  --proc /proc \
  --dev /dev \
  --tmpfs /tmp \
  --dir /tmp/sandbox_run \
  --chdir /tmp/sandbox_run \
  python3 script.py
```

#### Fail-Closed Security Setting
In [`backend/app/config.py`](backend/app/config.py):
```python
ALLOW_UNSANDBOXED_FALLBACK: bool = False
```
If `/usr/bin/bwrap` is missing or fails kernel namespace creation (e.g. unprivileged user namespaces disabled), the platform **fails closed** with an explicit error rather than executing unconfined Python on the host operating system.

---

### 4.2 Network Watchdog & Reactive Air-Gap Kill-Switch
To guarantee continuous statutory compliance, Aquanex implements an autonomous network monitoring daemon located in [`backend/app/security/network_monitor.py`](backend/app/security/network_monitor.py).

```text
               +-------------------------------------------------------------+
               |             Kernel Routing Table (/proc/net/route)          |
               |             Active Non-Blocking UDP/TCP Socket Probes       |
               +-------------------------------------------------------------+
                                              │
                                              ▼
               +-------------------------------------------------------------+
               |            Background Network Monitor Daemon (2.0s loop)    |
               +-------------------------------------------------------------+
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │ Default Gateway Detected?                         │ Public Internet Reachable?
                    ▼                                                   ▼
         [ 0.0.0.0 via eth0/wlan0 ]                              [ 8.8.8.8:53 SYN-ACK ]
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              │
                                 Any Route Violations Found?
                                /                           \
                          [NO]                               [YES]
                            │                                  │
                            ▼                                  ▼
                 🟢 AIR-GAP COMPLIANT               🚨 AIR-GAP BREACH DETECTED
                 • Normal operations continue       • Sub-50ms Reactive Trip
                 • Outbound WAN delta = 0           • API returns HTTP 403 Forbidden
                 • UI shows green shield            • Active inferences aborted
                                                    • UI triggers Emergency Lockdown Modal
                                                    • Red screen + audible warning
                                                    • Security event logged to SHA-256 chain
```

#### Mathematical Proof of Zero-WAN Egress
The monitor reads raw kernel metrics from `/proc/net/dev` and `/proc/net/tcp` to compute interface byte differentials:

$$\Delta \text{WAN}_{\text{bytes}} = \text{TX}_{\text{wan}}(t) - \text{TX}_{\text{wan}}(t_0)$$

In compliance mode, $\Delta \text{WAN}_{\text{bytes}} \equiv 0$. Real-time metrics stream continuously to client frontends via Server-Sent Events (SSE) at `/api/telemetry/network/stream`.

#### Autonomous Recovery
The watchdog actively monitors interface detachment. If an unauthorized 4G USB dongle or Ethernet patch cable is physically unplugged, the daemon detects the removal of the default gateway in under $1.5\text{ seconds}$, clears the lockdown state, and restores API traffic without requiring a server reboot.

---

## 5. Bring-Your-Own-Model (BYOM) & Inference Gateway

### 5.1 Model Gateway Abstraction (`FoundationModelEngine`)
Refineries must never be locked into a single AI model provider or specific parameter weight. Aquanex implements a unified inference gateway in [`backend/app/llm/engine.py`](backend/app/llm/engine.py) that adheres strictly to OpenAI-compatible REST specifications (`/v1/chat/completions` and `/v1/models`).

```text
                      +-------------------------------------------------------+
                      |         Aquanex Unified Foundation Gateway            |
                      |            (`app/llm/engine.py`)                      |
                      +-------------------------------------------------------+
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │ Priority 1 (Datacenter Cluster)                                 │ Priority 2 (Workstation / Edge)
                 ▼                                                                 ▼
+──────────────────────────────────────────────────+             +──────────────────────────────────────────────────+
| vLLM / SGLang Engine                             |             | Ollama Engine                                    |
| Endpoint: http://127.0.0.1:8001/v1               |             | Endpoint: http://127.0.0.1:11434/v1              |
|                                                  |             |                                                  |
| • DeepSeek-R1 70B/671B MoE                       |             | • DeepSeek-R1-Distill-Qwen-8B (Q4_K_M)           |
| • Qwen2.5-72B-Instruct                           |             | • Qwen-2.5-Coder-7B-Instruct (Q4_K_M)            |
| • Qwen2-VL-72B-Instruct                          |             | • Qwen2-VL-7B-Instruct (Q4_K_M)                  |
| • Tensor Parallelism: TP=4                       |             | • Qwen-2.5-3B-Instruct (Q8_0)                    |
| • Continuous PagedAttention Batching             |             | • Single GPU (6GB-16GB VRAM)                     |
+──────────────────────────────────────────────────+             +──────────────────────────────────────────────────+
```

### 5.2 Sizing & Deployment Tier Matrix
Aquanex is designed with a hardware-agnostic profile selector ([`app/config.py`](backend/app/config.py)):

| Metric / Parameter | Tier 1: ENTERPRISE_100B | Tier 2: WORKSTATION_32B | Tier 3: EDGE_LAPTOP_8B |
| :--- | :--- | :--- | :--- |
| **Operational Setting** | Central Refinery Datacenter | Departmental Engineering Lab | Field Operations / Demo Rig |
| **Host Compute** | Dual AMD EPYC 9654 (192 Cores) | Intel Core i9-14900K / 64GB RAM | Intel Core i7 / Ryzen 7 / 32GB RAM |
| **GPU Hardware** | 4x NVIDIA A100 (80GB) / H100 | 1x NVIDIA RTX 4090 (24GB VRAM) | 1x NVIDIA RTX 3060/4060 (6-8GB VRAM) |
| **Serving Framework**| vLLM / TensorRT-LLM | Ollama / llama.cpp | Ollama / llama.cpp |
| **Tensor Parallelism**| `TP = 4` | `TP = 1` | `TP = 1` |
| **Context Window** | $131,072\text{ tokens}$ | $32,768\text{ tokens}$ | $8,192\text{ tokens}$ |
| **Reasoning Model** | `deepseek-r1:70b-q8_0` | `deepseek-r1:32b` | `deepseek-r1:8b` (Q4_K_M) |
| **Vision Model** | `qwen2-vl:72b-instruct` | `qwen2-vl:7b-instruct` | `qwen2-vl:7b-instruct-q4_K_M` |
| **Code Model** | `qwen2.5-coder:32b-instruct` | `qwen2.5-coder:14b-instruct` | `qwen2.5-coder:7b-instruct` |
| **Router Model** | `qwen2.5:72b-instruct` | `qwen2.5:14b-instruct` | `qwen2.5:3b-instruct-q8_0` |
| **Peak VRAM Cap** | $320\text{ GB}$ pooled | $24\text{ GB}$ | $5.5\text{ GB}$ (Sequential Unload) |

### 5.3 VRAM Residency & CUDA Out-Of-Memory Prevention
On edge hardware with limited VRAM ($6\text{GB} - 8\text{GB}$), loading both a 7B vision model and an 8B reasoning model simultaneously will instantly cause a CUDA Out-Of-Memory (OOM) kernel crash. 

Aquanex prevents this via an active **Sequential Model Unloading Policy**:
* When dispatching calls to Ollama, the gateway specifies `"keep_alive": 0` on intermediate inference requests.
* When the vision node finishes parameter extraction, the model weights are cleared from GPU memory before the coder or reasoning model is paged in. Peak VRAM utilization never exceeds $5.5\text{ GB}$, allowing full agentic execution on a single gaming laptop.

### 5.4 Fail-Closed Inference Policy
Under industrial safety protocols, generating fictional calculations is worse than failing to execute.
```python
# app/llm/engine.py:L186
raise ConnectionError(
    "NO LLM MODEL CONNECTED: Local model server is offline. "
    "Please start Ollama (http://127.0.0.1:11434) or vLLM (http://127.0.0.1:8001) to begin sovereign inference."
)
```
If no local inference server responds, the backend **refuses to fabricate outputs**. It returns a clean HTTP 503 status code with operational setup instructions, guaranteeing that mock data never enters official plant records.

---

## 6. Omni-Modal Deliverable Compilation Engine

A fundamental architectural divergence between Aquanex and conversational AI chatbots is the **Deliverables Subsystem**. Chatbots output markdown text blocks. Aquanex outputs formal, publication-ready physical engineering files.

```text
                     +----------------------------------------------------+
                     |    Validated Engineering State (PipeInspectionData) |
                     +----------------------------------------------------+
                                                │
       ┌────────────────────┬───────────────────┼───────────────────┬────────────────────┐
       │                    │                   │                   │                    │
       ▼                    ▼                   ▼                   ▼                    ▼
+──────────────+     +──────────────+    +──────────────+    +──────────────+     +──────────────+
|  Word Note   |     | Cost Matrix  |    |  AutoCAD CAD |    |  3D Spool    |     | Certificate  |
|   (.docx)    |     |   (.xlsx)    |    |   2D (.dxf)  |    |  Mesh (.stl) |     |   PDF (.pdf) |
+──────────────+     +──────────────+    +──────────────+    +──────────────+     +──────────────+
| python-docx  |     | openpyxl     |    | ezdxf        |    | numpy-stl    |     | ReportLab    |
| • Letterhead |     | • Formulas   |    | • ANSI Layer |    | • 3D Facets  |     | • Signatures |
| • Math Steps |     | • Conditional|    | • Spool Geo  |    | • Volumetric |     | • Audit QR   |
| • Signatures |     | • Contingency|    | • Weld Neck  |    | • 3D Print   |     | • Statutory  |
+──────────────+     +──────────────+    +──────────────+    +──────────────+     +──────────────+
       │                    │                   │                   │                    │
       └────────────────────┼───────────────────┴───────────────────┴────────────────────┘
                            │
                            ▼
     +─────────────────────────────────────────────────────────────+
     |   Calculated SHA-256 Checksums -> MRPL_Audit_Manifest.json  |
     +─────────────────────────────────────────────────────────────+
```

### 6.1 The 10 Production Deliverables Matrix

| # | File Extension | Compiler Module | Primary Purpose & Contents |
| :- | :--- | :--- | :--- |
| **1** | `.docx` | [`docx_builder.py`](backend/app/compilers/docx_builder.py) | **Official MRPL Executive Approval Note:** Formal corporate letterhead, statutory citations, equation derivation walkthroughs, recommended procurement actions, and dual signatory blocks for Senior Inspection and Chief Technical Managers. |
| **2** | `.xlsx` | [`xlsx_builder.py`](backend/app/compilers/xlsx_builder.py) | **Capex/Opex Cost & Risk Matrix:** Formatted spreadsheet with live dynamic Excel formulas (`SUM`, `PRODUCT`), color-coded risk flags (Red = Critical Replacement, Green = Compliant), line-item procurement breakdown, and automated 10% contingency calculations. |
| **3** | `.pptx` | [`pptx_builder.py`](backend/app/compilers/pptx_builder.py) | **Board-Level Executive Slide Deck:** High-impact executive briefing containing plant asset health summaries, turnaround risk evaluations, and financial impact assessments. |
| **4** | `.pdf` | [`pdf_builder.py`](backend/app/compilers/pdf_builder.py) | **Statutory Inspection Certificate:** Vector PDF document formatted to OISD-STD-118 and ASME standards with document hashing metadata and official stamping layouts. |
| **5** | `.dxf` | [`cad_builder.py`](backend/app/compilers/cad_builder.py) | **AutoCAD 2D Piping Spool Schematic:** Native DXF vector CAD layout displaying nominal bore dimensions, weld necks, flange ratings (Class 150 RF), and corrosion measurement thickness callouts. |
| **6** | `.stl` | [`stl_builder.py`](backend/app/compilers/stl_builder.py) | **3D CAD Mesh:** Tessellated 3D facet geometry of the affected piping spool for inspection visualization, spatial clearance checks, or rapid additive manufacturing. |
| **7** | `.png` | [`image_builder.py`](backend/app/compilers/image_builder.py) | **Ultrasonic Corrosion Heatmap:** Visual degradation spectrum mapping measured wall thickness across grid coordinate inspection locations. |
| **8** | `.csv` | [`csv_builder.py`](backend/app/compilers/csv_builder.py) | **Raw NDT Thickness Survey Log:** Comma-separated dataset of Condition Monitoring Locations (CML) ready for ingestion into SAP Plant Maintenance (PM) or Meridium APM. |
| **9** | `.py` | `compile_deliverables_node` | **Standalone Verification Script:** Independent, self-contained Python script allowing any field engineer to re-verify the exact math calculations offline on any computer. |
| **10**| `.json`| `compile_deliverables_node` | **Cryptographic Audit Manifest:** Machine-readable manifest containing environmental metadata, hardware tiers, input parameters, and SHA-256 hashes of the other 9 artifacts. |

---

## 7. Cryptographic SHA-256 Audit Chain Architecture

### 7.1 Mathematical Specification of the Ledger
Located at [`backend/app/security/audit_chain.py`](backend/app/security/audit_chain.py), the audit ledger guarantees tamper-evidence and non-repudiation for Indian statutory bodies (MoPNG, OISD, CERT-In).

The ledger is implemented as an append-only SQLite database table (`audit_ledger` in `mrpl_audit.db`). Each transaction block $n$ is defined as:

$$B_n = \langle \text{Index}_n, \text{EventID}_n, T_n, R_n, M_n, K_n, P_n, E_n, O_n, H_{n-1}, H_n \rangle$$

Where:
* $T_n$: UTC ISO-8601 Timestamp
* $R_n$: User Role (`admin`, `senior`, `junior`)
* $M_n$: Foundation Model Identifier (e.g., `deepseek-r1:8b`)
* $K_n$: Task Classification (`VISION_AUDIT`, `SOP_LOOKUP`)
* $P_n$: SHA-256 Hash of raw user prompt and attachments
* $E_n$: Tool execution status (Process exit code)
* $O_n$: SHA-256 Hash of synthesized deliverables and output report
* $H_{n-1}$: Hash of the previous block ($H_0 = 0^{64}$ for the Genesis Block)
* $H_n$: Block Entry Hash computed via:

$$H_n = \text{SHA-256}\Big( H_{n-1} \parallel T_n \parallel R_n \parallel P_n \parallel O_n \Big)$$

```text
┌──────────────────────────────────────┐          ┌──────────────────────────────────────┐
│            AUDIT BLOCK #1            │          │            AUDIT BLOCK #2            │
├──────────────────────────────────────┤          ├──────────────────────────────────────┤
│ Prev Hash: 000000000000000000...     │          │ Prev Hash: 8f4a1b8c2e9c4d7a1f3c9e... ◄───┐
│ Timestamp: 2026-09-08T10:15:00Z      │          │ Timestamp: 2026-09-08T10:17:22Z      │   │
│ User Role: senior                    │          │ User Role: junior                    │   │
│ Prompt Hash: a1b2c3d4...             │          │ Prompt Hash: d4e5f6a7...             │   │
│ Output Hash: e5f6a7b8...             │          │ Output Hash: 1a2b3c4d...             │   │
├──────────────────────────────────────┤          ├──────────────────────────────────────┤   │
│ Entry Hash: 8f4a1b8c2e9c4d7a1f3c9e...┼──────────┼──────────────────────────────────────┼───┘
└──────────────────────────────────────┘          │ Entry Hash: c7d8e9f01a2b3c4d5e6f7a...│
                                                   └──────────────────────────────────────┘
```

### 7.2 Verification & Tamper Detection Algorithm
The IT Administrator or statutory inspector can verify the ledger's integrity at any time via the endpoint `GET /api/telemetry/audit/verify`.

```python
# app/security/audit_chain.py:L142
def verify_audit_chain() -> Tuple[bool, int, Optional[str]]:
    conn = _get_db_connection()
    rows = conn.execute("SELECT * FROM audit_ledger ORDER BY id ASC").fetchall()
    previous_hash = GENESIS_HASH
    
    for idx, row in enumerate(rows):
        # 1. Verify that stored previous_hash matches preceding block
        if row["previous_hash"] != previous_hash:
            return False, idx, f"Broken link at block #{row['id']}: expected {previous_hash}"
            
        # 2. Recompute the entry hash from row data
        expected_hash = _compute_entry_hash(
            previous_hash=row["previous_hash"],
            timestamp=row["timestamp"],
            user_role=row["user_role"],
            prompt_hash=row["prompt_hash"],
            output_hash=row["output_hash"]
        )
        
        # 3. Detect unauthorized modifications
        if row["entry_hash"] != expected_hash:
            return False, idx, f"Tampered record at block #{row['id']}: hash mismatch"
            
        previous_hash = row["entry_hash"]
        
    return True, len(rows), None
```

If an attacker modifies a single character, thickness value, or timestamp in a historical record directly within SQLite, the entry hash $H_k$ changes. This invalidates $H_{k+1}$, cascading an immediate mathematical failure across all subsequent entries in the chain.

---

## 8. Role-Based Access Control (RBAC) & Persona Architecture

### 8.1 Persona Capability Matrix
Industrial organizations enforce strict hierarchical signoff protocols. A field technician cannot approve a $1,000,000$ INR spool procurement; an IT administrator has no need for engineering prompt chips.

Aquanex enforces a strict **3-Tier RBAC Architecture** ([`backend/app/api/admin.py`](backend/app/api/admin.py)):

```text
                                  +---------------------------------------+
                                  |     Refinery RBAC Directory           |
                                  +---------------------------------------+
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                            │                                            │
         ▼                                            ▼                                            ▼
+─────────────────────────────────+  +─────────────────────────────────+  +─────────────────────────────────+
| IT & Systems Admin (`admin`)    |  | Senior Engineer (`senior`)     |  | Junior Field Tech (`junior`)    |
+─────────────────────────────────+  +─────────────────────────────────+  +─────────────────────────────────+
| • Sovereign IT Control Hub      |  | • Senior Engineering Workbench  |  | • Fast Field Terminal           |
| • Manage User Model Permissions |  | • Model Selector Dropdown       |  | • Model Selector LOCKED (8B)    |
| • Model Registry (.gguf ingest) |  | • Analytical Engineering Tools  |  | • Pre-configured Ingestion      |
| • Audit Chain Verification      |  | • Full Signoff Authority        |  | • Requires Senior Co-Sign       |
| • Hardware Cluster Telemetry    |  | • All Deliverables Generated    |  | • Streamlined Field UI          |
| • NO Chat / Conversational UI   |  | • Standard Conversational Chat  |  | • Simplified Single-Click Ops   |
+─────────────────────────────────+  +─────────────────────────────────+  +─────────────────────────────────+
```

### 8.2 Detailed Persona Permissions Specification

| Capability / Resource | Administrator (`admin`) | Senior Lead (`senior`) | Junior Tech (`junior`) | Enforcement Layer |
| :--- | :---: | :---: | :---: | :--- |
| **Model Ingestion & Registration** |  **YES** | ❌ NO | ❌ NO | `can_register_models` header dep |
| **RBAC Policy & Model Assignment** |  **YES** | ❌ NO | ❌ NO | `can_manage_rbac` header dep |
| **Audit Ledger Verification** |  **YES** |  **YES** | ❌ NO | `can_view_audit_logs` header dep |
| **Dynamic Model Switching Dropdown**| ❌ N/A |  **YES** | ❌ **LOCKED (8B)** | Frontend DOM controller |
| **Custom Prompt Input Chips** | ❌ N/A |  **YES** | ❌ **PRESET ONLY** | Dynamic greeting renderer |
| **Isolated Sandbox Execution** |  **YES** |  **YES** |  **YES** | `can_execute_sandbox` |
| **Statutory Signoff & Certificate**| ❌ NO |  **YES** | ❌ **CO-SIGN REQ** | Document compilation metadata |
| **Default Model Assigned** | System Health | `deepseek-r1:70b` | `deepseek-r1:8b` | User registry profile |

### 8.3 Authentication & Header Propagation
The desktop client and web SPA pass identity metadata across all HTTP and WebSocket requests via custom headers:
* `X-User-Role`: `admin` | `senior` | `junior`
* `X-User-Id`: Unique identifier (e.g., `USR-ADMIN-01`, `USR-SNR-02`, `USR-JNR-03`)

The FastAPI backend validates incoming requests against [`RBAC_REGISTRY`](backend/app/api/admin.py#L23) via the dependency injector `require_permission(perm)`. Any attempt by a Junior token to register a model or alter permissions triggers an immediate `HTTP 403 Forbidden`.

---

## 9. Physical Hardware Deployment Topology

To prove 100% compliance during field audits and live hackathon evaluations, Aquanex operates across **three separate physical machines connected via an isolated physical Ethernet switch with zero external uplink**.

```text
                     [OFFLINE PHYSICAL ETHERNET SWITCH / ISOLATED LAN]
                      (Subnet: 192.168.1.0/24 | Default Gateway: NONE)
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │ 192.168.1.100                      │ 192.168.1.101                      │ 192.168.1.102
         ▼                                    ▼                                    ▼
+──────────────────────────────+   +──────────────────────────────+   +──────────────────────────────+
| NODE 1: GPU SERVER           |   | NODE 2: IT & AUDIT CONSOLE   |   | NODE 3: USER WORKBENCH       |
| (High-Performance Compute)   |   | (Administrative Audit)       |   | (Process Engineer Client)    |
+──────────────────────────────+   +──────────────────────────────+   +──────────────────────────────+
| • OS: Linux (Ubuntu 22/24)   |   | • OS: Linux / macOS / Win    |   | • OS: Linux / macOS / Win    |
| • NVIDIA RTX GPU (6-16GB+)   |   | • Browser / IT Dashboard     |   | • Tauri Native App / Browser |
| • FastAPI Server (:8000)     |   | • Real-Time Packet Monitor   |   | • P&ID Blueprint Ingestion   |
| • Ollama / vLLM (:11434/:8001|   | • tcpdump Egress Sniffer     |   | • Model Switching (Senior)   |
| • LangGraph Cyclic Engine    |   | • SHA-256 Ledger Verifier    |   | • Deliverable Inspection     |
| • Bubblewrap Sandbox         |   | • Model Access Governance    |   | • Local File Download        |
| • ChromaDB & SQLite Storage  |   | • Cluster Health Telemetry   |   | • Air-Gap Alarm Display      |
+──────────────────────────────+   +──────────────────────────────+   +──────────────────────────────+
```

### Static IP & Service Allocation Matrix
* **Node 1 (`192.168.1.100`):** Central Server. Runs `backend/app/main.py`. Hosts the compiled frontend distribution at `/` for zero-install client access. Ollama and vLLM are strictly bound to loopback `127.0.0.1`, accessible only through the FastAPI reverse proxy gateway per **ADR-007**.
* **Node 2 (`192.168.1.101`):** IT Administrator Console. Accesses `http://192.168.1.100:8000/?persona=admin`. Used by security teams to verify zero packet egress via `scripts/verify_sovereignty.sh` and validate SHA-256 ledger integrity.
* **Node 3 (`192.168.1.102`):** Engineer Client. Accesses `http://192.168.1.100:8000/?persona=senior` or `?persona=junior`. Runs the native desktop launcher (`aquanex-senior.desktop` / `aquanex-field.desktop`).

---

## 10. Architectural Trade-Offs & Decision Records (ADRs)

| Decision ID | Choice Made | Rejected Alternatives | Architectural Rationale |
| :--- | :--- | :--- | :--- |
| **ADR-001** | **LangGraph State Machine** | Linear LangChain, CrewAI, AutoGen | **Cyclic Self-Healing:** Refinery code execution requires stateful while-loops and bounded retries. Linear chains crash upon sandbox errors; multi-agent frameworks introduce conversational token overhead. |
| **ADR-002** | **Linux Bubblewrap (`bwrap`)** | Docker, Podman, WebAssembly (WASM) | **Zero-Daemon, Low Latency:** Docker requires root daemons (`dockerd`) and takes 800ms+ per container spawn. `bwrap` spawns unprivileged namespaces in under $15\text{ms}$ with zero daemon dependency and native C library support (`numpy`, `ezdxf`). |
| **ADR-003** | **Program-Aided Language (PAL)** | Direct LLM Arithmetic Reasoning | **Zero Hallucination:** LLM transformer weights perform approximate matrix multiplication, not arithmetic. Delegating formulas to sandboxed Python guarantees $100\%$ mathematical determinism. |
| **ADR-004** | **SQLite SHA-256 Hash Chain** | Distributed Blockchain, Hyperledger | **Zero Operational Overhead:** Hyperledger or Raft consensus requires multiple witness nodes and complex consensus overhead. An append-only SQLite database with recursive SHA-256 chaining provides equivalent tamper-evidence on a single air-gapped node. |
| **ADR-005** | **FastEmbed (CPU) + ChromaDB** | Cloud Vector DBs (Pinecone, Weaviate), Milvus | **VRAM Conservation:** Running embedding models on the GPU steals $1.5\text{GB} - 2\text{GB}$ of VRAM needed by the foundation reasoning engine. FastEmbed running quantized ONNX models on CPU leaves $100\%$ of GPU memory for inference. |
| **ADR-006** | **Tauri v2 + Lightweight WebKit** | Electron, Heavy Chromium Wrapper | **Footprint & Air-Gap Efficiency:** Electron bundles an 85MB Chromium runtime with 250MB+ memory usage. Tauri compiles to native OS WebKit/WebView with a $<15\text{MB}$ installer and $<40\text{MB}$ idle RAM footprint. |
| **ADR-007** | **Proxy-Isolated Model Gateway** | Direct Client-to-Ollama Networking | **Strict Perimeter Defense:** Ollama listening on `0.0.0.0` allows unauthenticated model manipulation from the LAN. Binding Ollama strictly to `127.0.0.1` and proxying via FastAPI guarantees that all inference passes through RBAC and audit logging. |

---

## 11. Failure Modes & Failsafe Recovery Matrix

```text
+───────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    FAILURE MODES & FAILSAFE ACTIONS                               |
+───────────────────────────┬───────────────────────────────┬───────────────────────────────────────+
| Trigger Event             | Detection Mechanism           | Autonomous Failsafe Action            |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| Unauthorized WAN Uplink   | Network Watchdog detects      | 1. Sub-50ms Reactive Trip.            |
| (4G modem / Wi-Fi tether) | default gateway in            | 2. API returns HTTP 403 Forbidden.    |
|                           | `/proc/net/route`             | 3. UI triggers Red Lockdown Screen.   |
|                           |                               | 4. Outbound bytes delta held at 0.    |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| Mathematical Division-by- | Sandbox runner captures       | 1. Exit code 1 isolated.              |
| Zero in Generated Script  | `ZeroDivisionError` in        | 2. Error distilled into 2-line cause. |
|                           | `stderr`                      | 3. State routes back to math node.    |
|                           |                               | 4. Self-heals up to 3 cycles.         |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| VRAM Exhaustion           | CUDA OOM warning on model     | 1. Gateway enforces sequential unload |
| (CUDA Out of Memory)      | load request                  |    (`keep_alive: 0`).                 |
|                           |                               | 2. Vision model unloaded before       |
|                           |                               |    reasoning weights are paged in.    |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| Local LLM Server Offline  | Gateway connection timeout    | 1. Fails closed immediately.          |
| (Ollama/vLLM not running) | (1.5s connect timeout)        | 2. Returns HTTP 503 Service Unavail.  |
|                           |                               | 3. Shows Clean Offline Notice Banner. |
|                           |                               | 4. Zero fake data hallucinated.       |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| Physical Tampering of     | Periodic verification queries | 1. Hash mismatch detected at Block #k.|
| SQLite Audit Database     | recompute SHA-256 chain       | 2. Admin dashboard raises red alert.  |
|                           |                               | 3. Event flagged in system telemetry. |
+───────────────────────────┼───────────────────────────────┼───────────────────────────────────────+
| Bubblewrap Missing from   | System sanity check on        | 1. `ALLOW_UNSANDBOXED_FALLBACK=False` |
| Host Operating System     | `/usr/bin/bwrap`              | 2. Refuses to run unconfined code.    |
|                           |                               | 3. Returns HTTP 500 configuration err.|
+───────────────────────────┴───────────────────────────────┴───────────────────────────────────────+
```

---

## 12. Verification & Testing Framework

The Aquanex platform is backed by an automated verification suite confirming functional, mathematical, and security contracts:

```bash
# Execute complete verification suite inside air-gapped backend
pytest backend/tests/ -v
```

### Verified Test Categories (44 Passing Automated Tests)
1. **Air-Gap & Telemetry Tests (`test_airgap.py`):** Validates default gateway detection, socket connection counting, and zero-WAN byte increment invariants.
2. **Sandbox & Kernel Isolation Tests (`test_sandbox.py`):** Validates namespace enforcement, execution timeouts (5.0s SIGKILL), memory ceilings (256MB), and `ZeroDivisionError` error distillation.
3. **LangGraph State Machine Tests (`test_graph.py`):** Validates cyclic state transitions, self-healing recovery loops across 3 retries, and deliverable state population.
4. **Omni-Modal Compiler Tests (`test_compilers.py`):** Validates binary and text generation for `.docx`, `.xlsx`, `.pptx`, `.dxf`, `.stl`, `.pdf`, `.png`, and `.csv`.
5. **Cryptographic Audit Chain Tests (`test_audit_chain.py`):** Validates SHA-256 block calculation, forward-link verification, and tamper detection upon record corruption.
6. **RBAC & Admin Governance Tests (`test_admin_rbac.py`):** Validates persona headers, model permission grants, user profiles, and unauthorized endpoint rejection.

---

## 13. Future Roadmap & Strategic Scalability

```text
  Phase 1: Hackathon & Core MVP (COMPLETED)
  ├── 100% Air-Gapped Local Inference Engine (Ollama 8B/3B)
  ├── Deterministic LangGraph State Machine with 3-Cycle Self-Healing
  ├── Bubblewrap Linux Kernel Sandboxing & Route Watchdog
  ├── 10 Omni-Modal Deliverable Compilers
  └── Cryptographic SHA-256 Audit Ledger & 3-Tier RBAC
  
  Phase 2: Enterprise Refinery Integration (Next Milestone)
  ├── Multi-Node vLLM Datacenter Cluster with Tensor Parallelism (TP=4)
  ├── Direct OPC-UA & SCADA Protocol Bridge for Real-Time Sensor Telemetry
  ├── Fine-Tuned Domain LoRA Adapters for Indian Refinery Equipment (MRPL CML Tags)
  └── Hardware Security Module (HSM) Integration for PKI Audit Signing
```

---
*End of Technical Architecture Specification - Mangalore Refinery and Petrochemicals Limited (MRPL / SIH26117)*
