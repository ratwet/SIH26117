# 🔒 BYOM & Air-Gap Security Architecture

Security and data sovereignty are the foundational pillars of Aquanex. In industrial refining complexes, engineering blueprints (P&IDs) and pipe wear data are classified as **Critical Information Infrastructure (CII)** under Indian cyber laws. Aquanex enforces defense-in-depth security across compute, kernel, and network layers.

---

## 🤖 Bring-Your-Own-Model (BYOM) Architecture

Unlike SaaS AI platforms that lock organizations into proprietary cloud APIs, Aquanex is strictly **model-agnostic**. The platform provides a unified inference abstraction layer that allows refineries to deploy their choice of open-weight models or private fine-tunes without code changes.

```text
               +-------------------------------------------------+
               |              Aquanex Agentic Engine             |
               +-------------------------------------------------+
                                        │
                                        ▼
               +-------------------------------------------------+
               |     Unified Foundation Model Gateway (engine.py)|
               +-------------------------------------------------+
                                        │
                     ┌──────────────────┴──────────────────┐
                     │ (Edge Deployment)                   │ (Datacenter Cluster)
                     ▼                                     ▼
        +-------------------------+           +-------------------------+
        |   Local Ollama Engine   |           |    vLLM Cluster / GPU   |
        |   http://127.0.0.1:11434|           |    http://127.0.0.1:8001|
        +-------------------------+           +-------------------------+
        | • 3B/8B Open-Weights    |           | • 70B/100B+ Foundation  |
        | • CPU / RTX Laptop      |           | • Multi-GPU Enterprise  |
        | • Qwen / DeepSeek /     |           | • High-Throughput vLLM  |
        |   Llama / Mistral       |           |   OpenAI-compatible API |
        +-------------------------+           +-------------------------+
```

### Key Principles of BYOM:
1. **Zero Vendor Lock-In:** Standardized on OpenAI-compatible API schemas and Ollama REST protocols.
2. **Fail-Fast Integrity:** If no model engine is online, Aquanex immediately returns a clean `503 Service Unavailable` with diagnostic guidance rather than hallucinating mock data.
3. **Model-Agnostic UI:** Natural language status feeds ("Thinking...", "Vision Extraction...", "Reasoning Engine...") keep the user experience seamless and professional regardless of which underlying weights are serving inference.

---

## 🛡️ Hardened Linux Bubblewrap (`bwrap`) Sandboxing

All untrusted engineering calculation scripts generated during the agentic cycle are executed inside **Linux Bubblewrap** container namespaces.

```text
+---------------------------------------------------------------------------------+
|                       Host Operating System (Linux Kernel)                      |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                 Bubblewrap Isolated Namespace Container                 |   |
|   |                                                                         |   |
|   |  • Network Stack:       DISABLED (--unshare-net)                        |   |
|   |  • Filesystem:          READ-ONLY (--ro-bind /usr, /lib, /bin, sys.pfx) |   |
|   |  • Temp Directory:      EPHEMERAL RAM DISK (--dir /tmp --tmpfs /tmp)    |   |
|   |  • Memory Limit:        256 MB (setrlimit RLIMIT_AS)                    |   |
|   |  • Execution Timeout:   5.0 Seconds (SIGKILL on overrun)                |   |
|   |  • System Access:       NO /etc write, NO /home write, NO device nodes  |   |
|   |                                                                         |   |
|   |                     [ Deterministic Python Script ]                     |   |
|   +-------------------------------------------------------------------------+   |
|                                         │                                       |
|                  Socket / Egress Attempt ──> Kernel EPERM                       |
+---------------------------------------------------------------------------------+
```

### Sandboxing Enforcements:
* **`--unshare-net`:** Completely removes network interfaces from the container's Linux namespace. Any attempt to create raw sockets or initiate outbound HTTP calls triggers an immediate kernel-level `EPERM` (*Operation not permitted*).
* **Strict Fail-Closed Setting:** In [`backend/app/config.py`](backend/app/config.py), `ALLOW_UNSANDBOXED_FALLBACK` is strictly defaulted to `False`. If Bubblewrap is unavailable, execution fails closed rather than running unconfined on the host.
* **Kernel Memory Ceilings:** Python scripts have their address space bounded to 256MB (`RLIMIT_AS`) preventing memory-exhaustion denial of service attacks.
* **Process Lifetime Watchdog:** A strict 5.0-second timeout ensures infinite loops or stalled calculations are terminated immediately via `SIGKILL`.

---

## 🚨 Active Kernel Route Watchdog & Reactive Kill-Switch

To guarantee compliance with **MoPNG** and **CERT-In Section 70B** guidelines, Aquanex features an active network watchdog that constantly monitors network routing and physical interface changes:

```text
       [ Kernel /proc/net/route ]  +  [ Active Socket Probes ]
                                 │
                                 ▼
              [ Background Network Monitor Daemon ]
                                 │
           Is Public WAN Reachable / Gateway Present?
                            /          \
                      [NO]              [YES]
                        │                 │
                        ▼                 ▼
               🟢 System Operates    🔴 INSTANT HARD LOCKDOWN
                  Normally           • All APIs return HTTP 403
                                     • Model inference aborted
                                     • UI displays Emergency Modal
                                     • Audio/Visual alarm triggered
                                     • Audit log records breach
```

### Watchdog Capabilities:
1. **Intelligent Reachability vs Local Subnet:** Active non-blocking socket probes differentiate between clean local offline Wi-Fi (e.g. connecting wirelessly to an on-premise GPU workstation) and true public Internet connectivity.
2. **Sub-50ms Trip Latency:** Detects unauthorized 4G/5G USB modems, Wi-Fi tethering, or accidental Ethernet patch cords within milliseconds.
3. **SSE Telemetry Streaming:** Live network metrics (bytes sent, bytes received, connection state) stream continuously to the frontend via `/api/telemetry/network/stream`.
4. **Autonomous Self-Recovery:** When the unauthorized WAN connection is unplugged or Airplane Mode is toggled, the system detects the cleared routing table and automatically restores operations within 1.5 seconds.

---

## 📜 Cryptographic SHA-256 Audit Ledger

Every execution cycle in Aquanex generates an immutable, forward-chained cryptographic audit record maintained in [`backend/app/security/audit_chain.py`](backend/app/security/audit_chain.py):

```json
{
  "index": 42,
  "timestamp": "2026-09-06T00:54:12.184Z",
  "action": "API_570_INSPECTION_AUDIT",
  "line_tag": "CDU-2-04-150-A1A",
  "calculated_remaining_life": 3.14,
  "mandatory_shutdown": true,
  "deliverables_hashes": {
    "Inspection_Certificate.pdf": "8f4a1b8c...",
    "Approval_Note.docx": "2e9c4d7a...",
    "Cost_Matrix.xlsx": "a1f3c9e4...",
    "Piping_Spool.dxf": "d4e8b2a1..."
  },
  "previous_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "entry_hash": "5f1a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
}
```

* **Tamper Evidence:** Altering any historical entry invalidates all subsequent hashes in the chain, providing mathematically verifiable non-repudiation for regulatory auditors (OISD / CERT-In).
