# Project Context & Conversation Trajectory (`context.md`)

## 1. Project Background & Problem Context

### 1.1 The Challenge
* **Initiative:** Smart India Hackathon (SIH) 2026
* **Problem Statement ID:** SIH26117 (PS 117)
* **Title:** *Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work*
* **Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL), an ONGC group company under the Ministry of Petroleum and Natural Gas (MoPNG).
* **Category:** Software | **Theme:** Smart Automation

### 1.2 The Regulatory & Operational Deadlock
Indian oil refineries, petrochemical plants, and defence manufacturing facilities handle strictly proprietary engineering data:
* P&ID blueprints, process flow diagrams, isometric piping designs.
* Ultrasonic corrosion surveys, metallurgical inspection logs, Non-Destructive Testing (NDT) data.
* Capital expenditure (Capex) procurement briefs, statutory compliance submissions (OISD, ASME, API).

**The Deadlock:** Under MoPNG, OISD, and CERT-In mandates, this confidential data cannot be transmitted to external cloud LLM providers (OpenAI, Anthropic, Azure, Google Cloud). At the same time, engineers face high cognitive overload manually cross-referencing paper SOPs, recalculating pipe corrosion rates, and drafting compliance approval notes.

### 1.3 The Technical Solution
A **100% on-premise, distributed Agentic AI Workbench** running locally on an organization's own mid-range GPU workstation or server. It automates technical document parsing, runs deterministic math in an isolated sandbox, auto-selects open-weight models based on task type, generates signable Word/Excel deliverables, and provides verifiable cryptographic proof that zero outbound network traffic is generated.

---

## 2. Complete Workspace File Catalog

The project workspace is located at `/home/cyanide/SIH/`. Below is the complete manifest of files currently created and maintained:

| File Path | Size | Description & Role |
| :--- | :--- | :--- |
| [`PRD.md`](file:///home/cyanide/SIH/PRD.md) | ~20.7 KB | **Product Requirements Document (v1.1):** Exhaustive specifications for the 8 Functional Requirements, 5 Non-Functional Requirements, User Personas (IT Admin vs. Junior vs. Senior Engineer), 3-Tier Topology, Self-Healing Sandbox, CPU RAG, Cryptographic Audit Trail, Demo Script, Roadmap, and Risk Mitigation Matrix. |
| [`TEAM_CONTEXT.md`](file:///home/cyanide/SIH/TEAM_CONTEXT.md) | ~14.5 KB | **Team Collaboration & Onboarding Guide:** Clear, actionable onboarding briefing for teammates covering problem context, physical 3-laptop layout, LangGraph state loop, 5-minute demo script, team role assignments, and day-1 dev setup. |
| [`memory.md`](file:///home/cyanide/SIH/memory.md) | ~7.2 KB | **Persistent Operational Memory:** Core architectural decisions, hardware VRAM budgets, technology stack selections, user preferences, security interlocks, and the winning demo sequence. |
| [`context.md`](file:///home/cyanide/SIH/context.md) | Current | **Project Context & Conversation Record:** Deep dive into problem background, conversation trajectory, codebase catalog, and immediate next implementation steps. |
| [`PROBLEM_STATEMENT_117.md`](file:///home/cyanide/SIH/PROBLEM_STATEMENT_117.md) | ~22.7 KB | **Master Problem Dossier:** Deep technical analysis of PS 117, multi-model routing table, tool registry design, air-gap proof mechanics, team roles, and hackathon execution strategy. |
| [`PS_117_Sovereign_AI_Workbench.tex`](file:///home/cyanide/SIH/PS_117_Sovereign_AI_Workbench.tex) | ~3.9 KB | **Academic / Technical Overview (LaTeX):** Formatted with strict 1cm margins on A4 paper (`\usepackage[a4paper, margin=1cm]{geometry}`), explaining in simple, basic English the difference between a raw Base Model (passive engine) and an AI Harness (complete operating vehicle). |
| [`simple_system_flow.svg`](file:///home/cyanide/SIH/simple_system_flow.svg) | ~5.6 KB | **Systems Engineering Pipeline Flow (SVG):** Clean, minimalistic vector block diagram showing the 6 stages from User Ingestion -> Air-Gap Gate -> Task Router -> Local GPU Inference -> Deterministic Sandbox -> Office Deliverable Compiler. |
| [`architecture_tree.svg`](file:///home/cyanide/SIH/architecture_tree.svg) | ~19.7 KB | **Comprehensive 4-Tier Tree Diagram (SVG):** Detailed vector tree showing the 4 physical/functional branches: IT Admin Console, Central GPU Server, Chemical Engineer Client, and Air-Gap Security Interlock. |
| [`README.md`](file:///home/cyanide/SIH/README.md) | ~3.1 KB | **Repository Landing Page:** Quick-start guide, high-level architecture overview, feature list, and hardware requirements. |
| `deepseek-harness/` | Directory | **External Reference Codebase:** Open-source AI harness provided by the user for reference and adaptation into our air-gapped sovereign framework. |
| `what is harness.pdf` | ~64.7 KB | **Reference Document:** PDF explaining the conceptual mechanics of an AI harness. |

---

## 3. Chronological Conversation Record & Decisions Log

Below is the chronological record of user requests, key dilemmas resolved, and architectural decisions made throughout the conversation:

### Phase 1: Problem Selection & Domain Alignment
* **Action:** Evaluated 10 shortlisted SIH problems from `selected_ps.json` across domains (Cybersecurity, Blockchain, GIS, Port Management, AI).
* **Decision:** Selected **PS 117 (SIH26117) from MRPL** as the highest-leverage opportunity due to its massive enterprise credibility, clear evaluation boundaries, and strong fit with local open-weight AI.
* **Cleanup:** Purged obsolete scraper files, old problem dossiers, and outdated ranking PDFs to keep the workspace clean and focused on PS 117.

### Phase 2: Conceptual Clarity — Base Model vs. AI Harness
* **User Dilemma:** *"Basically in some way we are building an ai harness right? Deekseek released an open source ai harness i have that saved somewhere else... can we use that and modify that?"*
* **Resolution:** 
  * Clarified the exact distinction using the car engine analogy: The LLM (`Qwen`, `DeepSeek-R1`) is just the raw internal combustion engine sitting on the floor. An AI Harness provides the transmission, steering wheel, brakes, dashboard, and fuel tank.
  * Created `PS_117_Sovereign_AI_Workbench.tex` formatted to exact user style: simple, plain English paragraphs, no academic fluff, with exact 1cm margins on A4.

### Phase 3: Physical Table Layout & Network Realism
* **User Dilemma:** *"No we will keep the original flow and will use a say 3b 8 bit quantized model. 3 laptops. 1 admin laptop choose the model 2. a gaming laptop for hosting the model 3 user laptop to run/use. Now how will the hosting and usage take place... i dont have the option of offline wifi box can i use hotspot without internet?"*
* **Resolution:**
  * Designed the **3-Laptop Physical Layout**:
    1. Laptop 1: Corporate IT Admin (Model weights import, RBAC governance, SHA-256 verification).
    2. Laptop 2: Gaming Laptop Server (Hosts Ollama, RTX 3060/4060 GPU, FastAPI orchestrator, isolated sandbox, mDNS broadcast).
    3. Laptop 3: Chemical Engineer Client (Runs native desktop client app).
  * Confirmed that a mobile hotspot (or the gaming laptop's built-in Windows/Linux hotspot) with mobile data / WAN physically disabled acts as the perfect offline local area network.
  * Configured **mDNS (`mrpl-server.local`)** so the client laptop automatically discovers the server without typing IP addresses.

### Phase 4: Enterprise RBAC & Security Kill Switch
* **User Insight:** Chemical engineers will never download models; the IT department will. Models can be tiered: lightweight 3B models for junior trainees/operators (SOP queries) and deep reasoning models (`DeepSeek-R1`) for senior inspectors (failure calculations).
* **The Security Interlock:** User requested: *"we will disable the application when internet is connected specially in jr and sr engi pcs"*.
* **Implementation:** Architected the **Air-Gap Interlock (Kill Switch)**. A background network sniffer checks routing tables every 2 seconds. If an external WAN gateway (public Wi-Fi, 4G dongle) is detected, the application instantly locks down with a red emergency modal screen to prevent data exfiltration.

### Phase 5: Client Application Decision — Native vs. Browser
* **User Decision:** Rejected browser/PWA fallbacks (*"i think 3 is not required its good but atleast the admin would have should have installed it right?"*).
* **Implementation:** The client is built as a **cross-platform native desktop app** via **Tauri** (`.exe` for Windows, `.AppImage` for Linux, `.dmg` for macOS). This guarantees a tiny installer footprint (<15MB), near-zero RAM consumption (~40MB), and direct native disk file saving.

### Phase 6: Visual Architecture & Diagrams
* **User Request:** *"create me the final graph architecture that would be proposed... i meant tree diagram... create svg of the actual tree with boxes arrows etc"*.
* **Deliverables:**
  * Created `architecture_tree.svg`: High-resolution 4-tier tree diagram showing all branches, models, and components.
  * User requested a simpler view (*"too much details i just want an simple flow of our system from the eyes of an system engineer"*).
  * Created `simple_system_flow.svg`: Minimalist, linear 6-stage systems engineering vector flow (Ingestion -> Air-Gap Gate -> Router -> Local GPU Inference -> Sandbox -> Deliverable Compiler).

### Phase 7: Systems Engineering Audit & "The Real Problem"
* **User Prompt:** *"from the eyes of an systems engineer how tight is our project ? why not 10/10 ?"*
* **Evaluation:** Rated the architecture 9.5/10. Identified three potential gaps to reach 10/10:
  1. Dense blueprint resolution (P&ID tiling).
  2. Multi-user GPU queue UI.
  3. **Self-Correction & Autonomous Error Recovery (The Real Problem).**
* **User Insight:** *"bro for 1 we are just building the system in practical the company will have gpu server they will run any model they want for 2nd same and tell me about 3 i think thats the real problem"*.
* **Deep-Dive:** User correctly recognized that hardware scaling (1 & 2) is solved by datacenter infrastructure, while **autonomous self-correction (3)** is the central software challenge of agentic AI.
* **Architectural Solution:** Designed the 4-step self-healing loop:
  1. Catch `stderr` in isolated sandbox.
  2. Distill the error down to the exact failing line and root cause (no messy 80-line system tracebacks).
  3. Reflection re-prompt with pre-installed library whitelist.
  4. 3-attempt circuit breaker with human-in-the-loop fallback.

### Phase 8: PRD Creation & Refinement
* **Action:** Drafted `PRD.md` v1.0.
* **Review & Critique:** Identified missing functional specs:
  1. Local Knowledge Base & Retrieval (`FR-07: Sovereign RAG` using CPU embeddings to preserve 100% GPU VRAM).
  2. Cryptographic Audit Trail (`FR-08: Tamper-Evident Logging` using SHA-256 hash chains).
  3. Replaced speculative rubric percentage weights with strategic evaluation pillars.
  4. Structured roadmap into Pre-Hackathon Sprints vs. 36-Hour Grand Finale Execution Schedule.
  5. Added Section 10: Failure Mode & Risk Mitigation Matrix.
  6. Added technical justification for Tauri vs. Electron and cleaned LaTeX math notation into clean UTF-8 text.
* **Result:** Updated `PRD.md` to v1.1 — an airtight, production-grade document.

---

## 4. Immediate Next Implementation Roadmap

With the architectural, conceptual, and product requirements phases 100% finalized and documented, the project is ready for active codebase implementation:

```
                          [CODEBASE SCAFFOLDING PLAN]
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
 1. BACKEND ENGINE              2. EXECUTION SANDBOX           3. DESKTOP CLIENT
 • FastAPI (:8000)              • Linux `bwrap` runner         • Tauri Shell (Rust/Web)
 • Ollama model switcher        • Error distillation parser    • mDNS auto-discovery
 • Router heuristic (3B)        • 3-attempt circuit breaker    • Air-Gap Kill Switch UI
 • CPU RAG (Chroma + FastEmbed) • docx / xlsx generators       • P&ID upload & viewer
```

### Next Steps:
1. **Repository Structure Initialization:** Scaffold `/backend` (Python/FastAPI), `/client` (Tauri), and `/shared` (types and protocols).
2. **Local Model Connector:** Build the Ollama client wrapper with automatic `keep_alive: 0` model unloading.
3. **Sandbox Runner:** Implement the Bubblewrap / isolated Python subprocess execution harness with strict timeouts.
4. **Deliverable Engine:** Write the templates for `MRPL_Approval_Note.docx` and `Cost_Matrix.xlsx`.
5. **Air-Gap Sniffer:** Implement the cross-platform network route monitor.
