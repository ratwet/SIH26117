# 🛡️ SovereignWorkbench (Aquanex)

> **Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work**  
> **Problem Statement ID:** SIH26117 | **Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL / ONGC)  
> **Theme:** Smart Automation | **Category:** Software | **Status:** Production Delivery Ready (40/40 Tests Passing)

---

## 📌 Executive Summary

Modern process refineries such as **Mangalore Refinery and Petrochemicals Limited (MRPL)** manage highly confidential engineering infrastructure, statutory inspection logs, and critical piping schematics (P&IDs). Sending these artifacts to commercial public cloud APIs (e.g. OpenAI, Anthropic, Gemini) violates national cybersecurity directives and creates severe data exfiltration risks.

**SovereignWorkbench (Aquanex)** solves this dilemma. It is a **100% self-hosted, air-gapped, agentic AI platform** powered entirely by open-weight foundation models. It automates complex engineering calculations (API 570 Remaining Safe Life, ASME B31.3 Minimum Wall Thickness), performs high-density OCR on piping drawings, self-heals Python calculation errors inside an isolated Linux sandbox, and autonomously compiles a **10-deliverable omni-modal publication suite**—with **verifiable zero outbound WAN bytes**.

---

## ⚡ Key Capabilities & Engineering Pillars

### 1. Modern Conversational Interface (Gemini & Claude Style)
- **Minimalist Dark Theme:** Sleek, high-performance interface with zero third-party CDN dependencies.
- **Collapsible Reasoning Drawer:** LangGraph cyclic state machine node transitions and DeepSeek-R1 reasoning steps are presented in a clean, collapsible thought drawer (`<details class="thought-drawer">`) with an animated pulse dot.
- **Floating Pill Input Bar:** Centered floating container with auto-expanding textarea, industrial artifact attachment support, and circular send button.
- **Real Session Management:** Real `localStorage`-backed conversation management (`+ New chat`, persistent history, delete on hover), with zero fake dummy items.
- **Artifacts on Demand:** Download chips for generated deliverables render only when actual files are compiled.

### 2. Strict Air-Gap Hardware/Kernel Isolation & Reactive Kill Switch
- **Active WAN Reachability Probe:** Active non-blocking socket probes in `network_monitor.py` distinguish clean, offline local Wi-Fi router connectivity (e.g. wirelessly connecting to an on-premise GPU server) from true public Internet backhaul.
- **Reactive Defense-in-Depth:** Kernel `/proc/net/route` and interface delta monitoring stream real-time telemetry via Server-Sent Events (`/api/telemetry/network/stream`).
- **Instant Lockdown:** If public Internet connectivity is detected:
  - Top indicator turns red: `🔴 Internet Detected (Locked)`.
  - Full-screen high-priority alert appears: `🚨 Air-Gap Security Alert: Internet Detected`.
  - All chat inputs and operations are frozen (`HTTP 403 Forbidden`).
- **Autonomous Recovery:** Disconnecting from public Wi-Fi or activating Airplane Mode automatically dismisses the lockdown modal within 1.5 seconds and restores operations without manual intervention.

### 3. Strict No-Model Fail-Fast (Zero Fake Emulation)
- **Zero Simulation / Emulation Fallbacks:** Silent mock responses are completely eradicated from both backend and frontend.
- **Scalable Architecture:** A unified multi-endpoint gateway in `app/llm/engine.py` seamlessly supports:
  - **Laptop / Edge Rig:** Local Ollama (`http://127.0.0.1:11434`) running 3B/8B models (e.g. `qwen2.5:3b`, `deepseek-r1:8b`).
  - **Enterprise Datacenter Cluster:** High-throughput vLLM OpenAI-compatible endpoint (`http://127.0.0.1:8001/v1`) serving 70B/100B+ models (e.g. `qwen2.5:72b`, `deepseek-r1:70b`).
- **Fail-Fast Integrity:** When offline with no model running, the system returns a clean `503 Service Unavailable` and displays an informative assistance card rather than hallucinating fake inspection data.

### 4. 10-Deliverable Omni-Modal Generation Suite
The system autonomously compiles a full suite of statutory inspection deliverables into `backend/data/deliverables/`:
1. **`Inspection_Certificate.pdf`** — Formal statutory certificate with digital signatures and QR verification.
2. **`Approval_Note.docx`** — Formal executive note styled with corporate MRPL typography.
3. **`Cost_Matrix.xlsx`** — Multi-tab Capex procurement matrix with dynamic API 570 risk badges (`MANDATORY REPLACEMENT REQUIRED` vs. `IN-SERVICE MONITORING ACCEPTABLE`).
4. **`Executive_Pitch_Deck.pptx`** — Board-level presentation deck.
5. **`Piping_Spool.dxf`** — Production AutoCAD DXF drawing with dimensioned spool layout.
6. **`Piping_Spool_3D.stl`** — 3D printable manifold CAD mesh.
7. **`Inspection_Heatmap.png`** — Visual P&ID schematic with corrosion severity color scale.
8. **`UT_Thickness_Survey.csv`** — Ultrasonic thickness inspection log with CML tags.
9. **`API570_Calculation.py`** — Standalone reproducible math verification script.
10. **`Audit_Manifest.json`** — Cryptographic manifest with SHA-256 hashes of all artifacts.

### 5. Deterministic Linux Sandbox & Self-Healing Loop
- **Bubblewrap (`bwrap`) Isolation:** Sandboxed Python code execution with strict read-only system mounts (`/usr`, `/lib`, `/bin`, `sys.prefix`), dedicated tmpfs, and Linux kernel memory ceilings (`RLIMIT_AS`).
- **Cyclic Self-Healing Engine:** If generated code produces an exception (e.g. `ZeroDivisionError` or syntax flaw), the sandbox captures stderr, distills the traceback, and feeds it back into the reasoning model for up to 3 autonomous correction cycles.

### 6. Sovereign RAG Vector Store
- **100% Local Embeddings:** Utilizes FastEmbed (`bge-small-en-v1.5`) and ChromaDB vector storage running entirely on CPU/GPU without cloud calls.
- **Authoritative Engineering Standards:** Ingests plant SOPs, OISD-STD-118, and API 570 inspection documents.
- **SOP Grounded Routing:** Queries regarding refinery standards and procedures are directly routed to cited, clause-referenced conversational answers.

### 7. Native Linux Desktop Application (Fedora / GNOME / KDE)
- **GTK 3.0 + WebKit2 Client:** Standalone desktop runner (`scripts/run_linux_desktop.py`) with hardware acceleration.
- **Desktop Entry Installer:** Automated script (`scripts/install_desktop_entry.sh`) registers `aquanex.desktop` into the Linux GNOME/KDE App Drawer with high-res iconography.

---

## 🏛️ Physical 3-Node Offline LAN Architecture

```
                                  [ ISOLATED LOCAL SWITCH / ROUTER ]
                                  (Subnet: 192.168.1.0/24 - ZERO WAN)
                                                   |
         +-----------------------------------------+-----------------------------------------+
         |                                         |                                         |
         v                                         v                                         v
   +-----------------------+                 +-----------------------+                 +-----------------------+
   |   NODE 1: SERVER      |                 |   NODE 2: ADMIN       |                 |   NODE 3: WORKBENCH   |
   |   192.168.1.100:8000  |                 |   192.168.1.101       |                 |   192.168.1.102       |
   +-----------------------+                 +-----------------------+                 +-----------------------+
   | • FastAPI Backend     |                 | • Cryptographic Audit |                 | • Aquanex UI (Desktop)|
   | • LangGraph State     |                 | • Tamper Ledger HUD   |                 | • WebKit2 / GTK 3.0   |
   | • bwrap Sandbox       |                 | • Kill-Switch Sim     |                 | • Engineer Chat Feed  |
   | • ChromaDB RAG        |                 | • Admin Oversight     |                 | • Artifact Downloader |
   | • Ollama / vLLM Models|                 |                       |                 |                       |
   +-----------------------+                 +-----------------------+                 +-----------------------+
```

---

## 📂 Repository Structure

```text
SIH/
├── README.md                      # Authoritative project overview & execution guide
├── LICENSE.md                     # License information
├── PROBLEM_STATEMENT_117.md       # Master MRPL problem statement specification
├── PRD.md                         # Product Requirements Document (Functional & Non-Functional)
├── TEAM_CONTEXT.md                # 3-node physical setup & presentation reference
├── aquanex.desktop                # FreeDesktop GNOME/KDE application launcher entry
├── backend/                       # Python 3.10+ FastAPI on-premise backend
│   ├── app/
│   │   ├── api/                   # REST & SSE streaming routers (chat, telemetry, files, admin)
│   │   ├── compilers/             # 10-deliverable omni-modal compilers (PDF, DOCX, XLSX, CAD, etc.)
│   │   ├── graph/                 # LangGraph cyclic state machine, nodes, and self-healing edges
│   │   ├── llm/                   # Unified 100B/8B model gateway (vLLM & Ollama)
│   │   ├── rag/                   # Sovereign RAG engine (FastEmbed + ChromaDB)
│   │   ├── sandbox/               # Bubblewrap hardened Linux sandbox & error parser
│   │   ├── security/              # Active socket network monitor & SHA-256 audit ledger
│   │   ├── config.py              # Centralized Pydantic application settings
│   │   └── main.py                # FastAPI lifecycle, CORS, and SPA static mount
│   ├── tests/                     # Comprehensive test suite (40/40 tests passing)
│   ├── Dockerfile                 # Multi-stage production container
│   ├── docker-compose.yml         # Multi-node compose specification
│   └── requirements.txt           # Pinned production dependencies
├── frontend/                      # Aquanex Modern Conversational Client
│   ├── src/
│   │   ├── api.js                 # Zero-mock API client & SSE streaming parser
│   │   ├── main.js                # Gemini/Claude conversational logic & session manager
│   │   ├── markdown.js            # Safe, lightweight Markdown to HTML renderer
│   │   └── style.css              # Editorial dark mode design system
│   ├── index.html                 # Semantic HTML5 single-page application
│   ├── package.json               # Vite build configuration
│   └── src-tauri/                 # Tauri v2 cross-platform native wrapper (Linux/macOS/Windows)
├── scripts/                       # Deployment, networking & verification tooling
│   ├── install_desktop_entry.sh   # Registers Aquanex in Linux App Drawer
│   ├── launch_aquanex.sh          # Native desktop launcher script
│   ├── run_linux_desktop.py       # Standalone GTK 3.0 + WebKit2 runner
│   ├── setup_lan_nodes.sh         # Offline 3-node Netplan network configuration
│   ├── start_workbench.sh         # Starts background backend & server daemon
│   └── verify_sovereignty.sh      # Zero-egress network verification sniffer
└── docs/                          # Presentation & architectural diagrams
    ├── presentation/              # SIH pitch dossier & presentation deck
    └── diagrams/                  # High-res SVG architecture & process flow diagrams
```

---

## 🚀 Quickstart & Execution Guide

### 1. Prerequisites
- **Operating System:** Linux (Fedora 38+, Ubuntu 22.04+, or RHEL 9+)
- **Python:** 3.10+ (Recommended: active virtualenv)
- **Node.js:** v18+ & npm
- **System Packages:** `bubblewrap`, `libwebkit2gtk-4.1`, `gir1.2-gtk-3.0`

### 2. Environment Setup
```bash
# Clone the repository and navigate to root
git clone https://github.com/ratwet/SIH26117.git
cd SIH26117

# Create and activate Python virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install backend dependencies
python -m pip install -r backend/requirements.txt
```

### 3. Build Desktop Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Start Sovereign Backend Server
```bash
# Option A: Using the automated start script
bash scripts/start_workbench.sh

# Option B: Direct uvicorn launch
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Launch Native Desktop Client
```bash
# Install to Linux App Drawer (GNOME / KDE)
bash scripts/install_desktop_entry.sh

# Launch directly via script
bash scripts/launch_aquanex.sh
```

---

## 🧪 Automated Testing & Verification

The test suite thoroughly validates sandbox security, graph routing, omni-modal compilers, RAG retrieval, and air-gap network enforcement.

```bash
# Run all 40 unit and integration tests
PYTHONPATH=backend python -m pytest backend/tests/ -v
```

### Test Suite Summary:
- **`backend/tests/test_audit_fixes.py`**: Validates 14 audit remediations (sandbox mounts, RAG grounding, RBAC authorization, CORS limits).
- **`backend/tests/test_dev1_graph.py`**: Validates LangGraph state machine node transitions and streaming contracts.
- **`backend/tests/test_dev2_tools.py`**: Validates Bubblewrap execution, error parsing, and deliverable builders.
- **`backend/tests/test_omni_modal_100b.py`**: Validates 10-deliverable compilation, multi-tier scaling, no-model fail-fast (503), and Internet rejection (403).
- **Result:** `40 passed in 5.33s (100% pass rate)`

---

## 👥 Team Ownership & Role Handshake

| Member | Role | Key Contributions |
| :--- | :--- | :--- |
| **Rajat** | Dev 1: Orchestration & API Lead | LangGraph cyclic self-healing state machine, SSE chat streaming API, 100B fail-fast gateway |
| **Anand** | Dev 2: Deterministic Tools Lead | Bubblewrap sandbox, 10-deliverable omni-modal compilers, Sovereign RAG retriever |
| **Kaushal** | Dev 3: GPU & Deployment Lead | Ollama & vLLM cluster integration, hardware-agnostic multi-tier model configuration |
| **Naveen** | Dev 4: Frontend & Desktop Lead | Gemini/Claude conversational UI, GTK 3.0 desktop client, Air-Gap reactive lockdown system |

---

## 📜 License & Intellectual Property
Proprietary implementation developed for **Smart India Hackathon 2026** (Problem Statement SIH26117) under the mandate of **Mangalore Refinery and Petrochemicals Limited (MRPL)**. All rights reserved.
