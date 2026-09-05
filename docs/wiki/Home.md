# 🛡️ Aquanex — Sovereign On-Premise Agentic AI Workbench

Welcome to the official **Aquanex Knowledge Base & Architecture Wiki**!

**Aquanex** is an enterprise-grade, 100% self-hosted, air-gapped Agentic AI platform built for confidential engineering, statutory compliance, and asset integrity verification in heavy process industries, public sector undertakings (PSUs), and refineries such as **Mangalore Refinery and Petrochemicals Limited (MRPL / ONGC)**.

---

## 📌 Executive Overview & Project Mandate

| Key Dimension | Specification |
| :--- | :--- |
| **Hackathon & Problem ID** | **Smart India Hackathon (SIH) 2026** — Problem Statement **SIH26117** |
| **Client Organization** | **Mangalore Refinery and Petrochemicals Limited (MRPL / MoPNG)** |
| **Theme & Category** | Smart Automation \| Industrial Software Architecture |
| **Verification Status** | ✅ **Production Delivery Ready (40/40 Automated Tests Passing — 100% Pass Rate)** |
| **Data Sovereignty** | **100% Air-Gapped**: Zero telemetry, zero external API dependencies, kernel route kill-switch |
| **Core Architecture** | Stateful Cyclic LangGraph Engine, Bubblewrap Sandbox, 10-Deliverable Compiler Suite |
| **Model Philosophy** | **BYOM (Bring-Your-Own-Model)**: Drop-in open-weights (Ollama Edge / vLLM Datacenter Cluster) |

---

## ⚡ The Industrial Challenge: Why Aquanex Exists

In hydrocarbon refineries and petrochemical complexes, maintaining process piping integrity under statutory mandates (**OISD-STD-118/153**, **API 570**, and **ASME B31.3**) is a life-safety critical requirement. However, plants face a three-fold operational bottleneck:

1. **The 3-Hour Manual Inspection Deadlock:** Engineers spend 2.5 to 3.0 hours per piping circuit manually retrieving P&ID drawings, transcribing ultrasonic thickness gauge readings, calculating short-term and long-term corrosion rates, and drafting executive Word approval notes and Excel Capex budgets.
2. **The "Shadow AI" National Security Threat:** Frustrated by repetitive administrative transcription, field personnel risk pasting confidential piping line tags, operating pressures, and metallurgy into public cloud AI services (ChatGPT, Claude, Copilot)—violating **CERT-In IT Act Section 70B** and **MoPNG Cyber Security Directives** on Critical Information Infrastructure (CII).
3. **The LLM Arithmetic Hallucination Crisis:** Generative AI models operate probabilistically (next-token prediction) and suffer high error rates (>37%) on floating-point engineering arithmetic, risking catastrophic plant failure if relied upon for turnaround decisions.

---

## 🚀 How Aquanex Solves the Problem

Aquanex replaces this fragile workflow with an end-to-end, deterministic agentic pipeline:

```text
[ Physical / PDF P&ID Blueprint ]
               │
               ▼
   [ Visual OCR Extraction Node ] ── (Extracts Line Tag, Schedule, Nominal & Measured Thickness)
               │
               ▼
   [ Statutory Reasoning Engine ] ── (Synthesizes API 570 / ASME B31.3 Deterministic Python Code)
               │
               ▼
   [ Bubblewrap Linux Sandbox ]   ── (Executes in zero-network namespace; auto-corrects on syntax errors)
               │
               ▼
   [ 10-Deliverable Compilers ]   ── (Outputs Word note, Excel Capex, AutoCAD DXF, 3D STL, PDF certificate)
               │
               ▼
   [ Cryptographic Audit Chain ]  ── (Logs immutable SHA-256 forward-linked audit manifest)
```

**Key Result:** Inspection turnaround cut from **3 hours down to 45 seconds per circuit** (**99.58% compute speedup**; >90% operational turnaround reduction) with verifiable mathematical accuracy and **zero outbound WAN bytes**.

---

## 🗺️ Wiki Documentation Index

Explore the detailed engineering specifications across our structured wiki sections:

* 📐 **[[Architecture and LangGraph]]** — Deep-dive into our cyclic state machine, state schema, 8 nodes, and 3-cycle autonomous self-healing recovery loop.
* 🔒 **[[BYOM and Air Gap Security]]** — Bring-Your-Own-Model architecture, Bubblewrap fail-closed sandboxing, and Linux kernel `/proc/net/route` active watchdog.
* 📑 **[[Omni Modal Deliverables]]** — Specification of all 10 publication-ready enterprise files generated without Microsoft Office or Autodesk software.
* 📊 **[[Verification and Benchmarks]]** — Statutory mathematical formulas (API 570 / ASME B31.3), empirical speedup study, and 40/40 test suite breakdown.
* 🚀 **[[Deployment and Operations]]** — Setup guide for Linux Desktop (WebKit2/GTK), 3-node offline physical LAN topology, and diagnostic scripts.

---

## 🏛️ Physical 3-Node Offline LAN Topology

To demonstrate uncompromised sovereignty during live refinery and jury inspections, Aquanex is deployed across three dedicated physical nodes connected through an unmanaged Ethernet switch with **no default gateway**:

```text
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

## 🧪 Quick Test Verification

Verify all 40 unit and integration tests instantly on any Linux workstation:

```bash
# Clone and enter repository
git clone https://github.com/ratwet/SIH26117.git
cd SIH26117

# Run comprehensive test suite
PYTHONPATH=backend python3 -m pytest backend/tests/ -v
# Output: 40 passed in ~3.22s (100% pass rate)
```
