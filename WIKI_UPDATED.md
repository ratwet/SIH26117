# MRPL Sovereign On-Premise Agentic AI Workbench (Wiki Reference Draft)
**Competition:** Smart India Hackathon (SIH) 2026  
**Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL)  
**Problem Statement ID:** 26117  
**Category:** Software | **Theme:** Smart Automation  
**Deployment Infrastructure:** 3-Node Physical Offline Ubuntu LAN (Server, Admin, User)  

> [!NOTE]
> This is the updated local draft of the team wiki, harmonized with the production codebase in `backend/app/` and the specs in `ANAND_SPEC.md` and `RAJAT_SPEC.md`.

---

## 1. Executive Summary & Context

Refineries, PSUs, defense manufacturing units, and critical infrastructure organizations generate large amounts of sensitive, confidential information, including Piping & Instrumentation Diagrams (P&IDs), inspection reports, approval notes, internal code, and unreleased designs. Due to strict confidentiality, regulatory, and corporate policies, this data cannot be processed using public cloud AI services (e.g., ChatGPT, Claude, Codex).

The **MRPL Sovereign On-Premise Agentic AI Workbench** provides a fully local, self-hosted, air-gapped solution running on organizational infrastructure. The system is deployed across three physical Ubuntu Linux laptops connected via an isolated physical Ethernet switch with zero external network connectivity. It utilizes open-weight multimodal models to execute multi-step agentic workflows, perform local RAG knowledge retrieval, execute code in isolated kernel namespaces via Bubblewrap (`bwrap`), and generate tangible deliverables (`.docx`, `.xlsx`, `.pptx`, `.py`) while offering verifiable technical proof of zero outbound network egress.

---

## 2. Core Project Objectives

1. **Air-Gapped Data Sovereignty:** Guarantee zero external network calls during runtime, backed by visible network monitoring evidence (`tcpdump`, `/proc/net/dev`).
2. **Dynamic Multi-Model Routing:** Automatically select specialized open-weight models based on task type (e.g., Coder models for code execution, Vision LLMs for scanned PDFs/diagrams, Reasoning LLMs for analysis).
3. **3-Node Physical Architecture:** Deploy across dedicated Ubuntu Server, Admin, and User nodes via an offline LAN switch.
4. **Isolated Proxy Gateway:** Bind Ollama LLM serving strictly to local loopback (`127.0.0.1`), routing all client traffic through an audited FastAPI gateway on `192.168.1.100:8000`.
5. **Agentic Workflows:** Implement multi-step task planning, local tool calling, autonomous error recovery loops (3 retries), and human-in-the-loop escalation.
6. **Tangible Artifact Generation:** Output structured Word approval notes (`.docx`) with corporate letterhead, financial cost matrices with active Excel formulas (`.xlsx`), and validated Python scripts.
7. **Grounded Local Knowledge Base:** Integrate local SOPs, manuals, and technical correspondence via an air-gapped RAG architecture with exact source citations.

---

## 3. Physical 3-Node Network & Topology Specs

```text
               +-------------------------------------------------------+
               |  OFFLINE LOCAL ETHERNET SWITCH (Zero Internet WAN)    |
               +-------------------------------------------------------+
                                  |
         +------------------------+------------------------+
         | (192.168.1.100)        | (192.168.1.101)        | (192.168.1.102)
         v                        v                        v
+------------------+    +------------------+    +------------------+
| UBUNTU NODE 1:   |    | UBUNTU NODE 2:   |    | UBUNTU NODE 3:   |
| SERVER           |    | ADMIN / AUDIT    |    | USER WORKBENCH   |
| - FastAPI Gateway|    | - Egress Monitor |    | - Web UI Client  |
| - Ollama (127.0.1|    | - Audit Dashboard|    | - Doc Upload     |
| - LangGraph Core |    | - System Rules   |    | - Deliverable    |
| - bwrap Sandbox  |    +------------------+    |   Downloads      |
| - ChromaDB (CPU) |                            +------------------+
+------------------+
```

### Ubuntu Netplan Configuration (`/etc/netplan/01-sih-lan.yaml`)
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24 # .100 for Server Node, .101 for Admin Node, .102 for User Node
      routes: []           # NO default gateway = strictly offline OS kernel
      nameservers:
        addresses: []     # NO external DNS resolution configured
```

---

## 4. Functional Requirements (MoSCoW Matrix)

* **FR-01 (Must Have): Local Inference Subsystem**  
  Self-hosted model serving via Ollama supporting multiple open-weight models loaded dynamically with sequential memory offloading (`keep_alive: 0`).
* **FR-02 (Must Have): Dynamic Model Router**  
  Heuristic and intent-based routing to direct incoming requests to specialized model capabilities (Code, Vision, Reasoning, General).
* **FR-03 (Must Have): Agentic Execution Engine**  
  LangGraph state machine for multi-step execution, tool selection, cyclic self-healing error recovery, and state persistence.
* **FR-04 (Must Have): Isolated Code Sandbox**  
  Deterministic code execution environment enforced via Linux Bubblewrap (`bwrap --unshare-net`) with sub-5ms launch time, zero network connectivity, 5s execution timeout, and 256MB memory cap.
* **FR-05 (Must Have): Structured Artifact Builder**  
  Dedicated generation modules for `.docx` approval notes with MRPL letterhead/sign-off blocks, `.xlsx` spreadsheets with active formulas, and `.py` source scripts.
* **FR-06 (Must Have): Grounded Local RAG**  
  Vector retrieval store (ChromaDB) with CPU-based ONNX embeddings (`BAAI/bge-small-en-v1.5` via FastEmbed) providing cited answers over ingested MRPL SOPs while reserving 100% of GPU VRAM for LLM inference.
* **FR-07 (Must Have): Multimodal & OCR Engine**  
  Vision-LLM integration (`Qwen2-VL-7B`) and OCR for processing scanned PDFs and P&ID engineering drawings.
* **FR-08 (Should Have): Execution Trace Summary**  
  UI timeline displaying real-time agent steps and thoughts streamed via Server-Sent Events (SSE) without exposing raw internal chain-of-thought tokens.

---

## 5. Non-Functional & Security Requirements

* **NFR-01 (Sovereignty Verification):** 100% execution without external egress; provable via local packet capturing tools (`tcpdump`, `scripts/verify_sovereignty.sh`) on the Admin and Server Nodes.
* **SR-01 (Path & Tool Sandboxing):** Tool access restricted to whitelisted execution functions and bounded directory paths (`data/deliverables/`, `data/uploads/`).
* **SR-02 (Auditability):** Cryptographic append-only SHA-256 block ledger in SQLite (`data/mrpl_audit.db`) recording timestamp, user role, model ID, prompt hash, output hash, tool exit code, and entry hash.

---

## 6. Project Monorepo Structure

```text
SIH/
├── backend/                            # Python FastAPI & LangGraph Engine
│   ├── app/
│   │   ├── api/                        # REST & Streaming SSE Endpoints
│   │   │   ├── chat.py                 # POST /api/chat (SSE event-stream)
│   │   │   ├── health.py               # GET /api/health (Air-gap status)
│   │   │   ├── admin.py                # Model registry & RBAC tiers
│   │   │   ├── files.py                # File upload & deliverable download
│   │   │   └── telemetry.py            # Real-time socket telemetry & audit ledger
│   │   ├── graph/                      # LangGraph State Machine (Dev 1: Rajat)
│   │   │   ├── state.py                # AgentState TypedDict schema
│   │   │   ├── nodes.py                # 8 worker nodes with fallback mocks
│   │   │   ├── edges.py                # Conditional routing & 3-retry cyclic recovery
│   │   │   └── builder.py              # StateGraph assembly & compiler
│   │   ├── sandbox/                    # Isolated Execution Sandbox (Dev 2: Anand)
│   │   │   ├── runner.py               # bwrap --unshare-net execution runner
│   │   │   └── error_parser.py         # Python traceback distillation for self-healing
│   │   ├── compilers/                  # Tangible Deliverable Builders (Dev 2: Anand)
│   │   │   ├── docx_builder.py         # MRPL Approval Note .docx with letterhead
│   │   │   └── xlsx_builder.py         # Cost Matrix .xlsx with active formulas
│   │   ├── rag/                        # Sovereign Knowledge Base (Dev 2: Anand)
│   │   │   ├── ingest.py               # Document chunking & FastEmbed CPU indexing
│   │   │   └── retriever.py            # ChromaDB vector retrieval with citations
│   │   ├── security/                   # Air-Gap Protection & Audit (Dev 2: Anand)
│   │   │   ├── audit_chain.py          # Cryptographic SHA-256 SQLite hash ledger
│   │   │   └── network_monitor.py      # /proc/net/dev socket egress counter
│   │   ├── config.py                   # Central settings & 3-node static IPs
│   │   ├── schemas.py                  # Frozen Pydantic shared interface contract
│   │   └── main.py                     # FastAPI application entry point with CORS
│   ├── tests/                          # Automated Verification Suites
│   │   ├── test_dev1_graph.py          # State machine & cyclic recovery tests
│   │   └── test_dev2_tools.py          # Sandbox, compilers, RAG, and audit tests
│   ├── Dockerfile                      # Server container with bwrap pre-installed
│   ├── docker-compose.yml              # GPU passthrough stack (Ollama + Backend)
│   └── requirements.txt                # Pinned production dependencies
│
├── frontend/                           # Aquanex Air-Gapped Desktop Client (Dev 4: Naveen)
│   ├── index.html                      # Editorial Dark UI (Zero CDNs, 100% local assets)
│   ├── src/                            # Frontend Logic & Styles
│   │   ├── style.css                   # Obsidian/Amber/Cyan refinery design system
│   │   ├── api.js                      # Dual-mode client (Live FastAPI SSE + Offline Mock Engine)
│   │   └── main.js                     # Workspace controller & thought stream renderer
│   ├── src-tauri/                      # Native Rust Desktop Core (Tauri v2)
│   │   ├── src/main.rs                 # Native desktop application entry point
│   │   ├── src/lib.rs                  # OS detection & air-gap verification commands
│   │   ├── tauri.conf.json             # Window constraints & multi-OS bundle targets
│   │   └── Cargo.toml                  # Rust dependencies & memory optimizations
│   ├── public/                         # Brand emblems & icon sets
│   ├── vite.config.js                  # Vite 6 bundler configuration
│   └── package.json                    # Vite + Tauri v2 build scripts
│
├── .github/workflows/                  # Automated CI/CD Workflows
│   └── build-desktop.yml               # Multi-OS Desktop matrix (Windows, Linux, macOS)
│
├── data/                               # Local Storage (Excluded from Git)
│   ├── uploads/                        # Uploaded engineering drawings & logs
│   ├── deliverables/                   # Generated .docx and .xlsx artifacts
│   ├── chromadb/                       # Local vector store persistence
│   └── mrpl_audit.db                   # Immutable cryptographic audit database
│
├── scripts/                            # Operational & Demonstration Tooling
│   ├── setup_lan_nodes.sh              # Ubuntu Netplan static IP configurator
│   ├── start_workbench.sh              # Single-command stack launcher
│   └── verify_sovereignty.sh           # Live tcpdump zero-WAN technical verifier
│
├── RAJAT_SPEC.md                       # Dev 1 Implementation Specification
├── ANAND_SPEC.md                       # Dev 2 Implementation Specification
├── KAUSHAL_SPEC.md                     # Dev 3 Implementation Specification
├── FRONTEND_SPEC.md                    # Dev 4 Handshake Specification
├── DEV4_AGENT_PROMPT.md                # Dev 4 AI Agent Master Prompt & Mock Engine
├── DEV4_AQUANEX_FRONTEND_DESKTOP_REPORT.md # Dev 4 Delivery Report
├── PRESENTATION_MASTER_DOSSIER.md      # SIH 10-slide deck & pitch defense
├── BACKEND_IMPLEMENTATION.md           # Master backend blueprint
└── README.md                           # Hackathon documentation
```

---

## 7. Architecture Decision Records (ADR Log)

* **ADR-001 — Core System Architecture & Inference Stack:**  
  Use Ollama for local LLM serving on `127.0.0.1`, FastAPI for REST/SSE proxy gateway on port `8000`, LangGraph for multi-step agent state machines, and Linux Bubblewrap (`bwrap`) for sub-5ms unprivileged namespace code execution.
* **ADR-002 — Dynamic Model Routing Architecture:**  
  Heuristic and intent-driven router distributing requests across Coder (`Qwen-2.5-Coder-7B`), Vision (`Qwen2-VL-7B`), and General Reasoning (`DeepSeek-R1-8B`) models with dynamic VRAM offloading (`keep_alive: 0`).
* **ADR-003 — Target Industrial Demonstration Scenarios:**  
  Focus on Piping Inspection Processing (CDU-2 Crude Unit), Sandboxed Calculation (API 570 remaining life), P&ID Diagram Parsing, and SOP RAG Search.
* **ADR-004 — MVP Scope Locking (MoSCoW):**  
  Freeze core MVP features to Must-Have functional requirements for the hackathon sprint.
* **ADR-005 — Modular Monorepo Hierarchy:**  
  Standardize on production `backend/app/` package architecture separating graph state machines, sandboxed tools, document compilers, and security monitors.
* **ADR-006 — Physical 3-Node Offline LAN Architecture:**  
  Deploy across three physical Ubuntu laptops connected via an offline Ethernet switch (Server `192.168.1.100`, Admin `192.168.1.101`, User `192.168.1.102`).
* **ADR-007 — Isolated Proxy Gateway & Zero-Gateway Netplan:**  
  Bind inference to loopback (`127.0.0.1`) on Server, proxy via FastAPI gateway on `192.168.1.100:8000`, and strip default routes in Ubuntu Netplan (`routes: []`).
* **ADR-008 — CPU-Offloaded Embeddings for VRAM Conservation:**  
  Run local RAG embeddings via FastEmbed ONNX (`BAAI/bge-small-en-v1.5`) exclusively on the CPU (0 MB GPU VRAM) to leave 100% of GPU memory available for LLM inference on consumer gaming hardware.
* **ADR-009 — Cyclic Self-Healing Error Loop:**  
  Intercept sandbox execution failures, distill Python `stderr` down to offending lines via `error_parser.py`, and automatically cycle back to the reasoning model with a 3-attempt circuit breaker before human escalation.
* **ADR-010 — Aquanex Air-Gapped Desktop Architecture (Tauri v2 + Vite + Zero-CDN CSS):**  
  Package the chemical engineer workbench via Tauri v2 and modern ES Modules with strictly 0 external CDN calls. Embed a dual-mode communication engine in `api.js` allowing instant offline simulation while consuming live Server-Sent Events from `POST /api/chat`, `POST /api/files/upload`, and `GET /api/telemetry/network/stream`. Include multi-OS build matrix via GitHub Actions (`build-desktop.yml`).
