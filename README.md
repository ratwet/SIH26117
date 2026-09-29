<div align="center">

# Aquanex

**Sovereign On-Premise AI Workbench for Confidential Industrial Operations**

[![Tests](https://img.shields.io/badge/tests-58%2F58%20passing-brightgreen?style=flat-square)](backend/tests/)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE.md)

A fully air-gapped, self-hosted AI platform that runs open-weight LLMs on-premise — designed for industrial environments where data **never leaves the network**.

[Architecture](ARCHITECTURE.md) · [Documentation](docs/wiki/Home.md) · [Q&A Guide](docs/guides/PROJECT_QNA_GUIDE.md) · [PRD](PRD.md)

</div>

---

## Problem

Critical infrastructure organizations — refineries, power plants, defense facilities — handle classified engineering documents (P&IDs, inspection reports, equipment schematics) that **cannot be sent to public cloud AI services** due to regulatory and security constraints.

Existing solutions force a choice: use powerful AI but leak data, or keep data safe but lose AI capabilities.

**Aquanex eliminates this trade-off.** It delivers production-grade AI capabilities on a fully isolated local network with zero outbound data transfer — verified and enforced at the kernel level.

> **Built for:** [Smart India Hackathon 2026](https://sih.gov.in) — Problem Statement SIH26117  
> **Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL / ONGC)

---

## Key Features

### Air-Gap Enforcement
- Active WAN reachability probing via kernel socket telemetry
- Automatic lockdown (`HTTP 403`) when outbound internet is detected
- Real-time SSE alerts to all connected clients
- Autonomous recovery within 1.5 seconds of WAN disconnection

### Three Dedicated Workstation Personas
| Persona | Purpose |
|:--------|:--------|
| **Field Engineer** | Minimalist chat interface for UT thickness logging, formula verification, and remaining life estimation |
| **Senior Reliability Lead** | Full dossier builder — generates approval notes, cost matrices, pitch decks, DXF drawings, and 3D CAD meshes |
| **IT Admin Control Center** | Governance dashboard with live LAN topology, GPU VRAM monitoring, SHA-256 audit ledger, and air-gap kill-switch |

### 10-Deliverable Generation Suite
Autonomously compiles statutory inspection deliverables from a single conversation:

| # | Output | Format |
|---|--------|--------|
| 1 | Inspection Certificate | PDF |
| 2 | Executive Approval Note | DOCX |
| 3 | Capex Cost Matrix | XLSX |
| 4 | Board Pitch Deck | PPTX |
| 5 | Piping Spool Drawing | DXF |
| 6 | 3D Printable Manifold | STL |
| 7 | Corrosion Heatmap | PNG |
| 8 | UT Thickness Survey | CSV |
| 9 | API 570 Calculation Script | PY |
| 10 | Cryptographic Audit Manifest | JSON |

### Sandboxed Code Execution
- Bubblewrap (`bwrap`) isolation with read-only system mounts and memory ceilings
- Cyclic self-healing: captures errors and feeds them back to the LLM for autonomous correction (up to 3 retries)

### Cryptographic Audit Ledger
- SHA-256 chained blocks in an append-only SQLite database
- Every prompt, response, sandbox exit code, and deliverable hash is recorded
- One-click chain integrity verification

### Plug-and-Play Model Backend
- Model-agnostic — works with any Ollama or vLLM compatible model out of the box
- Users choose which open-weight LLM to run based on their available hardware
- Zero application-level configuration required to switch models

---

## Architecture

```
                          [ ISOLATED LAN SWITCH ]
                          (192.168.1.0/24 — No WAN)
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
   ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
   │  SERVER      │          │  ADMIN       │          │  WORKBENCH   │
   │  :8000       │          │  :8001       │          │  :8002       │
   ├──────────────┤          ├──────────────┤          ├──────────────┤
   │ FastAPI      │          │ Audit Ledger │          │ Web UI (Vite)│
   │ LangGraph    │          │ Kill-Switch  │          │ GTK Desktop  │
   │ Sandbox      │          │ Node Monitor │          │ 3 Personas   │
   │ ChromaDB RAG │          │              │          │              │
   │ Ollama/vLLM  │          │              │          │              │
   └──────────────┘          └──────────────┘          └──────────────┘
```

> Full technical specification → [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Quickstart

### Prerequisites

- Linux (Ubuntu 22.04+, Fedora 38+, or RHEL 9+)
- Python 3.10+
- Node.js 18+ & npm
- [Ollama](https://ollama.ai) or [vLLM](https://vllm.ai) running locally

### Setup

```bash
# Clone
git clone https://github.com/ratwet/SIH26117.git
cd SIH26117

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env

# Frontend
cd frontend && npm install && npm run build && cd ..

# Run
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access

| Persona | URL |
|:--------|:----|
| Field Engineer | `http://localhost:8000/?persona=junior&standalone=1` |
| Senior Lead | `http://localhost:8000/?persona=senior&standalone=1` |
| Admin Control | `http://localhost:8000/?persona=admin&standalone=1` |

Native Linux desktop apps:
```bash
python3 scripts/run_linux_desktop.py --persona junior
python3 scripts/run_linux_desktop.py --persona senior
python3 scripts/run_linux_desktop.py --persona admin
```

---

## Testing

```bash
PYTHONPATH=backend python -m pytest backend/tests/ -v
```

**58 tests passing** across 5 test modules:

| Module | Coverage |
|:-------|:---------|
| `test_audit_fixes.py` | Sandbox mounts, RAG grounding, RBAC, CORS |
| `test_dev1_graph.py` | LangGraph state machine transitions, streaming |
| `test_dev2_tools.py` | Bubblewrap execution, error parsing, deliverables |
| `test_omni_modal_100b.py` | 10-deliverable compilation, scaling, fail-fast |
| `test_sovereign_hardened.py` | Air-gap kill-switch, HMAC tokens, ledger chaining |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # REST & SSE routers
│   │   ├── compilers/        # Deliverable generators (PDF, DOCX, XLSX, DXF, STL…)
│   │   ├── graph/            # LangGraph state machine & self-healing engine
│   │   ├── llm/              # Model gateway with auto-discovery
│   │   ├── rag/              # Sovereign RAG (FastEmbed + ChromaDB)
│   │   ├── sandbox/          # Bubblewrap Linux sandbox
│   │   ├── security/         # Network monitor & SHA-256 audit ledger
│   │   └── main.py           # Application entrypoint
│   └── tests/                # Test suite (58 tests)
├── frontend/
│   ├── src/                  # Vite + Vanilla JS client
│   └── src-tauri/            # Tauri v2 native wrapper
├── deploy/                   # Linux packaging & .desktop entries
├── docs/                     # Wiki, diagrams, specs, research
├── scripts/                  # Deployment & networking utilities
├── ARCHITECTURE.md
├── PRD.md
└── .env.example
```

---

## Team Aquanex

| Name | Role |
|:-----|:-----|
| **Rajat** | Orchestration & API — LangGraph state machine, SSE streaming, model gateway |
| **Anand** | Deterministic Tools — Bubblewrap sandbox, deliverable compilers, RAG engine |
| **Kaushal** | GPU & Deployment — Ollama/vLLM integration, multi-tier model configuration |
| **Naveen** | Frontend & Desktop — UI system, persona apps, GTK desktop client, air-gap lockdown |
| **Divij** | AI & Model Integration — Prompt engineering, LLM evaluation, agentic workflow design |
| **Sakshi** | Full-Stack & Desktop — Frontend components, backend API routes, native desktop packaging |

---

## License

[MIT](LICENSE.md) — Built for [Smart India Hackathon 2026](https://sih.gov.in), Problem Statement SIH26117.
