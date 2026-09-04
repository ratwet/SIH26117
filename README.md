# SIH 2026 — Project SovereignWorkbench (PS 117)

> **Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work**  
> **Problem Statement ID:** SIH26117 | **Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL) | **Theme:** Smart Automation

---

## 📌 Project Overview
**SovereignWorkbench** is a 100% self-hosted, air-gapped agentic AI platform tailored for refineries, PSUs, and defense-linked manufacturing enterprises. Built entirely on open-weight multimodal foundation models, it empowers industrial engineers to automate sensitive knowledge work—such as P&ID technical drawing audits, failure analysis calculations, and formal executive approval dossiers—with **verifiable zero cloud exfiltration**.

For the complete technical breakdown, architecture specifications, and evaluation rubric:  
👉 **[Read the Full Problem Statement 117 Master Dossier](./PROBLEM_STATEMENT_117.md)**

---

## ⚡ Key Highlights & Capabilities
- **100% Air-Gapped & Sovereign:** Absolute local execution with zero internet connectivity. Includes an active eBPF/kernel socket telemetry HUD proving zero outbound WAN bytes.
- **Dynamic Multi-Model Auto-Routing:** Intelligently routes tasks to specialized open-weight models (Qwen-2.5-Coder for code, DeepSeek-R1 for reasoning/math, Qwen2-VL for P&ID schematics and scanned notes).
- **Autonomous Agentic Workflow:** Multi-step planning, reflection, and error-recovery via LangGraph state machines.
- **Industrial Tooling & Code Sandbox:** Deterministic execution of engineering formulas in an isolated Python sandbox (`bwrap`/Docker).
- **Publication-Ready Enterprise Artifacts:** Automatically drafts formal executive approval notes (`.docx`), engineering cost/risk workbooks (`.xlsx`), and presentation decks (`.pptx`).
- **Sovereign Industrial RAG:** Grounded locally against plant SOPs, historical inspection notes, and OISD/API standards using local vector embeddings (ChromaDB + BAAI/BGE).

---

## 📂 Repository Structure
```text
SIH/
├── README.md                      # Project overview and documentation entry point
├── LICENSE.md                     # Proprietary license
├── PROBLEM_STATEMENT_117.md       # Master problem specification & requirements
├── PRD.md                         # Product Requirements Document
├── TEAM_CONTEXT.md                # 3-node LAN physical layout & team context guide
├── aquanex.desktop                # FreeDesktop GNOME/KDE application launcher
├── backend/                       # FastAPI gateway, LangGraph state engine & tools
│   ├── app/                       # Core engine (api, graph, sandbox, compilers, rag, security)
│   └── tests/                     # Comprehensive test suite (16/16 passing)
├── frontend/                      # Aquanex UI & cross-platform desktop client
│   ├── src/                       # Vanilla CSS/JS air-gapped web client (0 CDN dependencies)
│   └── src-tauri/                 # Tauri v2 native desktop shell (Windows, Linux, macOS)
├── scripts/                       # Deployment, networking & verification scripts
│   ├── install_desktop_entry.sh   # Installs launcher to Linux application menu
│   ├── launch_aquanex.sh          # Native desktop client launcher wrapper
│   ├── run_linux_desktop.py       # GTK 3.0 + WebKit2 native window runner
│   ├── setup_lan_nodes.sh         # Offline 3-node Netplan network configuration
│   ├── start_workbench.sh         # Ollama and backend daemon starter
│   └── verify_sovereignty.sh      # Zero-egress network verification sniffer
└── docs/                          # Clean project documentation architecture
    ├── specs/                     # Developer specifications & AI agent handoff prompts
    ├── reports/                   # Implementation reports & local wiki drafts
    ├── presentation/              # SIH pitch dossier & presentation template
    └── diagrams/                  # System architecture & process flow SVG diagrams
```

---

## 🚀 Quick Reference
- **Problem Statement ID:** SIH26117
- **Ministry / PSU:** Mangalore Refinery and Petrochemicals Limited (MRPL) / ONGC
- **Category:** Software
- **Theme:** Smart Automation
- **SIH Priority Tier:** Tier 1 (Winning Potential: 9.5/10)
