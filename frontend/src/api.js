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
      return {
        status: "OPERATIONAL",
        system: "SovereignWorkbench Node 2 (MOCK)",
        air_gap_verified: true,
        wan_connection: "DISABLED_ISOLATED_SUBNET",
        uptime_seconds: 342.1,
        active_models: {
          router: "qwen2.5:3b-instruct-q8_0",
          reasoning: "deepseek-r1:8b",
          vision: "qwen2-vl:7b-instruct-q4_K_M",
          coder: "qwen2.5-coder:7b-instruct-q4_K_M"
        },
        sandbox_config: {
          timeout_seconds: 15,
          memory_limit_mb: 256,
          max_retries: 3
        }
      };
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
        { delay: 400, type: "thought", payload: { node: "route_task_node", thought: "🧭 Intent Router: Classified task as 'VISION_AUDIT' (Model: qwen2-vl:7b)" } },
        { delay: 1400, type: "thought", payload: { node: "vision_extraction_node", thought: "👁️ Vision Extraction: Found Line Tag 'CDU-2-04-150-A1A' | Actual Thickness = 3.2mm (Nominal = 4.8mm)" } },
        { delay: 2600, type: "thought", payload: { node: "math_generation_node", thought: "📐 Reasoning Engine: DeepSeek-R1 generating deterministic API 570 Python calculation script..." } },
      ];

      if (isErrorScenario) {
        steps.push(
          { delay: 3800, type: "thought", payload: { node: "sandbox_execution_node", thought: "⚠️ Sandbox Execution: Runtime Error caught (ZeroDivisionError on line 4)" } },
          { delay: 4900, type: "thought", payload: { node: "distill_error_node", thought: "🔧 Self-Healing Engine: Distilled traceback -> re-prompting DeepSeek-R1 with diagnostic fix (Attempt 2/3)" } },
          { delay: 6000, type: "thought", payload: { node: "sandbox_execution_node", thought: "⚡ Sandbox Execution: Retry Succeeded (Exit Code 0) | Remaining Life = 3.14 Years" } }
        );
      } else {
        steps.push(
          { delay: 3800, type: "thought", payload: { node: "sandbox_execution_node", thought: "⚡ Sandbox: Execution Success (Exit Code 0) | Remaining Life = 3.14 Years" } }
        );
      }

      steps.push(
        { delay: isErrorScenario ? 6800 : 4800, type: "deliverable", payload: { docx_path: "MRPL_Approval_Note_sim-2026.docx", xlsx_path: "Cost_Matrix_sim-2026.xlsx" } },
        { delay: isErrorScenario ? 7400 : 5400, type: "done", payload: {
            status: "COMPLETED",
            final_response: `### API 570 Mandatory Inspection Finding
- **Plant Unit:** Crude Distillation Unit 2 (CDU-2)
- **Line Tag:** CDU-2-04-150-A1A (Overhead Vapor Line)
- **Nominal Wall Thickness:** 4.80 mm
- **Measured Thickness (UTG):** 3.20 mm
- **Corrosion Rate:** 0.35 mm/year
- **Remaining Safe Operating Life:** **3.14 Years** (Critical Alert: < 5.0 Years Threshold)
- **Statutory Regulatory Action:** **MANDATORY SHUTDOWN REPLACEMENT**
- **Estimated Turnaround Capex Budget:** **INR ₹1,154,400.00**`,
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
            external_gateway_detected: false,
            timestamp: new Date().toLocaleTimeString()
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
        if ((!data.is_air_gapped || data.external_gateway_detected || (data.outbound_wan_bytes_delta > 0)) && onLockdown) {
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
        verification_message: "Tamper-evident SHA-256 hash chain verified (All 22 blocks intact)",
        total_blocks: 22,
        recent_events: [
          { id: 22, timestamp: Date.now() / 1000 - 15, event_type: "deliverable_compilation", model_id: "openpyxl+python-docx", current_hash: "ee20df464db2c67b7e7ebde71f84d299...", status: "success" },
          { id: 21, timestamp: Date.now() / 1000 - 32, event_type: "sandbox_execution", model_id: "bwrap-linux", current_hash: "34b35283d9fff4ff9f0d0be880ca41ad...", status: "success" },
          { id: 20, timestamp: Date.now() / 1000 - 45, event_type: "math_generation", model_id: "deepseek-r1:8b", current_hash: "cfd331b14a2b3c4d5e6f7a8b9012cd34...", status: "success" },
          { id: 19, timestamp: Date.now() / 1000 - 62, event_type: "vision_extraction", model_id: "qwen2-vl:7b", current_hash: "88a1b2c3d4e5f60718293a4b5c6d7e8f...", status: "success" }
        ]
      };
    }
    const res = await fetch(`${BACKEND_URL}/api/telemetry/audit`);
    return await res.json();
  }
};
