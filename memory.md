# Project Memory (`memory.md`)

## 1. System Identity & Core Tenets
* **Project Name:** SovereignWorkbench
* **Competition / Track:** Smart India Hackathon (SIH) 2026 — Theme: Smart Automation
* **Problem Statement:** PS 117 (SIH26117) — *Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work*
* **Client / Ministry:** Mangalore Refinery and Petrochemicals Limited (MRPL) / Ministry of Petroleum and Natural Gas (MoPNG)
* **Core Analogy:** **The Base Model is an Engine on the Garage Floor; SovereignWorkbench is the Complete Operating Vehicle.** The model provides passive probability; our agentic harness provides hands (tools), eyes (vision), memory (RAG), safety interlocks (kill switch), and deterministic execution (isolated Python sandbox).

---

## 2. User Directives, Preferences & Rules
1. **Communication Style:** Clear, direct, basic English. Avoid unnecessary academic jargon or overly dense buzzwords. Focus on practical systems engineering reality.
2. **Document Specifications:**
   * LaTeX documents must use `geometry` package with `a4paper` and **strict 1cm margins** on all sides (`\usepackage[a4paper, margin=1cm]{geometry}`).
   * Keep paragraphs clean and readable without excessive decorative frames or filler boxes.
3. **No Cloud / 100% Air-Gap Mandate:**
   * Zero external API calls. Zero phoning home.
   * Chemical engineer and server laptops operate in a strictly air-gapped subnet.
   * If external internet (Wi-Fi/4G dongle) is detected on the engineer workstation, an **Air-Gap Interlock (Kill Switch)** immediately triggers a red lock screen to prevent data leaks.
4. **Physical Deployment Setup (The 3-Laptop Rig):**
   * **Laptop 1 (IT Admin):** Connects to corporate zone to download open weights (`.gguf`); assigns RBAC tiers (Junior vs Senior), verifies SHA-256 hashes, monitors audit logs.
   * **Laptop 2 (Gaming Laptop / Central Server):** Houses the GPU (RTX 3060/4060, 6–12GB VRAM), runs Ollama (`OLLAMA_NO_UPDATE=1`), FastAPI orchestrator (`:8000`), CPU-based RAG, and isolated sandbox. Broadcasts via mDNS as `mrpl-server.local`.
   * **Laptop 3 (Chemical Engineer Workstation):** Standard user laptop running a native cross-platform desktop application. Auto-discovers server with zero IP configuration.
5. **No Browser-Only Fallback for End Users:**
   * The client must be a **native installed desktop application** packaged via **Tauri** (`.exe` for Windows, `.AppImage` for Linux, `.dmg` for macOS).
   * Rationale for Tauri: Sub-15MB binary and ~40MB RAM usage vs. Electron's 150MB+ bundle and 300MB+ RAM overhead.
6. **Zero-Hallucination Math Rule:**
   * The LLM must **never** perform safety-critical engineering arithmetic (e.g., API 570 remaining life, MAWP, corrosion rates) directly in token generation.
   * It must formulate and write Python scripts executed deterministically inside an isolated sandbox.
7. **The Real Problem (Self-Healing Loop):**
   * The agent must have an autonomous error recovery loop: Sandbox execution -> intercept `stderr` -> error distillation (extracting failing line/cause) -> reflection re-prompt -> 3-attempt circuit breaker -> human-in-the-loop fallback if all retries fail.

---

## 3. Technology Stack & Component Choices

| Subsystem | Technology Selected | Rationale / Key Parameters |
| :--- | :--- | :--- |
| **Local Model Engine** | **Ollama** | Native C++ (`llama.cpp`), `mmap()` zero-copy weight loading from NVMe, sub-2s model swapping, offline flag `OLLAMA_NO_UPDATE=1`. |
| **Backend Orchestration** | **FastAPI (Python 3.11+)** | Asynchronous, lightweight, native Pydantic schema validation, SSE (Server-Sent Events) for token streaming. |
| **Task Router Model** | `Qwen-2.5-3B-Instruct` (Q8_0) | ~3.5GB VRAM, sub-100ms intent classification and schema decomposition. |
| **Reasoning & Math Model** | `DeepSeek-R1-Distill-Qwen-8B` (Q4_K_M)| ~5.4GB VRAM, chain-of-thought derivation for API 570 standards and Python code synthesis. |
| **Vision Model** | `Qwen2-VL-7B-Instruct` (Q4_K_M) | ~5.2GB VRAM, technical drawing OCR, P&ID line tag extraction, symbol parsing. |
| **Deterministic Code Model**| `Qwen-2.5-Coder-7B-Instruct` (Q4_K_M) | ~4.8GB VRAM, strict Python calculation script generation. |
| **Local RAG Embedding** | `bge-small-en-v1.5` via ONNX/FastEmbed | **CPU-only execution (0 MB GPU VRAM hit)**, reserving 100% of GPU memory for LLM inference. |
| **Vector Storage** | **ChromaDB / SQLite-vec** | Embedded, serverless local disk persistence, zero external database daemon required. |
| **Execution Sandbox** | **Linux `bwrap` (Bubblewrap)** | Lightweight kernel namespace isolation: `--unshare-net` (no network), read-only root mount, 5s timeout, 256MB RAM cap. |
| **Desktop Client Shell** | **Tauri (Rust + HTML/JS/CSS)** | Cross-platform (`.exe`, `.AppImage`, `.dmg`), native file dialogs, zero-dependency distribution. |
| **Network Discovery** | **mDNS (Multicast DNS)** | Broadcasts `mrpl-server.local` over offline Wi-Fi/Hotspot; eliminates manual IP entry. |
| **Deliverable Compilers** | `python-docx` & `openpyxl` | Formatted **`.docx`** with MRPL letterhead/sign-off blocks and **`.xlsx`** with live formulas. |
| **Audit Trail** | **SQLite + SHA-256 Hash Chain** | Immutable append-only cryptographic ledger (`mrpl_audit.db`) recording all model actions and kill switch trips. |

---

## 4. Hardware Sizing & Memory Budget (Gaming Laptop Target)

* **Target GPU:** NVIDIA GeForce RTX 3060 / 4060 Mobile (6GB or 8GB VRAM)
* **VRAM Ceiling:** Strictly $\le 5.5\text{ GB}$ peak allocation.
* **Residency Strategy:** Sequential dynamic model swapping via Ollama's `keep_alive: 0` offload flag:
  1. *Router (3B):* Loads, classifies intent, generates plan $\rightarrow$ unloads.
  2. *Vision (7B):* Loads, parses P&ID image/PDF $\rightarrow$ unloads.
  3. *Reasoning (8B):* Loads, synthesizes formulas and Python script $\rightarrow$ unloads.
  4. *Sandbox:* CPU execution (0 VRAM).
  5. *Deliverable Compiler:* CPU execution (0 VRAM).
* **Result:** No out-of-memory (OOM) crashes, fast generation speeds (50–80 tok/s).

---

## 5. Security & Air-Gap Defense Strategy
* **Physical Isolation:** Run over an offline Wi-Fi hotspot or router with the WAN/Ethernet uplink cable physically unplugged.
* **Kernel Route Polling:** Client monitors local network adapters every 2 seconds. If a gateway to public WAN or external DNS responds $\rightarrow$ Emergency Red Screen lockdown.
* **Socket Telemetry HUD:** Visual gauge on the client streaming `/proc/net/dev` and `/proc/net/tcp` counters to prove **0 outbound WAN bytes** live to evaluators.
* **Package Whitelist:** In the sandbox, strictly restrict Python imports to `['math', 'numpy', 'scipy', 'pandas', 'openpyxl', 'docx']`. Block all attempted system calls.

---

## 6. Live Hackathon Presentation Script (The 10/10 "WOW" Moments)
1. **The Physical 3-Laptop Layout:** Evaluators see IT Admin laptop, central GPU gaming laptop, and engineer client laptop working across an offline hotspot with no internet cable.
2. **The High-Stakes Industrial Scenario:** Upload a real CDU-2 crude unit ultrasonic inspection log and P&ID drawing.
3. **The Deliberate Bug & Self-Healing:** The script encounters a missing baseline thickness in the scan $\rightarrow$ throws an error in the sandbox $\rightarrow$ agent catches it, re-reads page 2, fixes the code, and computes the 3.1-year remaining life on attempt #2.
4. **The Physical Artifact:** Click "Save Deliverable" $\rightarrow$ opens a formatted, signable `.docx` Approval Note and `.xlsx` Cost Matrix directly on the engineer's laptop.
5. **The Live Kill Switch Demonstration:** Presenter turns on a 4G mobile hotspot on the client laptop $\rightarrow$ app instantly locks down with a red warning screen $\rightarrow$ hotspot turned off $\rightarrow$ app restores green operational state.
