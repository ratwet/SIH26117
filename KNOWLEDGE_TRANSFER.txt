================================================================================
AQUANEX SOVEREIGN AI WORKBENCH — TEAM ONBOARDING & KNOWLEDGE TRANSFER (KT)
================================================================================
Document Version : 2.4.0 (Hardened Sovereign Release)
Classification   : INTERNAL // MRPL REFINERY ASSET INTEGRITY TEAM
Target Audience  : New Software Engineers, AI/ML Engineers & Systems Leads
Date Created     : September 2026
================================================================================

TABLE OF CONTENTS:
--------------------------------------------------------------------------------
1. EXECUTIVE SUMMARY & PROJECT MISSION
2. CORE ARCHITECTURAL INVARIANTS (THE NON-NEGOTIABLES)
3. TECHNOLOGY STACK OVERVIEW
4. SYSTEM ARCHITECTURE & DATA FLOW
5. PERSONA & PERMISSION MODEL (RBAC & ABAC)
6. REPOSITORY STRUCTURE & CODE DIRECTORY MAP
7. THE OMNI-MODAL COMPILER PIPELINE
8. COWORK ACTION GATING & CRYPTOGRAPHIC TOKENS
9. LOCAL ENVIRONMENT SETUP & RUNNING THE APP
10. RUNNING AUTOMATED TESTS & VERIFICATION
11. KNOWN GOTCHAS, GOTCHA MITIGATIONS & DEBUGGING FAQ
12. ONBOARDING CHECKLIST (DAY 1 TO DAY 3)


================================================================================
1. EXECUTIVE SUMMARY & PROJECT MISSION
================================================================================

Aquanex is an on-premise, strictly air-gapped sovereign AI engineering workbench 
developed for heavy industrial environments (specifically crude distillation 
units, fluid catalytic crackers, and high-pressure hydrocarbon pipeline networks 
at Mangalore Refinery and Petrochemicals Limited — MRPL).

In refining and petrochemical operations, statutory failure can lead to 
catastrophic loss of containment, environmental violations, or plant shutdown. 
Commercial cloud AI services (OpenAI, Anthropic, AWS Bedrock) cannot be used 
due to:
  a) Critical National Infrastructure (CNI) cybersecurity mandates.
  b) Complete physical air-gapping of refinery operational networks (OT/LAN).
  c) Strict liability under statutory engineering standards (OISD-118, API 570, 
     ASME B31.3) requiring deterministic audit trails.

Aquanex replaces ad-hoc engineering workflows with an autonomous, policy-governed 
on-premise coworker that analyzes NDT ultrasonic inspection data, computes remaining 
safe piping life, generates statutory engineering deliverables (DOCX reports, 
PDF certificates, AutoCAD DXF spools, 3D STL meshes, Excel survey logs), and 
enforces cryptographic verification on every generated token.


================================================================================
2. CORE ARCHITECTURAL INVARIANTS (THE NON-NEGOTIABLES)
================================================================================

As a new engineer touching this codebase, you must preserve these 6 invariants:

[INVARIANT 1] ZERO OUTBOUND WAN EGRESS (STRICT HARDWARE AIR-GAP)
  - The application must function 100% offline on loopback (127.0.0.1) or local 
    refinery LAN (192.168.1.0/24).
  - Kernel network route monitoring (/proc/net/route) triggers an immediate 
    UI lockdown and process kill switch if an external default gateway is detected.
  - Never add external CDN imports, third-party telemetry, remote font links, or 
    cloud API calls.

[INVARIANT 2] PRE-RETRIEVAL ATTRIBUTE-BASED ACCESS CONTROL (ABAC RAG)
  - Chunks in vector storage are classified: UNCLASSIFIED, INTERNAL, CONFIDENTIAL, 
    or RESTRICTED.
  - Documents are filtered BEFORE entering prompt context. A Junior Technician 
    query cannot even retrieve CONFIDENTIAL chunks. Denied chunks never enter 
    the model's context window, completely neutralizing prompt injection leaks.

[INVARIANT 3] ZERO AUTONOMOUS CONSEQUENTIAL ACTIONS (HUMAN APPROVAL GATE)
  - The system NEVER sends emails, dispatches orders, or alters database state 
    without explicit human sign-off.
  - Actions produce a frozen draft and require a cryptographically signed one-time 
    HMAC-SHA256 Approval Token issued by an authorized Senior Lead or Admin.
  - Modifying the recipient, subject, or attachment payload invalidates the token.

[INVARIANT 4] STATUTORY WATERMARKING ON ALL DELIVERABLES
  - Every compiled Word (.docx) and PDF (.pdf) file MUST automatically embed 
    the statutory draft watermark:
    "AI-GENERATED DRAFT — STATUTORY HUMAN REVIEW REQUIRED"
  - Not valid for capital procurement without physical wet-ink sign-off blocks.

[INVARIANT 5] LOCAL VOICE SENTINEL (ZERO SURVEILLANCE INVARIANT)
  - Voice input is Push-to-Talk only (mouse hold / touch).
  - Audio streams into an ephemeral in-memory RAM buffer (io.BytesIO).
  - The raw audio buffer is immediately wiped (del raw_bytes) upon transcription. 
    Zero audio files are ever written to disk.
  - Voice is strictly an input modality, NEVER an authentication credential.

[INVARIANT 6] APPEND-ONLY CRYPTOGRAPHIC AUDIT CHAIN
  - Every model invocation, RAG retrieval, tool execution, and deliverable compiler 
    is hashed using SHA-256 and chained in an immutable SQLite ledger (mrpl_audit.db).
  - Any tampering with historical records breaks the cryptographic hash chain.


================================================================================
3. TECHNOLOGY STACK OVERVIEW
================================================================================

LAYER             TECHNOLOGIES
--------------------------------------------------------------------------------
Backend Core      Python 3.14 / 3.11+, FastAPI (REST + SSE streaming), Uvicorn
Agent Graph       LangGraph StateGraph (State Machine: router -> retriever -> 
                  reasoning -> compiler -> validator -> approval gate)
Vector Database   ChromaDB (local persistent on-premise embeddings)
Audit Database    SQLite3 with SHA-256 genesis hash chaining (mrpl_audit.db)
Execution Sandbox Linux Bubblewrap (bwrap) with isolated namespaces & 256MB cap
Deliverable Engine ezdxf (CAD DXF), ReportLab (PDF), python-docx (Word), 
                  openpyxl (Excel), matplotlib (Heatmaps), numpy-stl (3D STL)
Speech Subsystem  Faster-Whisper / local speech adapter (STT), Piper TTS (WAV)
Frontend Core     HTML5, Vanilla ES6+ JavaScript, Custom Modern CSS (CSS Grid, 
                  Flexbox, CSS variables — zero heavy framework dependencies)
Bundler & Dev     Vite 6.x (sub-300ms builds, zero runtime overhead)
Desktop Wrapper   PySide6 / WebKit2GTK native Linux window launcher 
                  (scripts/run_linux_desktop.py)
Testing Suite     pytest, pytest-asyncio, anyio (58 automated test suites)


================================================================================
4. SYSTEM ARCHITECTURE & DATA FLOW
================================================================================

                          [USER / CLIENT]
             ┌───────────────────┴───────────────────┐
             │                                       │
     [Desktop Client]                        [Web Browser]
  (PySide6 / WebKit2GTK)                  (http://127.0.0.1:5173)
             │                                       │
             └───────────────────┬───────────────────┘
                                 │ HTTP / SSE Stream
                                 ▼
                    [FASTAPI GATEWAY (Port 8000)]
      ┌──────────────────────────┼──────────────────────────┐
      │                          │                          │
[Auth & RBAC Matrix]   [Air-Gap Monitor]          [Telemetry Stream]
(/api/admin/auth)      (/proc/net/route)          (/api/telemetry/network)
      │
      ▼
[LANGGRAPH WORKFLOW ENGINE]
  │
  ├── 1. Router Node: Identifies intent (Line Analysis, CAD, NDT, SOP, General)
  │
  ├── 2. Pre-Retrieval ABAC Filter: Filters ChromaDB by user role & clearance
  │
  ├── 3. Sovereign Inference Tier:
  │      - Enterprise 100B+ Cluster (vLLM on 8x H100 SXM5 / NVLink)
  │      - Departmental Workstation 32B (Local RTX 4090 GPU via Ollama)
  │      - Ruggedized Field Laptop 8B (Intel NPU / CPU AVX-512)
  │
  ├── 4. Tool Sandbox Execution (Bubblewrap bwrap):
  │      - Code execution isolated in read-only chroot namespace
  │      - 256 MB RAM ceiling, SIGKILL timeout on runaway loops
  │
  ├── 5. Omni-Modal Compilers:
  │      - Generates DXF CAD, DOCX report, PDF certificate, XLSX sheet
  │      - Injects statutory draft watermarks & SHA-256 file hashes
  │
  ├── 6. Action Approval Gate:
  │      - If consequential action (e.g. Email dispatch, file commit):
  │        Freezes payload -> issues HMAC-SHA256 Token -> awaits Human Sign-off
  │
  └── 7. Cryptographic Ledger (mrpl_audit.db):
         - Appends Block #[N] with prev_hash, current_hash, timestamp, operator


================================================================================
5. PERSONA & PERMISSION MODEL (RBAC & ABAC)
================================================================================

Aquanex serves three distinct refinery operational personas:

1. RAJAT — IT Systems Administrator (Role: "admin", Level 1)
   - Scope: Complete infrastructure governance and security oversight.
   - UI: "Sovereign Cluster Control Center" (Clean, minimalist dashboard matching
     Pic 1). No dummy chat interface; registered cluster list, access matrix, 
     live hardware telemetry (CPU, RAM, DISK, Network 0 B/s), and SHA-256 ledger.
   - Model Permissions: All models (*).
   - Document Clearance: RESTRICTED, CONFIDENTIAL, INTERNAL.
   - Can issue approval tokens: YES.

2. ANAND — Senior Reliability Lead (Role: "senior", Level 2)
   - Scope: Line fitness calculations (API 570, ASME B31.3), remaining safe life,
     statutory sign-offs, and CAD replacement spools.
   - UI: Engineering workbench with prompt suggestion chips, live thought feed,
     omni-modal deliverable preview chips, and model tier dropdown.
   - Model Permissions: Configurable by Admin (typically 100B, 32B, 8B).
   - Document Clearance: CONFIDENTIAL & INTERNAL.
   - Can issue approval tokens: YES.

3. NAVEEN — Field Inspection Technician (Role: "junior", Level 3)
   - Scope: Rapid field inspection on ruggedized field laptops. Zero model friction.
   - UI: Locked model badge ("Standard Inspection Model Pre-configured"). Model 
     dropdown is hidden to eliminate configuration errors.
   - Model Permissions: Pre-configured Edge-8B only.
   - Document Clearance: INTERNAL only (cannot access confidential refinery audits).
   - Can issue approval tokens: NO (Action gate blocks token generation).


================================================================================
6. REPOSITORY STRUCTURE & CODE DIRECTORY MAP
================================================================================

/home/cyanide/SIH/
├── backend/
│   ├── app/
│   │   ├── api/                     # FastAPI endpoint routers
│   │   │   ├── chat.py              # SSE streaming chat & deliverable endpoints
│   │   │   ├── auth.py              # User persona switching & PIN auth
│   │   │   ├── admin.py             # Model governance & RBAC matrix endpoints
│   │   │   ├── telemetry.py         # Network air-gap probes & audit stream
│   │   │   ├── voice.py             # Local Voice Sentinel (STT & TTS)
│   │   │   └── actions.py           # Human-in-the-loop approval token gate
│   │   ├── compilers/               # Native industrial artifact builders
│   │   │   ├── cad_compiler.py      # AutoCAD DXF piping spool generator
│   │   │   ├── docx_builder.py      # Statutory Word report with watermarks
│   │   │   ├── pdf_builder.py       # Statutory PDF inspection certificates
│   │   │   ├── xlsx_builder.py      # Statutory Excel NDT thickness sheets
│   │   │   ├── stl_builder.py       # 3D binary STL mesh compiler
│   │   │   └── heatmap_builder.py   # Ultrasonic thickness corrosion heatmaps
│   │   ├── connectors/              # Scoped CoWork integration connectors
│   │   │   └── email_connector.py   # Internal email draft & gated loopback spool
│   │   ├── graph/                   # LangGraph state machine & reasoning nodes
│   │   │   ├── state.py             # Agent state schema & deliverable models
│   │   │   └── nodes.py             # Router, retriever, reasoner, tool executor
│   │   ├── policy/                  # Security, governance & isolation policies
│   │   │   ├── approval_tokens.py   # HMAC-SHA256 cryptographic action tokens
│   │   │   ├── air_gap.py           # Kernel /proc/net/route interface auditor
│   │   │   └── sandbox.py           # Linux bubblewrap (bwrap) isolation driver
│   │   ├── rag/                     # Pre-Retrieval ABAC & ChromaDB storage
│   │   │   └── retriever.py         # Classified RAG retriever with RBAC filters
│   │   ├── config.py                # Environment paths, secrets, vault directories
│   │   ├── main.py                  # Main FastAPI application factory
│   │   └── schemas.py               # Pydantic data validation contracts
│   └── tests/                       # Automated test suite (58 tests)
│       ├── test_sovereign_hardened.py # ABAC RAG, tokens, watermarking, voice
│       ├── test_omni_modal_100b.py  # Compilers (CAD, PDF, DOCX, STL, Excel)
│       ├── test_audit_fixes.py      # RBAC, air-gap kill switch, sandbox limits
│       ├── test_dev1_graph.py       # LangGraph routing & self-healing nodes
│       └── test_dev2_tools.py       # Sandbox isolation, RAG, & audit chain
│
├── frontend/
│   ├── index.html                   # Single Page App layout (Admin + Chat UI)
│   ├── package.json                 # Vite dependencies & build scripts
│   ├── src/
│   │   ├── api.js                   # SovereignAPI client with SSE event parser
│   │   ├── main.js                  # UI controllers, role toggling, voice, modal
│   │   └── style.css                # Sovereign design system (clean minimalistic)
│   └── dist/                        # Production build output
│
├── data/
│   ├── vault/                       # Read-only input engineering documents
│   ├── staging/                     # Staging area for compiled deliverables
│   └── mrpl_audit.db                # SQLite3 cryptographic ledger
│
├── scripts/
│   ├── run_linux_desktop.py         # Native Linux PySide6 desktop bootloader
│   ├── generate_synthetic_vault.py  # Generates test NDT logs, blueprints, CSVs
│   └── verify_airgap_killswitch.sh  # Automated hardware air-gap test script
│
├── KNOWLEDGE_TRANSFER.txt           # This document!
└── SovereignWorkbench_Gap_Analysis_and_Roadmap.md # Architectural specification


================================================================================
7. THE OMNI-MODAL COMPILER PIPELINE
================================================================================

Aquanex does not just output text chat. It compiles production-ready engineering 
artifacts directly inside the air-gapped environment:

FILE TYPE        OUTPUT FORMAT    COMPILER ENGINE             STATUTORY BADGE
--------------------------------------------------------------------------------
Piping CAD       .dxf             backend.app.compilers.cad   ANSI D / ISO-A1
Executive Report .docx            docx_builder.py             DRAFT WATERMARK
Statutory Cert   .pdf             pdf_builder.py              OISD-118 Sign-off
NDT Wall Log     .xlsx            xlsx_builder.py             API 570 Color-Code
3D Spool Mesh    .stl             stl_builder.py              Binary 3D Facets
Corrosion Map    .png             heatmap_builder.py          Jet Ultrasonic Scale


================================================================================
8. COWORK ACTION GATING & CRYPTOGRAPHIC TOKENS
================================================================================

When the AI prepares a consequential action (such as dispatching an inspection 
warning email to turnaround teams or modifying staging spools):

Step 1: The AI drafts the email and computes SHA-256 hashes of all attachments.
Step 2: The action payload is FROZEN in memory.
Step 3: The UI displays the Action Approval Modal (#actionApprovalModal).
Step 4: The Senior Lead or Admin reviews the frozen draft and clicks "Approve".
Step 5: The gateway (/api/actions/approve) issues a cryptographically signed token:
          HMAC-SHA256(user_id + action_type + payload_hash + expiration)
Step 6: The email connector verifies the token. If valid, the email is logged 
        to the local on-premise spool (dispatched_emails.jsonl).
Step 7: The audit block is recorded in mrpl_audit.db.


================================================================================
9. LOCAL ENVIRONMENT SETUP & RUNNING THE APP
================================================================================

PREREQUISITES:
  - Linux OS (Ubuntu 22.04+, Debian 12+, Arch, Fedora, RHEL)
  - Python 3.11+ (Python 3.14 recommended)
  - Node.js 18+ and npm
  - Bubblewrap (`bwrap`) installed: `sudo apt install bubblewrap`
  - SQLite3 installed

STEP-BY-STEP STARTUP:

1. Clone & Navigate to Workspace:
   cd /home/cyanide/SIH

2. Activate Python Virtual Environment:
   source .venv/bin/activate  (or use system Python if packages are installed)

3. Install Backend Dependencies:
   pip install -r backend/requirements.txt

4. Install Frontend Dependencies:
   cd frontend
   npm install
   cd ..

5. Start the FastAPI Backend Server (Terminal 1):
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

6. Start the Vite Frontend Server (Terminal 2):
   cd frontend
   npm run dev -- --host 127.0.0.1 --port 5173

7. Launch in Browser:
   - For IT Admin (Rajat):
     http://127.0.0.1:5173/?persona=admin&bypass_airgap=1
   - For Senior Reliability Lead (Anand):
     http://127.0.0.1:5173/?persona=senior&bypass_airgap=1
   - For Field Inspection Tech (Naveen):
     http://127.0.0.1:5173/?persona=junior&bypass_airgap=1

8. (Optional) Launch as Native Linux Desktop App:
   python3 scripts/run_linux_desktop.py --persona senior


================================================================================
10. RUNNING AUTOMATED TESTS & VERIFICATION
================================================================================

Always run the full test suite before committing any code changes:

1. Run Backend Automated Test Suite (58 Tests):
   cd /home/cyanide/SIH
   PYTHONPATH=backend pytest backend/tests/ -v

   Expected output: 58 passed in ~4 seconds.

2. Run Specific Test Suites:
   - Hardened Sovereign Security & Tokens:
     PYTHONPATH=backend pytest backend/tests/test_sovereign_hardened.py -v
   - Omni-Modal Compilers (CAD, PDF, DOCX, STL):
     PYTHONPATH=backend pytest backend/tests/test_omni_modal_100b.py -v
   - Air-Gap & Sandbox Isolation:
     PYTHONPATH=backend pytest backend/tests/test_audit_fixes.py -v

3. Validate Frontend Production Build:
   cd frontend
   npm run build
   Expected output: "built in ~250ms" with zero errors.


================================================================================
11. KNOWN GOTCHAS, GOTCHA MITIGATIONS & DEBUGGING FAQ
================================================================================

Q1: The red "Air-Gap Security Alert: Internet Detected" lockdown modal appeared!
A1: Your machine has an active default network route to the public internet. 
    In development, you can add `?bypass_airgap=1` to the URL or click "Dismiss 
    Alert (Emergency Bypass)" in the UI to continue local testing.

Q2: Why did `PYTHONPATH=backend pytest` fail with ModuleNotFoundError?
A2: Always set `PYTHONPATH=backend` when invoking pytest so Python resolves `app.*` 
    modules correctly: `PYTHONPATH=backend pytest backend/tests/ -v`.

Q3: Why doesn't the IT Admin have a chat box or "+ New chat" button?
A3: By design (per the architecture and Pic 1 / Pic 2 requirements). The IT Admin 
    (Rajat) is a Level 1 systems governance user who manages compute clusters, 
    personnel RBAC permissions, and cryptographic ledger blocks. He does not run 
    engineering chats. Switch persona to Anand (Senior Lead) to access chat.

Q4: How do I test the Push-to-Talk Voice Sentinel without a real microphone?
A4: The endpoint `/api/voice/transcribe` accepts a `mock_prompt` parameter, or you 
    can invoke the automated test `backend/tests/test_sovereign_hardened.py` which 
    validates the zero-surveillance ephemeral RAM buffer contract programmatically.

Q5: Where do compiled CAD and report deliverables go?
A5: All deliverables are compiled into `data/staging/` and registered with a 
    SHA-256 digest in `mrpl_audit.db`. They can be downloaded from the UI.


================================================================================
12. ONBOARDING CHECKLIST (DAY 1 TO DAY 3)
================================================================================

[ ] DAY 1: GETTING SET UP
    - Read this KNOWLEDGE_TRANSFER.txt thoroughly.
    - Run `PYTHONPATH=backend pytest backend/tests/ -v` and confirm 58/58 tests pass.
    - Start backend (port 8000) and frontend (port 5173).
    - Open `http://127.0.0.1:5173/?persona=senior&bypass_airgap=1` in your browser.
    - Submit a prompt: "Audit line CDU-2-04-150-A1A for remaining safe life per API 570".
    - Inspect the generated deliverables (CAD DXF, DOCX draft, NDT Excel sheet).

[ ] DAY 2: CODEBASE WALKTHROUGH
    - Inspect `backend/app/graph/nodes.py` to see how LangGraph coordinates tools.
    - Inspect `backend/app/policy/approval_tokens.py` to understand token binding.
    - Inspect `backend/app/rag/retriever.py` to understand pre-retrieval ABAC filtering.
    - Inspect `frontend/src/main.js` to see how role toggling switches views.

[ ] DAY 3: MAKE YOUR FIRST CONTRIBUTION
    - Add a test or utility function to `backend/app/compilers/`.
    - Verify `npm run build` in `frontend/`.
    - Run the complete test suite.
    - Submit your branch for peer review.

================================================================================
WELCOME TO THE AQUANEX TEAM! KEEP IT AIR-GAPPED, SAFE, AND STATUTORY.
================================================================================
