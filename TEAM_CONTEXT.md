# 🛡️ SovereignWorkbench — Team Collaboration & Context Guide
> **Smart India Hackathon (SIH) 2026 | Problem Statement 117 (SIH26117)**  
> **Client / Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL) / MoPNG  
> **Project Name:** `SovereignWorkbench`  
> **Repository Root:** `/home/cyanide/SIH/`  
> **Status:** Backend Engine Fully Implemented, Integrated & Verified (15/15 Tests Passing) — Presentation & Client Phase  

---

## 📌 1. The Big Picture: What Are We Building & Why?

### The Core Problem (The Industrial Deadlock)
Modern oil refineries (like MRPL), defense manufacturers, and Public Sector Undertakings (PSUs) generate massive amounts of confidential, high-stakes technical documentation:
* **Piping & Instrumentation Diagrams (P&IDs)** and isometric engineering drawings.
* **Ultrasonic wall-thickness corrosion reports** and non-destructive testing (NDT) logs.
* **Capital expenditure (Capex) procurement briefs**, executive board approval notes, and compliance audits.

**The Deadlock:** Under Indian statutory data sovereignty rules (MoPNG, OISD, CERT-In), **zero bytes of this proprietary industrial data can touch commercial cloud AI tools** (ChatGPT, Claude, Copilot, etc.). 
* If engineers do it manually, they spend 30–40% of their working hours cross-referencing paper SOPs, calculating pipe remaining life in Excel, and formatting compliance notes.
* If they secretly paste snippets into cloud AI (*Shadow AI*), they commit severe national security and corporate compliance violations.

### Our Solution (`SovereignWorkbench`)
We are building a **100% on-premise, air-gapped Agentic AI Workbench** running entirely on an organization's own local GPU workstation. It:
1. **Parses complex industrial documents** (scanned ultrasonic inspection PDFs and P&ID engineering drawings).
2. **Never does mental math:** Translates engineering formulas (API 570 / ASME) into Python scripts and executes them inside an isolated, non-networked Linux sandbox (`bwrap`).
3. **Features a Self-Healing Recovery Loop:** If a script crashes (e.g., divide-by-zero, missing parameter), the system captures `stderr`, distills the root cause, and auto-corrects the code in up to 3 autonomous retries.
4. **Compiles Real Deliverables:** Outputs corporate `.docx` approval notes with letterhead/formulas and formatted `.xlsx` cost matrices—not just raw chat text.
5. **Enforces a Hardware-Level Air-Gap Kill Switch:** Actively sniffs network routes; if anyone connects an external WAN (mobile hotspot/Wi-Fi), the app instantly locks down with a modal emergency screen.

---

## 🖥️ 2. Physical System Topology: The 3-Laptop Layout

To prove sovereign, air-gapped compliance during the live SIH demo, the system operates across **three separate machines over an isolated local Ethernet switch (no internet cable)**:

```text
                      [OFFLINE PHYSICAL ETHERNET SWITCH / ISOLATED LAN]
                         (Subnet: 192.168.1.0/24 | Default Gateway: NONE)
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │ (192.168.1.100)              │ (192.168.1.101)              │ (192.168.1.102)
          ▼                              ▼                              ▼
┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  NODE 1: GPU SERVER  │    │  NODE 2: ADMIN/AUDIT │    │  NODE 3: USER CLIENT │
│ (Laptop 1: 16GB+ VRAM│    │ (Laptop 2: Standard) │    │ (Laptop 3: Standard) │
│ • FastAPI Gateway:8000    │ • Live Egress Monitor│    │ • Aquanex UI / Tauri │
│ • Ollama (127.0.0.1) │    │ • tcpdump Sniffer    │    │ • Air-Gap Kill Switch│
│ • LangGraph Engine   │    │ • SHA-256 Audit View │    │ • P&ID Viewer & Chat │
│ • Linux bwrap Sandbox│    │ • Security Watchdog  │    │ • Deliverable DL     │
│ • ChromaDB & SQLite  │    └──────────────────────┘    └──────────────────────┘
└──────────────────────┘

### Node Roles & Static IP Matrix (Authoritative Wiki Spec):
* **Node 1: Central GPU Server Workstation (`192.168.1.100:8000`):**
  A high-compute laptop with NVIDIA RTX GPU (6GB–16GB VRAM). Runs:
  * `Ollama` daemon bound strictly to local loopback (`http://127.0.0.1:11434`) per ADR-007 proxy isolation.
  * `FastAPI` gateway listening on `0.0.0.0:8000` (accessible across LAN at `http://192.168.1.100:8000`).
  * `LangGraph` deterministic cyclic state machine.
  * Isolated Linux sandbox (`bwrap`).
  * Local ChromaDB vector store and SQLite cryptographic audit ledger.
  * Embedded Aquanex Web UI served directly from `/` for browser access.
* **Node 2: IT & Security Admin / Audit Console (`192.168.1.101`):**
  A dedicated audit laptop running real-time packet monitoring (`scripts/verify_sovereignty.sh`), `tcpdump` egress sniffer, and inspecting tamper-evident SHA-256 audit ledger records from `http://192.168.1.100:8000/api/telemetry/audit`.
* **Node 3: User Workbench Client (`192.168.1.102`):**
  Standard process engineer laptop running the native cross-platform desktop client (Tauri v2) or browser pointing to `http://192.168.1.100:8000`. Auto-connects to Node 1 via configurable gateway settings.

---

## ⚙️ 3. Core Technical Architecture & Technology Stack

### 3.1 Orchestration: LangGraph (Python)
We use **LangGraph** to build a deterministic, cyclic state machine:
* **Why LangGraph over linear chains?** Because industrial audits require **cycles**. When Python code fails in the sandbox, LangGraph uses conditional edges to route the error back to the code generator for autonomous self-healing.
* **Flow:** `Ingest Document -> Vision OCR Node -> Router Node -> DeepSeek-R1 Math Node -> Sandbox Node -> [Conditional Edge: Success -> Compiler Node | Error -> Self-Healing Node]`.

### 3.2 Local Model Fleet (Served via Ollama)
All models run locally with 4-bit or 8-bit quantization to fit within a single 6GB–12GB VRAM envelope:
| Model Role | Selected Model | Quantization & VRAM | Purpose |
| :--- | :--- | :--- | :--- |
| **Router / Classifier** | `Qwen-2.5-3B-Instruct` | Q8_0 (~3.5 GB) | Classifies intent (SOP lookup vs. P&ID audit vs. code) |
| **Reasoning & Math** | `DeepSeek-R1-Distill-Qwen-8B` | Q4_K_M (~5.4 GB) | Generates API 570 calculation logic & Python scripts |
| **Visual P&ID Inspection** | `Qwen2-VL-7B-Instruct` | Q4_K_M (~5.2 GB) | Reads engineering blueprints, line tags, and valve symbols |
| **Tool Code Generation** | `Qwen-2.5-Coder-7B-Instruct` | Q4_K_M (~4.8 GB) | General automation script writer |

> ⚠️ **VRAM Residency Management:** The GPU server enforces sequential model unloading (`keep_alive: 0` in Ollama) before loading a new model. This ensures peak VRAM never exceeds **5.5 GB**, completely preventing CUDA Out-of-Memory (OOM) crashes.

### 3.3 The Isolated Sandbox (`bwrap` / Bubblewrap)
* Executes model-generated Python code inside an unshared Linux namespace (`bwrap --unshare-net --ro-bind / / ...`).
* **Hard Constraints:** 5-second timeout, 256MB RAM cap, zero network interfaces.
* **Pre-installed Library Whitelist:** `math`, `numpy`, `scipy`, `pandas`, `openpyxl`, `python-docx`.

### 3.4 Deliverable Compiler Engine
* **Executive Word Note:** Generated via `python-docx`. Includes official MRPL letterhead, ultrasonic inspection data table, formula derivation steps, and signatory block.
* **Corrosion & Cost Matrix:** Generated via `openpyxl`. Formatted with active Excel formulas, cell color coding (Green = Safe, Red = Critical Replacement), and replacement cost estimates.

### 3.5 Client Application (Tauri + React)
* Built using **Tauri (Rust + React + Tailwind CSS)** instead of Electron.
* **Benefits:** Installer size is `<15 MB` (vs. Electron's 150MB+), idle RAM is `<40 MB` (vs. Electron's 300MB+), and native file dialogs save deliverables directly to disk.
* **mDNS Auto-Discovery:** Discovers `mrpl-server.local:8000` via Zeroconf/Bonjour automatically on the offline Wi-Fi.

### 3.6 Air-Gap Kill Switch & Telemetry Sniffer
* Background thread in the client polls local network routing tables every 2 seconds.
* **The Kill Switch:** If a gateway to the public internet (4G mobile tethering, corporate WAN) is connected, the app immediately freezes all document access and shows a full-screen red emergency modal:
  `🚨 AIR-GAP VIOLATION: External Internet connection detected. Disconnect to resume.`
* **Zero-Packet Proof:** Server reads `/proc/net/dev` and `/proc/net/tcp` to display a live network HUD proving **0 outbound WAN packets**.

---

## 🎬 4. The 5-Minute SIH Winning Demo Script

This is the exact sequence we will perform in front of the evaluators:

1. **The Setup (30 seconds):**
   * Show evaluator the 3 laptops connected to `MRPL_AIRGAP` (hotspot with mobile data OFF).
   * Show that the WAN cable is physically disconnected. Show the live zero-packet telemetry gauge on Laptop 1.
2. **The Ingestion (1 minute):**
   * On Laptop 3 (Engineer Client), drag and drop `CDU2_Ultrasonic_Inspection_Report.pdf` and `P&ID_Drawing_Line150.png`.
   * Client uploads to Laptop 2 (GPU Server).
3. **The Agentic Execution (1.5 minutes):**
   * `Qwen2-VL` parses the P&ID blueprint -> extracts Line `CDU-2-04-150-A1A` with nominal thickness `4.8 mm` and actual wall thickness `3.2 mm`.
   * Router hands off to `DeepSeek-R1` to compute remaining life via API 570 formulas.
   * **The WOW Factor (Deliberate Self-Healing Error):** The initial script intentionally triggers a missing parameter error -> sandbox intercepts `stderr` -> LangGraph error edge catches it -> re-prompts model with distilled error -> model fixes script on attempt #2!
   * Python executes in sandbox: Computes remaining life = **3.1 years** (Threshold < 5 years triggers mandatory replacement).
4. **Deliverable Export (1 minute):**
   * Click "Generate Approval Dossier".
   * Instantly open `MRPL_Approval_Note.docx` and `Cost_Matrix.xlsx` in LibreOffice/Microsoft Office on Laptop 3.
5. **The Climax: The Live Kill Switch Test (1 minute):**
   * Presenter connects Laptop 3 to a mobile 4G hotspot.
   * **Within 2 seconds, the client screen flashes RED and locks down:** `AIR-GAP VIOLATION DETECTED`.
   * Disconnect mobile hotspot -> screen instantly turns green and unlocks.
   * Evaluators are blown away by true enterprise zero-trust compliance!

---

## 👥 5. Team Roles & Ownership Matrix

| Team Member | Module Ownership | Core Tech Stack | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Rajat (Dev 1: LangGraph & API Lead)** | LangGraph Orchestrator & SSE Streaming | Python, FastAPI, LangGraph, SSE | • LangGraph state graph & conditional edges<br>• Intent routing & self-healing loop<br>• Streaming chat API (`/api/chat`) |
| **Anand (Dev 2: Tools & Security Lead)** | Sandboxing, Self-Healing, Deliverables & Security | Linux `bwrap`, `python-docx`, `openpyxl`, ChromaDB | • Secure Bubblewrap sandbox runner<br>• Error distillation parser<br>• Word & Excel deliverable compilers<br>• CPU Sovereign RAG & SHA-256 audit |
| **Kaushal (Dev 3: Model & GPU Lead)** | Ollama GPU Server, GGUF Models & VRAM | Ollama API, GGUF Quantization, NVIDIA CUDA | • Local Ollama daemon configuration<br>• Model weight ingestion & quantization<br>• Sequential VRAM offloader (`keep_alive: 0`)<br>• Async `call_llm` model gateway |
| **Naveen (Dev 4 — Frontend & Desktop Lead)** | Aquanex Air-Gapped UI & Cross-Platform Desktop | Tauri v2 (Rust), Vite 6, Modern ES Modules, Vanilla CSS | • Aquanex refinery dark workspace (`frontend/`)<br>• Zero-CDN air-gapped architecture<br>• Native desktop client (Windows, Linux, macOS)<br>• Multi-OS GitHub Actions workflow (`build-desktop.yml`) |
| **QA, Pitch & Demo Lead** | Integration, Synthetic Data & Presentation | Hardware rig, PPT deck, Test scenarios | • 3-laptop network setup & hotspot routing<br>• Synthetic inspection PDFs & P&ID mockups<br>• Presentation deck & demo choreography |

---

## 🚀 6. Local Development Setup (Day 1 Checklist)

### 6.1 Prerequisites to Install on Your Machine
* **Python:** Version 3.11 or 3.12 (`python3 --version`)
* **Node.js & npm:** Node v20+ (`node -v`)
* **Ollama:** Installed locally ([ollama.com](https://ollama.com))
* **Linux / WSL2 Tools:** `bubblewrap` (`sudo apt install bubblewrap` for sandboxing)
* **Rust (Only for Frontend Lead):** `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

### 6.2 Pulling the Required Models (Run in Terminal)
```bash
# 1. Router Model (Fast, low memory)
ollama pull qwen2.5:3b-instruct-q8_0

# 2. Reasoning & Math Engine
ollama pull deepseek-r1:8b

# 3. Vision & Blueprint Reader
ollama pull qwen2-vl:7b-instruct-q4_K_M

# 4. Coding Specialist
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
```

### 6.3 Standard Repository Structure
```
SIH/
├── PRD.md                           # Master Product Requirements Document
├── TEAM_CONTEXT.md                  # This file (Team Onboarding Guide)
├── README.md                        # High-level repo overview
├── backend/                         # Node 2: FastAPI + LangGraph Server
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point & REST endpoints
│   │   ├── graph/                   # LangGraph StateGraph definitions
│   │   │   ├── state.py             # AgentState TypedDict
│   │   │   ├── nodes.py             # Vision, Math, Sandbox, Compiler nodes
│   │   │   └── router.py            # Conditional routing & retry edges
│   │   ├── sandbox/                 # Bubblewrap runner & error distillation
│   │   │   ├── runner.py            # bwrap execution wrapper
│   │   │   └── error_parser.py      # Traceback cleaner for self-healing
│   │   ├── compilers/               # Word & Excel deliverable builders
│   │   │   ├── docx_builder.py      # python-docx template engine
│   │   │   └── xlsx_builder.py      # openpyxl cost matrix generator
│   │   ├── rag/                     # CPU-based local document store
│   │   │   └── vector_store.py      # ChromaDB + bge-small-en-v1.5
│   │   └── security/                # Socket sniffer & SHA-256 audit logger
│   │       ├── network_monitor.py   # /proc/net/tcp monitor
│   │       └── audit_chain.py       # SQLite hash chain logger
│   └── requirements.txt
├── frontend/                        # Node 3: Tauri Desktop Client
│   ├── src-tauri/                   # Rust backend (mDNS + Kill Switch listener)
│   └── src/                         # React UI (Dashboard, P&ID viewer, HUD)
└── test_assets/                     # Demo test files
    ├── CDU2_Inspection_Report.pdf   # Mock ultrasonic wall-thickness report
    └── P&ID_Line150_Blueprint.png   # Mock refinery piping schematic
```

---

## 📖 7. Industrial Jargon Cheat Sheet (Know What to Say to Judges!)

* **P&ID (Piping & Instrumentation Diagram):** The definitive technical schematic used in refineries showing pipes, valves, instruments, and pumps with standardized tagging (e.g., `CDU-2-04-150-A1A`).
* **API 570:** The standard published by the American Petroleum Institute governing inspection, repair, alteration, and rerating of in-service piping systems.
* **CDU (Crude Distillation Unit):** The primary fractional distillation column in an oil refinery where crude oil is split into petrol, diesel, kerosene, and naphtha.
* **Ultrasonic Thickness Gauging (UTG):** A non-destructive test where high-frequency sound waves measure remaining metal pipe wall thickness without cutting the pipe.
* **Air-Gap:** A physical security measure where computers are completely disconnected from the internet and external networks.
* **Dynamic Model Swapping:** Loading a 7B model into GPU memory for task A, then explicitly unloading it to 0 MB before loading task B, allowing multiple models to run on a budget single-GPU laptop.

---

## 🎯 8. Team Implementation Status & Next Milestones
1. **Rajat (Dev 1 — Agentic Brain & Streaming API):**
   * `app/graph/state.py`, `nodes.py`, `edges.py`, `builder.py` (**COMPLETED & TESTED ✅**)
   * `app/api/chat.py` (SSE streaming & sync), `health.py`, `admin.py`, `main.py` (**COMPLETED & TESTED ✅**)
2. **Anand (Dev 2 — Tools, Sandbox, Deliverables & Security):**
   * `app/sandbox/runner.py` (Linux `bwrap`), `error_parser.py` (**COMPLETED & MERGED ✅**)
   * `app/compilers/docx_builder.py`, `xlsx_builder.py` (**COMPLETED & MERGED ✅**)
   * `app/rag/ingest.py`, `retriever.py` (ChromaDB + CPU FastEmbed) (**COMPLETED & MERGED ✅**)
   * `app/security/audit_chain.py` (SHA-256 ledger), `network_monitor.py` (**COMPLETED & MERGED ✅**)
   * `app/api/files.py`, `app/api/telemetry.py` (**COMPLETED & MERGED ✅**)
3. **Naveen (Dev 4 — Frontend & Desktop Lead):**
   * Aquanex air-gapped UI in `frontend/` with zero CDN dependencies (**COMPLETED & MERGED ✅**)
   * Native cross-platform desktop shell in `frontend/src-tauri/` (Windows, Linux, macOS) (**COMPLETED & MERGED ✅**)
   * Dual-mode API client (`frontend/src/api.js`) consuming live SSE streams + offline simulation (**COMPLETED & MERGED ✅**)
   * Multi-OS automated CI/CD workflow in `.github/workflows/build-desktop.yml` (**COMPLETED & MERGED ✅**)
4. **Automated Testing & Integration:**
   * Full unit test suite (`pytest`): **15 out of 15 tests passing** (**COMPLETED ✅**)
   * End-to-end industrial audit simulation (`test_e2e_simulation.py`): **COMPLETED ✅** (Generates real 38KB Word Approval Note and 6KB Excel Cost Matrix on disk).
   * Frontend production build (`vite build`): **100% SUCCESSFUL (155ms) ✅**
5. **Immediate Next Steps:**
   * Rehearse pitch deck and demo choreography per [`PRESENTATION_MASTER_DOSSIER.md`](PRESENTATION_MASTER_DOSSIER.md).
   * Final live dry-run connecting Aquanex desktop client to local FastAPI backend on `http://127.0.0.1:8000`.
