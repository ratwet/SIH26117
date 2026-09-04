# 🤖 Master Prompt for Developer 4's AI Agent
> **Instructions for Developer 4:**  
> Copy and paste the entire block below into your AI coding assistant (Cursor, Claude Code, GitHub Copilot, etc.) in an empty folder or branch.  
> It gives your AI 100% of the project context, backend contracts, design guidelines, and a built-in Mock Engine so you can build and preview the UI immediately!

---

```markdown
# MISSION BRIEF: FRONTEND DESKTOP CLIENT FOR SOVEREIGNWORKBENCH (MRPL REFINERY)

You are the Frontend & Desktop Engineer (Developer 4) for **SovereignWorkbench**, an on-premise, 100% air-gapped Agentic AI system built for Mangalore Refinery and Petrochemicals Limited (MRPL) for Smart India Hackathon 2026 (Problem Statement 117).

## 1. WHAT YOU ARE BUILDING
You are building the **Node 3 User Workbench**: a native desktop application for chemical and plant inspection engineers. The user does not interact with terminal code; they use your desktop UI to:
1. Upload scanned ultrasonic thickness inspection reports and P&ID blueprints.
2. Trigger autonomous agentic audits and watch real-time thoughts stream from the LangGraph state machine.
3. Download executive Word Approval Notes (`.docx`) and Excel Cost Matrices (`.xlsx`).
4. View the live air-gap security status and trigger the **Red Lockdown Screen** if external internet is detected.

## 2. TECH STACK & RESTRICTIONS
- **Framework:** Tauri v2 (or Vite + React / TypeScript / Vanilla HTML5+CSS3+JS).
- **Strict Rule:** **ZERO EXTERNAL CDNs!** The app must work in an isolated room with no internet. All CSS, fonts, and SVG icons must be bundled locally.
- **Design Aesthetic:** High-contrast industrial refinery command center:
  - Background Deep Navy: `#0A0E17`
  - Card/Panel Surface: `#131B2E`
  - Border/Grid: `#1F2D4A`
  - Accent Electric Cyan: `#00F5D4`
  - Status Emerald (Air-gap OK): `#2EC4B6`
  - Warning Amber: `#FFB703`
  - Emergency Crimson (Lockdown): `#EF233C`
  - Monospace font for logs & thoughts (`JetBrains Mono`, `Consolas`, or `monospace`).

---

## 3. UI LAYOUT & USER EXPERIENCE (3-PANEL COMMAND CENTER)

### Header Bar
- Title: `🛡️ SOVEREIGNWORKBENCH — MRPL REFINERY COMMAND CENTER`
- Plant Unit Selector: Dropdown (`Crude Distillation Unit 2 (CDU-2)`, `Vacuum Distillation Unit (VDU)`, `Fluid Catalytic Cracking (FCCU)`).
- Air-Gap Pill: Pulsating green badge `[🟢 AIR-GAP ENFORCED: 0 WAN BYTES]`.
- Mock Mode Toggle: A switch `[🧪 Mock Mode: ON/OFF]` (ON by default so you can test right now!).

### Panel 1: Document Ingestion (Left Column ~25% Width)
- Drag-and-drop file upload zone (accepts `.pdf`, `.png`, `.jpg`).
- Uploaded file preview card with filename, file size, and remove button.
- **Quick Preset Buttons:**
  - `[⚡ Audit CDU-2 Overhead Line]` (Auto-fills prompt: "Audit line CDU-2-04-150-A1A from uploaded UT inspection scan and generate formal executive approval note.")
  - `[🔄 Test Self-Healing Recovery]` (Auto-fills prompt with "[SIMULATE_ERROR]" to show the agent catching a sandbox bug and fixing it on attempt #2).

### Panel 2: Agentic Execution HUD (Center Column ~50% Width)
- Prompt input bar with active submit button.
- **Live Thought Stream Timeline:**
  - As Server-Sent Events (SSE) stream in, render animated cards with badges:
    - `[🧭 ROUTER]` Intent classification ("VISION_AUDIT")
    - `[👁️ VISION]` Parameter extraction ("Line CDU-2-04-150-A1A, actual 3.2mm, nominal 4.8mm")
    - `[📐 REASONING]` DeepSeek-R1 generating deterministic API 570 Python script
    - `[⚡ SANDBOX]` Bubblewrap kernel execution output ("Exit Code 0 | Remaining Life: 3.14 Yrs")
    - `[⚠️ SELF-HEAL]` (If retry count > 0, highlights the distilled error and corrected code)
    - `[📄 COMPILER]` Notification that `.docx` and `.xlsx` deliverables are ready.
- **Final Executive Summary Card:**
  - Prominently displays:
    - Line Tag: `CDU-2-04-150-A1A`
    - Remaining Safe Operating Life: `3.14 YEARS` (Warning badge: `< 5.0 Yrs`)
    - Statutory Action: `MANDATORY SHUTDOWN REPLACEMENT`
    - Estimated Turnaround Budget: `₹1,154,400 INR`

### Panel 3: Deliverables Shelf & Security Audit (Right Column ~25% Width)
- **Deliverables Cards:**
  - `📄 MRPL_Approval_Note_sim-2026.docx` (Word note with official letterhead) $\rightarrow$ Click to Download/Open.
  - `📊 Cost_Matrix_sim-2026.xlsx` (Excel workbook with active formulas) $\rightarrow$ Click to Download/Open.
- **Cryptographic Audit Ledger:**
  - Live table showing latest SHA-256 blocks from SQLite:
    - Block Height (e.g. `#22`)
    - Event Type (`deliverable_compilation`)
    - Hash (`ee20df46...`)
    - Integrity Pill (`VALID ✅`)

### Emergency Red Lockdown Modal (Kill Switch)
- A high-priority full-screen modal that triggers when `is_air_gapped === false` or `external_gateway_detected === true`.
- Shows a glowing crimson warning:
  `🚨 AIR-GAP VIOLATION DETECTED: UNAUTHORIZED WAN GATEWAY ACTIVE`
- Completely freezes all buttons and displays: "Disconnect Wi-Fi / Hotspot to restore Sovereign operations".
- Provide a button in Mock Mode: `[🔥 Simulate Hotspot Breach]` to demonstrate this to evaluators!

---

## 4. BACKEND API CONTRACT & MOCK ENGINE

The backend runs on `http://127.0.0.1:8000`.

### The Endpoints:
1. `POST /api/chat` (multipart/form-data with `prompt`, `user_role`, `files`):
   Streams named Server-Sent Events:
   - `event: connected` -> `data: {"session_id": "...", "status": "PROCESSING"}`
   - `event: thought` -> `data: {"node": "...", "thought": "...", "session_id": "..."}`
   - `event: deliverable` -> `data: {"docx_path": "...", "xlsx_path": "..."}`
   - `event: done` -> `data: {"final_response": "...", "docx_path": "...", "xlsx_path": "...", "status": "COMPLETED"}`
2. `POST /api/files/upload` (multipart with `file`):
   Returns `{"status": "success", "filename": "...", "size_bytes": 12345}`.
3. `GET /api/files/download/{filename}`:
   Downloads the binary `.docx` or `.xlsx` file.
4. `GET /api/telemetry/network/stream`:
   SSE stream emitting `data: {"is_air_gapped": true, "outbound_wan_bytes_delta": 0, "external_gateway_detected": false}` every 1.5s.
5. `GET /api/telemetry/audit`:
   Returns `{"chain_valid": true, "total_blocks": 22, "recent_events": [...]}`.
6. `GET /api/health`:
   Returns `{"status": "OPERATIONAL", "air_gap_verified": true}`.

---

## 5. READY-TO-USE API CLIENT WITH BUILT-IN MOCK MODE

Implement your `api.js` with this exact code so it works both connected to the real backend AND in standalone Mock Mode:

```javascript
// src/api.js - SovereignWorkbench API Client with Full Mock Fallback
const BACKEND_URL = "http://127.0.0.1:8000";
export let USE_MOCK = true; // Toggle to false when connecting to live Python server

export function setMockMode(val) {
  USE_MOCK = val;
}

export const SovereignAPI = {
  // 1. Health Check
  async checkHealth() {
    if (USE_MOCK) {
      return { status: "OPERATIONAL", system: "SovereignWorkbench Node 2 (MOCK)", air_gap_verified: true };
    }
    const res = await fetch(`${BACKEND_URL}/api/health`);
    return await res.json();
  },

  // 2. Upload Document
  async uploadDocument(file) {
    if (USE_MOCK) {
      return {
        status: "success",
        filename: file.name || "CDU_2_UT_Scan_2026.pdf",
        size_bytes: file.size || 1245000,
        file_path: `/data/uploads/${file.name || "CDU_2_UT_Scan_2026.pdf"}`
      };
    }
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BACKEND_URL}/api/files/upload`, { method: "POST", body: formData });
    return await res.json();
  },

  // 3. Streaming Chat (Supports Real SSE + Realistic Mock SSE)
  streamChat({ prompt, userRole = "senior", onThought, onDeliverable, onDone, onError }) {
    if (USE_MOCK) {
      console.log("[MOCK] Starting simulated SSE thought stream for prompt:", prompt);
      const isErrorScenario = prompt.includes("[SIMULATE_ERROR]");
      
      const steps = [
        { delay: 500, type: "thought", payload: { node: "route_task_node", thought: "🧭 Intent Router: Classified task as 'VISION_AUDIT' (Model: qwen2-vl:7b)" } },
        { delay: 1500, type: "thought", payload: { node: "vision_extraction_node", thought: "✅ Vision Extraction: Found Line Tag 'CDU-2-04-150-A1A' | Actual Thickness = 3.2mm (Nominal = 4.8mm)" } },
        { delay: 2800, type: "thought", payload: { node: "math_generation_node", thought: "📐 Reasoning Engine: DeepSeek-R1 generating deterministic API 570 Python calculation script..." } },
      ];

      if (isErrorScenario) {
        steps.push(
          { delay: 3800, type: "thought", payload: { node: "sandbox_execution_node", thought: "⚠️ Sandbox Execution: Runtime Error caught (ZeroDivisionError on line 4)" } },
          { delay: 4800, type: "thought", payload: { node: "distill_error_node", thought: "🔧 Self-Healing Engine: Distilled traceback -> re-prompting DeepSeek-R1 with diagnostic fix (Attempt 2/3)" } },
          { delay: 6000, type: "thought", payload: { node: "sandbox_execution_node", thought: "✅ Sandbox Execution: Retry Succeeded (Exit Code 0) | Remaining Life = 3.14 Years" } }
        );
      } else {
        steps.push(
          { delay: 4000, type: "thought", payload: { node: "sandbox_execution_node", thought: "✅ Sandbox: Execution Success (Exit Code 0) | Remaining Life = 3.14 Years" } }
        );
      }

      steps.push(
        { delay: isErrorScenario ? 7000 : 5000, type: "deliverable", payload: { docx_path: "MRPL_Approval_Note_sim-2026.docx", xlsx_path: "Cost_Matrix_sim-2026.xlsx" } },
        { delay: isErrorScenario ? 7500 : 5500, type: "done", payload: {
            status: "COMPLETED",
            final_response: `### API 570 Inspection Finding
- **Line Tag:** CDU-2-04-150-A1A (Crude Distillation Column Overhead)
- **Corrosion Rate:** 0.35 mm/year
- **Remaining Safe Operating Life:** 3.14 Years (< 5.0 Years Threshold)
- **Mandatory Action:** **SCHEDULE SHUTDOWN REPLACEMENT**
- **Estimated Turnaround Budget:** INR ₹1,154,400.00`,
            docx_path: "MRPL_Approval_Note_sim-2026.docx",
            xlsx_path: "Cost_Matrix_sim-2026.xlsx"
          }
        }
      );

      steps.forEach(({ delay, type, payload }) => {
        setTimeout(() => {
          if (type === "thought" && onThought) onThought(payload);
          if (type === "deliverable" && onDeliverable) onDeliverable(payload);
          if (type === "done" && onDone) onDone(payload);
        }, delay);
      });
      return;
    }

    // REAL BACKEND SSE PARSER
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("user_role", userRole);

    fetch(`${BACKEND_URL}/api/chat`, { method: "POST", body: formData })
      .then(async (response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split("\n\n");
          buffer = events.pop();

          for (const raw of events) {
            if (!raw.trim()) continue;
            const lines = raw.split("\n");
            let eventType = "message";
            let dataStr = "";
            for (const l of lines) {
              if (l.startsWith("event:")) eventType = l.replace("event:", "").trim();
              if (l.startsWith("data:")) dataStr = l.replace("data:", "").trim();
            }
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (eventType === "thought" && onThought) onThought(data);
              if (eventType === "deliverable" && onDeliverable) onDeliverable(data);
              if (eventType === "done" && onDone) onDone(data);
            } catch (err) {
              console.warn("SSE parse error:", err);
            }
          }
        }
      })
      .catch((err) => { if (onError) onError(err); });
  },

  // 4. Download Deliverable URL
  getDownloadUrl(filename) {
    if (USE_MOCK) return `#mock-download-${filename}`;
    return `${BACKEND_URL}/api/files/download/${encodeURIComponent(filename)}`;
  },

  // 5. Network Telemetry Stream
  listenToTelemetry({ onTelemetry, onLockdown }) {
    if (USE_MOCK) {
      const interval = setInterval(() => {
        if (onTelemetry) {
          onTelemetry({
            is_air_gapped: true,
            outbound_wan_bytes_delta: 0,
            active_local_connections: 3,
            external_gateway_detected: false
          });
        }
      }, 1500);
      return { close: () => clearInterval(interval) };
    }

    const eventSource = new EventSource(`${BACKEND_URL}/api/telemetry/network/stream`);
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onTelemetry) onTelemetry(data);
        if ((!data.is_air_gapped || data.external_gateway_detected) && onLockdown) {
          onLockdown(data);
        }
      } catch (e) {
        console.error("Telemetry parse error:", e);
      }
    };
    return eventSource;
  },

  // 6. Audit Chain
  async getAuditLedger() {
    if (USE_MOCK) {
      return {
        chain_valid: true,
        verification_message: "Mock audit chain verified.",
        total_blocks: 22,
        recent_events: [
          { id: 22, event_type: "deliverable_compilation", model_id: "openpyxl+python-docx", current_hash: "ee20df464db2c67b7e7ebde7...", status: "success" },
          { id: 21, event_type: "sandbox_execution", model_id: "bwrap-linux", current_hash: "34b35283d9fff4ff9f0d0be8...", status: "success" },
          { id: 20, event_type: "math_generation", model_id: "deepseek-r1:8b", current_hash: "cfd331b14a2b3c4d5e6f7a8b...", status: "success" },
        ]
      };
    }
    const res = await fetch(`${BACKEND_URL}/api/telemetry/audit`);
    return await res.json();
  }
};
```

---

## 6. YOUR STEP-BY-STEP ACTION PLAN

1. **Scaffold Project:**
   Create a clean, responsive layout using Vite (React or Vanilla JS).
2. **Implement the 3-Panel Grid:**
   Follow the design tokens and layout defined in Section 3.
3. **Wire `api.js`:**
   Drop the client code from Section 5 into `src/api.js`.
4. **Test the "WOW" Demo Moments in Mock Mode:**
   - Click `[⚡ Audit CDU-2 Overhead Line]` -> Watch the thought stream populate, see remaining life calculate (3.14 yrs), and see download cards appear.
   - Click `[🔄 Test Self-Healing Recovery]` -> See the agent catch a sandbox bug and recover automatically!
   - Click `[🔥 Simulate Hotspot Breach]` -> Watch the screen turn red with the Air-Gap Lockdown Modal!
5. **Package for Desktop:**
   Run `npm run tauri dev` or `cargo tauri dev` to package as a native desktop application.

Now execute and build the UI!
```
