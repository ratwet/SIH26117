# Product Requirements Document (PRD)

# Project: SovereignWorkbench
### Sovereign On-Premise Agentic AI Workbench for Confidential Industrial Work
**Problem Statement ID:** SIH26117 (PS 117)  
**Client / Beneficiary Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL) / MoPNG  
**Category:** Software | **Theme:** Smart Automation  
**Document Version:** 1.1 (Comprehensive Baseline)  
**Status:** Draft (Pending Team Sign-off)  

---

## 1. Executive Summary & Product Vision

### 1.1 Product Vision
**SovereignWorkbench** is an enterprise-grade, 100% air-gapped, multi-tier agentic AI platform engineered specifically for oil refineries, Public Sector Undertakings (PSUs), and defence-linked manufacturing units. It empowers process engineers, plant inspectors, and technical committees to automate high-stakes knowledge work—such as technical drawing audits (P&IDs), safety compliance calculations (API 570 / ASME), and executive approval dossiers—without a single byte of confidential enterprise data leaving the physical premises.

### 1.2 Core Philosophy
* **Zero Trust, Zero Cloud:** 100% on-premise execution with an active, kernel-enforced **Air-Gap Interlock (Kill Switch)** that freezes operations if an external internet route is detected.
* **Deterministic Orchestration over the Model (LangGraph):** Foundation models are passive computational engines; the SovereignWorkbench LangGraph state orchestrator provides deterministic memory, conditional graph routing, cyclic self-healing recovery, code execution sandboxing, and enterprise deliverable generation.
* **Deterministic Math over Hallucination:** Critical engineering figures are never mentally estimated by an LLM; they are compiled into Python scripts and executed in an isolated local sandbox with an autonomous **Self-Healing Error Recovery Loop**.
* **Zero Friction for Plant Staff:** Native cross-platform desktop application (`.exe`, `.AppImage`, `.dmg`) with mDNS auto-discovery (`mrpl-server.local`) requiring zero terminal commands or IP configuration from plant engineers.

---

## 2. Problem Statement & Enterprise Context

### 2.1 The Operational Problem
Refineries generate massive volumes of routine, high-stakes technical documentation:
* Piping & Instrumentation Diagrams (P&IDs) and isometric schematics.
* Ultrasonic wall-thickness corrosion reports and maintenance logs.
* Capex procurement notes, executive board briefs, and engineering calculations.

### 2.2 The Regulatory Deadlock
Under Indian data sovereignty directives (MoPNG, OISD, CERT-In), this intelligence cannot be transmitted to commercial cloud AI vendors (OpenAI, Anthropic, Microsoft) due to severe national security and trade secret liabilities. 

Consequently, industrial engineers face a productivity deadlock:
1. **Manual Stagnation:** Engineers spend 30–40% of their working hours manually cross-referencing paper SOPs, recalculating formulas in Excel, and formatting compliance notes.
2. **The Shadow-AI Crisis:** Engineers under strict deadlines secretly copy-paste sensitive industrial data into public cloud tools, creating catastrophic data exfiltration vectors.

---

## 3. User Personas & Role-Based Access Control (RBAC)

The system enforces strict enterprise role segregation matching PSU operational hierarchy:

| Persona | Role in Organization | Core Needs from SovereignWorkbench | Assigned System Tier & Permissions |
| :--- | :--- | :--- | :--- |
| **P1: IT & Security Admin** | Corporate IT & Cyber Security Cell | • Securely import model weights (`.gguf`)<br>• Enforce air-gap compliance<br>• Allocate GPU compute quotas | **Admin Console (Laptop 1):** Full access to Model Registry, RBAC tiering, system audit logs, and hardware telemetry. |
| **P2: Senior Process Engineer** | Maintenance Superintendent / Chief Inspector | • Audit complex P&ID blueprints<br>• Run API 570 pipe failure calculations<br>• Export signed Word approval notes | **Senior Tier (Laptop 3):** Full access to `DeepSeek-R1` reasoning, `Qwen2-VL` vision, sandbox code execution, and unwatermarked `.docx`/`.xlsx` exports. |
| **P3: Junior Engineer / Trainee** | Plant Floor Trainee / Field Operator | • Look up refinery SOPs and standards<br>• Generate routine task summaries<br>• Draft simple internal correspondence | **Junior Tier (Laptop 3):** Routed to fast, lightweight models (`Qwen-2.5-3B`), standard GPU queue, read-only SOP knowledge base. |

---

## 4. System Topology & Physical Architecture (3-Tier Distributed Setup)

To guarantee flawless live demonstrability and reflect real refinery deployment, the system operates across three distinct nodes over an isolated local network:

```
                      [OFFLINE LOCAL ACCESS POINT / HOTSPOT]
                       (SSID: MRPL_AIRGAP | No WAN Cable!)
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│ NODE 1: ADMIN CONSOLE│    │ NODE 2: PLANT SERVER │    │ NODE 3: CLIENT APP   │
│ (Laptop 1: Corporate)│    │ (Laptop 2: GPU Host) │    │ (Laptop 3: Engineer) │
│ • Model Ingestion    │    │ • Ollama Model Engine│    │ • Native Desktop App │
│ • RBAC Assignment    │    │ • Execution Sandbox  │    │ • Air-Gap Kill Switch│
│ • SHA-256 Audit Log  │    │ • mDNS Broadcast     │    │ • P&ID Viewer & Docs │
└──────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

### 4.1 Node Specifications
1. **Node 1 (IT Admin Console):** Light laptop running the Web Admin Dashboard over port `8000/admin`.
2. **Node 2 (Central GPU Server / Gaming Laptop):** Dedicated GPU machine (RTX 3060/4060 6GB–12GB VRAM) hosting `Ollama` (`:11434`), `FastAPI` backend with LangGraph state machine orchestrator (`:8000`), and isolated sandbox runner. Broadcasts local mDNS as `mrpl-server.local`.
3. **Node 3 (Chemical Engineer Workstation):** Standard office laptop running the native desktop client. Auto-discovers Node 2 via mDNS.

---

## 5. Functional Requirements (FR)

### FR-01: Air-Gap Interlock & Zero-Exfiltration Security
* **FR-01.1 (Active Interface Sniffer):** The client application must poll local network routing tables every 2 seconds.
* **FR-01.2 (Emergency Kill Switch):** If a default gateway to a public WAN (e.g., 4G mobile tethering, external Wi-Fi, Ethernet) is detected, the application must immediately freeze all document access and display a modal red lock screen:  
  `🚨 AIR-GAP VIOLATION: External Internet connection detected. Disconnect to resume.`
* **FR-01.3 (Zero-Packet Kernel Telemetry):** The server must read `/proc/net/dev` and `/proc/net/tcp` to stream real-time socket statistics to the UI, proving 0 outbound WAN bytes.
* **FR-01.4 (Sandbox Network Disablement):** All code executed by the agent must run with the network stack completely unshared (`bwrap --unshare-net`).

### FR-02: Local Model Serving & Dynamic Routing
* **FR-02.1 (Local Inference):** The backend must serve open-weight quantized models locally via Ollama with zero external API calls.
* **FR-02.2 (Default Baseline Models):**
  * *Router / Intent Classifier:* `Qwen-2.5-3B-Instruct` (Q8_0, ~3.5GB VRAM).
  * *Engineering Reasoning & Math:* `DeepSeek-R1-Distill-Qwen-8B` (Q4_K_M, ~5.4GB VRAM).
  * *P&ID Blueprint Vision:* `Qwen2-VL-7B-Instruct` (Q4_K_M, ~5.2GB VRAM).
  * *Tool Code Generation:* `Qwen-2.5-Coder-7B-Instruct` (Q4_K_M, ~4.8GB VRAM).
* **FR-02.3 (Dynamic VRAM Swapping):** The LangGraph state orchestrator must manage model residency, sequentially offloading idle models in under 2 seconds to prevent GPU Out-Of-Memory (OOM) errors.
* **FR-02.4 (Pluggable Model Registry):** The IT Admin must be able to drop any new `.gguf` file into `/models_storage/`, register it via the UI, and assign it a functional role without modifying source code.

### FR-03: Multimodal Industrial Ingestion
* **FR-03.1 (Scanned PDF Parsing):** Ingest multi-page scanned ultrasonic wall-thickness inspection reports via local OCR (Docling / PaddleOCR).
* **FR-03.2 (P&ID Blueprint Analysis):** Process technical engineering drawings (PNG, TIFF, PDF) using `Qwen2-VL` to extract line tags (e.g., `CDU-2-04-150-A1A`), nominal thickness, valve types, and piping specs.

### FR-04: Deterministic Sandbox & Self-Healing Error Recovery
* **FR-04.1 (Math Offloading):** The LLM is strictly prohibited from doing mental arithmetic for safety-critical metrics. It must output standard Python calculation scripts.
* **FR-04.2 (Isolated Container REPL):** Run the generated Python code in a secured, non-networked Linux namespace with strict limits (5-second timeout, 256MB RAM).
* **FR-04.3 (Error Distillation & Cyclic Routing):** If a runtime error occurs (`ZeroDivisionError`, `KeyError`, `ValueError`), LangGraph's conditional retry edge must capture `stderr`, distill the exact failing line and message, and route back to the code generator node for self-healing.
* **FR-04.4 (Circuit Breaker):** The self-healing loop is capped at a maximum of 3 attempts. If attempt 3 fails, the system triggers a graceful Human-in-the-Loop escalation prompt.
* **FR-04.5 (Library Whitelist):** Enforce an explicit pre-installed Python manifest (`math`, `numpy`, `scipy`, `pandas`, `openpyxl`, `docx`). Block all unwhitelisted import attempts.

### FR-05: Enterprise Deliverable Compiler
* **FR-05.1 (Executive Word Note):** Automatically compile validated findings into a formal **`MRPL_Approval_Note.docx`** including corporate letterhead, ultrasonic data tables, step-by-step formula derivations, and signature blocks.
* **FR-05.2 (Cost & Corrosion Matrix):** Automatically compile a formatted **`Cost_Matrix.xlsx`** workbook with active Excel formulas and conditional risk formatting.
* **FR-05.3 (Native Disk Save):** Save files directly to the engineer's chosen local project directory without browser download prompts.

### FR-06: Cross-Platform Native Client & Zero-Config Networking
* **FR-06.1 (Cross-Platform Binaries via Tauri):** Ship standalone native client binaries for **Windows** (`.exe`), **Linux** (`.AppImage`), and **macOS** (`.dmg`). Tauri is chosen over Electron specifically to achieve a sub-15MB installer size and negligible memory footprint (~40MB RAM vs Electron's 150MB+ bundle and 300MB+ RAM consumption).
* **FR-06.2 (mDNS Auto-Discovery):** The client must automatically discover `mrpl-server.local` on the offline Wi-Fi without requiring users to type IP addresses or ports.

### FR-07: Local Knowledge Base & Retrieval (Sovereign RAG)
* **FR-07.1 (Offline Document Ingestion):** Ingest refinery SOPs, OISD standards, API 570 guidelines, and plant maintenance manuals into a local vector database.
* **FR-07.2 (Zero-GPU Embedding Engine):** Generate embeddings using CPU-optimized small models (e.g., `bge-small-en-v1.5` or `all-MiniLM-L6-v2` via ONNX Runtime/FastEmbed). This preserves 100% of GPU VRAM exclusively for LLM inference.
* **FR-07.3 (Local Vector Store):** Store vectors in an embedded, serverless database (ChromaDB or SQLite-vec) persisted directly on the server SSD.
* **FR-07.4 (Grounded Citations & Clause Retrieval):** Injected prompts must strictly cite specific document clauses, revision numbers, and page numbers (e.g., `Ref: OISD-STD-118 Section 4.2`) to eliminate unsubstantiated advice.

### FR-08: Cryptographic Audit Trail & Governance Logging
* **FR-08.1 (Tamper-Evident Hash Chain):** Maintain an append-only SQLite log (`mrpl_audit.db`). Each transaction records: timestamp, user role, model ID, prompt hash, tool execution exit code, output hash, and previous entry hash (SHA-256 chain).
* **FR-08.2 (Air-Gap Attestation Log):** Log every network scan result. If an external connection attempt is made, record the MAC address, network interface, and immediate lockdown timestamp.
* **FR-08.3 (Compliance Report Export):** Provide IT Admins with a one-click cryptographically signed audit report (`Audit_Report_[Date].pdf`) for CISO/CERT-In verification.

---

## 6. Non-Functional Requirements (NFR)

| ID | Category | Requirement Specification | Measurement / Verification |
| :--- | :--- | :--- | :--- |
| **NFR-01** | **Air-Gap Integrity** | Exactly 0 bytes transmitted outside the local subnetwork during any execution phase. | Continuous verification via kernel socket monitor (`/proc/net/dev`) showing 0 WAN packets. |
| **NFR-02** | **Inference Throughput** | The 3B Q8 baseline model must generate at least 45 tokens/second on an RTX 3060/4060 GPU. | Verified via Ollama token generation metrics. |
| **NFR-03** | **Memory Safety** | Active GPU VRAM footprint must not exceed 6.0 GB on the demo rig at any point during sequential swapping. | Monitored via `nvidia-smi` logging. |
| **NFR-04** | **Fault Resilience** | Script runtime errors must recover autonomously within 2 retries in >= 90% of common calculation edge cases. | Validated through synthetic unit test suite injecting division-by-zero and missing variables. |
| **NFR-05** | **Client Footprint** | The client installer size must remain under 15 MB with near-zero CPU idle consumption. | Verified via Tauri compiled binary inspection. |

---

## 7. End-to-End User Journey (The SIH Winning Demo Flow)

```
[SCENARIO: CRITICAL PIPE CORROSION AUDIT AT MRPL CDU-2]
```

1. **Setup:**
   * Laptop 1 (Admin), Laptop 2 (Server), and Laptop 3 (Client) connect to the offline Wi-Fi hotspot (`MRPL_AIRGAP`).
   * WAN cable is visibly disconnected.
2. **Launch:**
   * Chemical Engineer launches `SovereignWorkbench.AppImage` on Laptop 3.
   * Client automatically displays: `[GREEN] Connected to Plant Server (mrpl-server.local) | [LOCKED] Air-Gap Active`.
3. **Ingestion:**
   * Engineer drags-and-drops `CDU2_Ultrasonic_Inspection_Report.pdf` and `P&ID_Drawing_Line150.png`.
4. **Agentic Execution:**
   * Task Router delegates visual parsing to `Qwen2-VL`: identifies line `CDU-2-04-150-A1A` with thickness `t_actual = 3.2 mm` (nominal `4.8 mm`).
   * Router delegates calculation to `DeepSeek-R1`: retrieves API 570 formulas and writes a Python script.
   * **Deliberate Error & Self-Healing:** The script encounters a missing installation year -> sandbox captures error -> agent re-reads document page 2 -> self-heals on attempt #2.
   * Python executes in sandbox: computes remaining life = **3.1 years** (Threshold < 5 years triggers mandatory shutdown replacement).
5. **Deliverable Export:**
   * System generates `MRPL_Approval_Note_CDU2.docx` and `Cost_Estimate.xlsx`.
   * Engineer clicks "Save Deliverables" -> opens instantly in LibreOffice/Word.
6. **The Kill Switch Demonstration:**
   * Presenter connects Laptop 3 to a mobile 4G hotspot.
   * **App instantly flashes RED and locks down:** `AIR-GAP VIOLATION DETECTED`.
   * Hotspot disconnected -> app immediately unlocks and restores green operational state.

---

## 8. Development Roadmap & SIH Milestone Breakdown

### Phase 1: Pre-Hackathon Preparation Sprints
```
[SPRINT 1: CORE ENGINE] ──► [SPRINT 2: SANDBOX & RAG] ──► [SPRINT 3: CLIENT & UI] ──► [SPRINT 4: AIR-GAP TEST]
• Local Ollama setup        • Python REPL sandbox         • Tauri desktop app         • 3-Laptop live trial
• Model weights ingestion   • CPU-based RAG pipeline      • mDNS auto-discovery       • Deliberate bug rehearsal
• Multi-model router        • Error distillation loop     • Kill switch logic         • Offline hotspot stress
```

* **Sprint 1 (Days 1–7): Local Model Serving & LangGraph Router Gateway**
  * Configure Ollama with `Qwen-2.5-3B-Q8`, `DeepSeek-R1-8B`, and `Qwen2-VL-7B`.
  * Implement FastAPI backend with LangGraph state graph and dynamic model switching manager.
* **Sprint 2 (Days 8–14): Sandboxed Execution, RAG & Deliverable Engines**
  * Build isolated `bwrap` execution runner with strict timeout and memory limits.
  * Implement the LangGraph Self-Healing Error Recovery loop with conditional edges and error distillation.
  * Implement CPU-based RAG with ChromaDB and `bge-small-en-v1.5`.
  * Build templated generators for `MRPL_Approval_Note.docx` and `Cost_Matrix.xlsx`.
* **Sprint 3 (Days 15–21): Native Desktop Client & Air-Gap Interlock**
  * Develop Tauri desktop app with dark-mode industrial theme.
  * Implement mDNS auto-discovery (`mrpl-server.local`).
  * Implement kernel socket monitor, audit hash chain, and the Emergency Red Lock Screen.
* **Sprint 4 (Days 22–28): 3-Laptop Integration & Rehearsal**
  * Wire up the 3-laptop network over the offline hotspot.
  * Rehearse the live demo scenario: P&ID inspection -> self-healing math -> signed `.docx` export -> live hotspot kill switch trigger.

### Phase 2: 36-Hour Grand Finale Execution Schedule
* **Hours 00–04:** Rig Setup, offline hotspot verification, model weights verification on Laptop 2.
* **Hours 04–12:** Refinery domain customization: inject MRPL-specific CDU-2 inspection data into local RAG.
* **Hours 12–20:** Deliberate bug & self-healing test automation; ensure error trace distillation runs under 3 seconds.
* **Hours 20–28:** UI polish: live network HUD gauges, zero-outbound packet live graph, signed Word template formatting.
* **Hours 28–34:** Dry-run end-to-end demo under simulated evaluator questioning; test kill switch under various adapter states.
* **Hours 34–36:** Final code freeze, audit hash snapshot, presentation staging.

---

## 9. Alignment with SIH Evaluation Pillars

The project architecture is directly mapped against the core dimensions typically weighted by SIH judging committees:

| SIH Evaluation Dimension | Strategic Alignment in SovereignWorkbench |
| :--- | :--- |
| **Technical Novelty & AI Depth** | Multi-model dynamic scheduling, LangGraph cyclic state machine with autonomous self-healing, CPU-based sovereign RAG, and sandboxed deterministic code execution instead of a basic chat wrapper. |
| **Fulfillment of Problem Statement** | 100% adherence to MRPL requirements: runs on organization server, demonstrable on a mid-range GPU, zero cloud traffic, native `.docx`/`.xlsx` deliverables. |
| **Feasibility & Practical Usability** | Native desktop app with zero-IP mDNS auto-discovery and RBAC tiering tailored for chemical engineers and IT governance. |
| **Live Demonstration Impact (WOW Factor)**| The physical 3-laptop layout, the deliberate self-healing error recovery, and the live mobile hotspot kill switch test. |
| **Code Quality & Architecture** | Clean separation of concerns (Purdue model), isolated sandboxes, and immutable cryptographic audit logging. |

---

## 10. Failure Mode & Risk Mitigation Matrix (Demo & Plant Operations)

| Risk Event | Severity | Probability | Root Cause | Engineering Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **mDNS Discovery Blocked** | High | Low | Venue router or hotspot blocks multicast/UDP 5353. | **Zero-Config Fallback:** The client defaults to scanning the local subnet (`192.168.x.x`) or falls back to a hardcoded secondary alias (`192.168.137.1`). |
| **GPU Out of Memory (OOM)** | Critical | Low | Two heavy models loaded concurrently. | **Dynamic Residency Guard:** The orchestrator forces an explicit `keep_alive: 0` offload via Ollama before invoking a second model, guaranteeing peak VRAM <= 5.5GB. |
| **Model Code Generation Fails 3x** | Medium | Medium | Ill-formed input data or edge-case calculation syntax. | **Graceful Human-in-the-Loop Fallback:** The circuit breaker halts execution, displays the raw extracted values, and prompts the engineer to verify the formula manually before generating the note. |
| **Scanned Document Illegible** | Medium | Medium | Poor resolution or corrupted scan. | **Hybrid OCR Pipeline:** Primary Docling extraction falls back to secondary PaddleOCR with high-contrast pre-processing. |
| **Host Machine Thermal Throttling** | Medium | Medium | Continuous GPU load during long evaluation rounds. | **Quantization Overhead Reduction:** Defaulting to 4-bit/8-bit GGUFs keeps GPU power draw under 80W, preventing thermal degradation. |
