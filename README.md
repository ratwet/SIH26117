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

## 📂 Repository Structure (Planned)
```
SIH/
├── PROBLEM_STATEMENT_117.md   # Master problem specification, technical architecture & strategy
├── README.md                  # Project overview and documentation entry point
├── backend/                   # FastAPI backend, LangGraph state engine, and tool registry
├── frontend/                  # Modern Next.js / Tailwind CSS industrial workbench UI
├── models/                    # Ollama / vLLM model configuration & quantization scripts
├── sandbox/                   # Isolated local code execution environment
├── telemetry/                 # Real-time socket & eBPF air-gap monitoring service
└── sample_data/               # Public/synthetic P&ID drawings, inspection reports & SOPs
```

---

## 🚀 Quick Reference
- **Problem Statement ID:** SIH26117
- **Ministry / PSU:** Mangalore Refinery and Petrochemicals Limited (MRPL) / ONGC
- **Category:** Software
- **Theme:** Smart Automation
- **SIH Priority Tier:** Tier 1 (Winning Potential: 9.5/10)
