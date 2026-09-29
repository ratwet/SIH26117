# 🛡️ SovereignWorkbench (Aquanex)

> **Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work**  
> **Problem Statement ID:** SIH26117 (PS 117) | **Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL / ONGC)  
> **Theme:** Smart Automation | **Category:** Software | **Status:** Production Delivery Ready (**58/58 Tests Passing — 100%**)  
> 📖 **Documentation Wiki:** [docs/wiki/Home.md](docs/wiki/Home.md) | 📐 **Technical Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md) | 🎯 **Q&A Defense Guide:** [docs/guides/PROJECT_QNA_GUIDE.md](docs/guides/PROJECT_QNA_GUIDE.md)

---

## 📌 Executive Summary

Modern process refineries such as **Mangalore Refinery and Petrochemicals Limited (MRPL)** manage highly confidential engineering infrastructure, statutory inspection logs, and critical piping schematics (P&IDs). Sending these artifacts to commercial public cloud APIs (e.g. OpenAI, Anthropic, Gemini) violates national critical infrastructure directives (NCIIPC, MoPNG Hydrocarbon Cyber Security Framework, CERT-In Section 70B) and risks intellectual property exfiltration.

**SovereignWorkbench (Aquanex)** solves this trilemma. It is a **100% self-hosted, air-gapped, agentic AI platform** powered entirely by open-weight foundation models. It automates complex engineering calculations (API 570 Remaining Safe Life, ASME B31.3 Minimum Wall Thickness), performs high-density extraction on piping drawings, executes math formulas deterministically inside an isolated Linux sandbox, logs every action into an immutable SHA-256 blockchain audit ledger, and autonomously compiles a **10-deliverable omni-modal publication suite**—with **verifiable zero outbound WAN bytes**.

---

## ⚡ Core Architecture & Capabilities

### 1. Three Standalone Dedicated Industrial Personas
- **👷 Field Engineer Client:** Minimalist, pitch-black chat interface for field technicians. Supports one-tap formula verification, quick ultrasonic thickness (UT) logging, and instant remaining life estimation.
- **👨‍💼 Senior Reliability Lead Client:** Comprehensive technical dossier builder. Generates executive approval notes, Capex cost procurement workbooks, board presentation decks, 2D AutoCAD spools, and 3D printable manifold meshes.
- **🛡️ Admin Sovereign Control Center:** Complete IT governance dashboard displaying real-time 3-node physical LAN topology, active model GPU VRAM allocation, live cryptographic SHA-256 block ledger, and hardware air-gap kill-switch controls.

### 2. Strict Air-Gap Hardware/Kernel Isolation & Reactive Kill-Switch
- **Active WAN Reachability Probing:** Non-blocking kernel socket telemetry distinguishes clean local offline Wi-Fi router links (connecting laptops to the on-premise GPU server) from true public Internet backhaul.
- **Zero-Tolerance Lockdown:** If outbound WAN packets or public routes are detected during strict air-gap operation:
  - Global status indicator locks to `🔴 Internet Detected (Locked)`.
  - Operations freeze immediately with `HTTP 403 Forbidden`.
  - Real-time SSE streaming alerts all connected clients.
- **Autonomous Recovery:** Disconnecting from public WAN restores operations within 1.5 seconds without manual service restart.

### 3. Distributed On-Premise GPU Offloading (No Emulation)
- **Zero Mock Fallbacks:** Simulation fallbacks are completely eliminated. Every calculation and token stream is verified against active open-weight models (`ALLOW_EMULATION=false`).
- **Flexible Deployment Tiers:**
  - **Edge / Field Laptop:** Local Ollama running lightweight models (`qwen2.5:3b`, `qwen2.5-coder:1.5b`).
  - **Departmental Workstation:** Single NVIDIA RTX 3060/4060/4090 GPU node serving reasoning models.
  - **Enterprise Refinery Datacenter:** Multi-GPU vLLM cluster serving 70B+ models (`qwen2.5:72b`, `deepseek-r1:70b`).

### 4. 10-Deliverable Omni-Modal Generation Suite
The system autonomously compiles a full suite of statutory inspection deliverables into `data/deliverables/`:
1. **`Inspection_Certificate.pdf`** — Statutory inspection certificate with QR verification.
2. **`Approval_Note.docx`** — Formal executive approval note styled with corporate MRPL typography.
3. **`Cost_Matrix.xlsx`** — Multi-tab Capex procurement matrix with dynamic API 570 risk badges (`MANDATORY REPLACEMENT REQUIRED` vs. `IN-SERVICE MONITORING ACCEPTABLE`).
4. **`Executive_Pitch_Deck.pptx`** — Board-level presentation deck.
5. **`Piping_Spool.dxf`** — Production AutoCAD DXF drawing with dimensioned spool layout.
6. **`Piping_Spool_3D.stl`** — 3D printable manifold CAD mesh.
7. **`Inspection_Heatmap.png`** — Visual P&ID schematic with corrosion severity color scale.
8. **`UT_Thickness_Survey.csv`** — Ultrasonic thickness inspection log with CML tags.
9. **`API570_Calculation.py`** — Standalone reproducible math verification script.
10. **`Audit_Manifest.json`** — Cryptographic manifest with SHA-256 hashes of all artifacts.

### 5. Deterministic Linux Sandbox & Self-Healing Execution
- **Bubblewrap (`bwrap`) Isolation:** Sandboxed Python code execution with strict read-only system mounts (`/usr`, `/lib`, `/bin`), isolated tmpfs, and Linux kernel memory ceilings (`RLIMIT_AS`).
- **Cyclic Self-Healing Engine:** If generated code produces an exception, the sandbox captures stderr, distills the traceback, and feeds it back into the reasoning model for up to 3 autonomous correction cycles.

### 6. Cryptographic SHA-256 Audit Blockchain
- Every prompt, model output, sandbox exit code, and deliverable hash is committed to an immutable append-only SQLite ledger (`data/mrpl_audit.db`).
- Blocks are cryptographically linked using SHA-256 hashes (`previous_hash` + `current_hash`). Chain integrity can be verified on-demand with one click.

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
   | • FastAPI Backend     |                 | • Cryptographic Audit |                 | • Standalone Web Apps |
   | • LangGraph State     |                 | • Tamper Ledger HUD   |                 | • Native WebKit2 / GTK|
   | • bwrap Sandbox       |                 | • Kill-Switch Sim     |                 | • Field Engineer Chat |
   | • ChromaDB RAG        |                 | • Node Status Monitor |                 | • Senior Lead Dossier |
   | • Ollama / vLLM Models|                 |                       |                 |                       |
   +-----------------------+                 +-----------------------+                 +-----------------------+
```

---

## 📂 Repository Structure

```text
SIH/
├── README.md                      # Primary project overview & evaluator guide
├── ARCHITECTURE.md                # Principal Systems & AI Technical Architecture Specification
├── PRD.md                         # Product Requirements Document (Functional & Non-Functional)
├── LICENSE.md                     # MIT License
├── .env.example                   # Clean template for environment configuration
├── .gitignore                     # Exhaustive rules for zero-leakage development
├── backend/                       # Python 3.10+ FastAPI on-premise backend
│   ├── app/
│   │   ├── api/                   # REST & SSE streaming routers (chat, telemetry, files, admin)
│   │   ├── compilers/             # 10-deliverable omni-modal compilers (PDF, DOCX, XLSX, CAD, etc.)
│   │   ├── connectors/            # CoWork scoped vaults and email connector
│   │   ├── graph/                 # LangGraph cyclic state machine, nodes, and self-healing edges
│   │   ├── llm/                   # Unified 100B/8B model gateway with auto-discovery
│   │   ├── policy/                # HMAC-SHA256 time-bounded cryptographic approval tokens
│   │   ├── rag/                   # Sovereign RAG engine (FastEmbed + ChromaDB)
│   │   ├── sandbox/               # Bubblewrap hardened Linux sandbox & error parser
│   │   ├── security/              # Active socket network monitor & SHA-256 audit ledger
│   │   ├── config.py              # Centralized Pydantic application settings
│   │   ├── schemas.py             # Shared Pydantic data models
│   │   └── main.py                # FastAPI lifecycle, CORS, and SPA static mount
│   ├── tests/                     # Comprehensive test suite (58/58 tests passing)
│   ├── Dockerfile                 # Multi-stage production container
│   ├── docker-compose.yml         # Multi-node compose specification
│   └── requirements.txt           # Pinned production dependencies
├── frontend/                      # Aquanex Modern Conversational Client (Vite / Vanilla JS)
│   ├── src/
│   │   ├── api.js                 # Zero-mock API client & SSE streaming parser
│   │   ├── main.js                # Three standalone apps, state engine, and formula workbench
│   │   ├── markdown.js            # Safe, lightweight Markdown renderer
│   │   └── style.css              # Editorial pitch-black OLED design system
│   ├── index.html                 # Semantic HTML5 single-page application
│   ├── package.json               # Vite build configuration
│   └── src-tauri/                 # Tauri v2 cross-platform native wrapper (Linux/macOS/Windows)
├── deploy/                        # Linux packaging & deployment
│   └── desktop/                   # FreeDesktop GNOME/KDE launcher entries (.desktop)
├── docs/                          # Exhaustive Technical Documentation
│   ├── diagrams/                  # High-res SVG architecture & process flow diagrams
│   ├── specs/                     # Master problem statement, team context, and design specs
│   ├── benchmarks/                # Statutory, technical & empirical verification dossier
│   ├── guides/                    # Q&A defense guide, setup manuals, and knowledge transfer
│   ├── research/                  # Peer-level research report & regulatory analysis
│   └── wiki/                      # GitHub Wiki documentation pages
└── scripts/                       # Deployment, networking & desktop launcher tooling
    ├── install_desktop_entry.sh   # Registers Aquanex in Linux App Drawer
    ├── install_linux_apps.sh      # Installs all 3 persona apps into Linux desktop
    ├── launch_admin.sh            # Launch Admin Control Center
    ├── launch_senior.sh           # Launch Senior Lead App
    ├── launch_junior.sh           # Launch Field Engineer App
    ├── run_linux_desktop.py       # Standalone GTK 3.0 + WebKit2 runner
    ├── setup_lan_nodes.sh         # Offline 3-node Netplan network configuration
    ├── start_workbench.sh         # Starts background backend & server daemon
    └── verify_sovereignty.sh      # Zero-egress network verification sniffer
```

---

## 🚀 Quickstart & Execution Guide

### 1. Prerequisites
- **Operating System:** Linux (Fedora 38+, Ubuntu 22.04+, or RHEL 9+) / macOS
- **Python:** 3.10+ (Recommended: Python 3.11 or 3.12 in a virtualenv)
- **Node.js:** v18+ & npm
- **Inference Engine:** [Ollama](https://ollama.ai) or [vLLM](https://vllm.ai) running locally or on an on-premise GPU workstation.

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/ratwet/SIH26117.git
cd SIH26117

# Create and activate Python virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Build Frontend Assets
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Start Sovereign Backend Server
```bash
# Direct uvicorn launch
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Access the Standalone Applications
Once the server is running, navigate to:
- **👷 Field Engineer Client:** `http://localhost:8000/?persona=junior&standalone=1`
- **👨‍💼 Senior Reliability Lead:** `http://localhost:8000/?persona=senior&standalone=1`
- **🛡️ Admin Control Center:** `http://localhost:8000/?persona=admin&standalone=1`

Or launch them as native Linux desktop windows:
```bash
python3 scripts/run_linux_desktop.py --persona junior
python3 scripts/run_linux_desktop.py --persona senior
python3 scripts/run_linux_desktop.py --persona admin
```

---

## 🧪 Automated Testing & Verification

The test suite validates sandbox isolation, graph routing, omni-modal compilers, RAG retrieval, and air-gap network enforcement.

```bash
# Run all 58 unit and integration tests
PYTHONPATH=backend python -m pytest backend/tests/ -v
```

### Test Suite Summary:
- **`backend/tests/test_audit_fixes.py`**: Validates 14 audit remediations (sandbox mounts, RAG grounding, RBAC authorization, CORS limits).
- **`backend/tests/test_dev1_graph.py`**: Validates LangGraph state machine node transitions and streaming contracts.
- **`backend/tests/test_dev2_tools.py`**: Validates Bubblewrap execution, error parsing, and deliverable builders.
- **`backend/tests/test_omni_modal_100b.py`**: Validates 10-deliverable compilation, multi-tier scaling, no-model fail-fast (503), and Internet rejection (403).
- **`backend/tests/test_sovereign_hardened.py`**: Validates air-gap kill-switch, HMAC approval tokens, scoped vaults, and cryptographic ledger chaining.
- **Result:** `58 passed in 3.73s (100% pass rate)`

---

## 👥 Team Ownership & Role Handshake

| Member | Role | Key Contributions |
| :--- | :--- | :--- |
| **Rajat** | Dev 1: Orchestration & API Lead | LangGraph cyclic self-healing state machine, SSE chat streaming API, 100B fail-fast gateway |
| **Anand** | Dev 2: Deterministic Tools Lead | Bubblewrap sandbox, 10-deliverable omni-modal compilers, Sovereign RAG retriever |
| **Kaushal** | Dev 3: GPU & Deployment Lead | Ollama & vLLM cluster integration, hardware-agnostic multi-tier model configuration |
| **Naveen** | Dev 4: Frontend & Desktop Lead | Pitch-black OLED UI, 3 standalone persona apps, GTK 3.0 desktop client, Air-Gap reactive lockdown system |

---

## 📜 License & Intellectual Property
Proprietary implementation developed for **Smart India Hackathon 2026** (Problem Statement SIH26117) under the mandate of **Mangalore Refinery and Petrochemicals Limited (MRPL)**. Released under the MIT License.
