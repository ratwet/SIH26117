// src/api.js - SovereignWorkbench API Client
// Strict Sovereign Air-Gapped Architecture (Zero Fake Emulation, Zero WAN Exfiltration)

export const DEFAULT_LOCAL_URL = "http://127.0.0.1:8000";
export const DEFAULT_LAN_URL = "http://192.168.1.100:8000";

export function getInitialBackendUrl() {
  if (typeof window !== "undefined") {
    // If loaded directly from a FastAPI server running locally or on LAN
    if (window.location.origin && window.location.origin.startsWith("http") && (window.location.port === "8000" || window.location.port === "80")) {
      return window.location.origin;
    }
    const saved = localStorage.getItem("sovereign_backend_url");
    if (saved) {
      return saved.startsWith("http://") || saved.startsWith("https://") ? saved : `http://${saved}`;
    }
    const hostname = window.location.hostname;
    if (hostname === "localhost" || hostname === "127.0.0.1" || hostname === "") {
      return DEFAULT_LOCAL_URL;
    }
    if (hostname === "192.168.1.100") {
      return `http://${hostname}:8000`;
    }
  }
  return DEFAULT_LOCAL_URL;
}

let currentBackendUrl = getInitialBackendUrl();

export function getBackendUrl() {
  return currentBackendUrl;
}

export function setBackendUrl(url) {
  if (!url) return currentBackendUrl;
  let formatted = url.trim().replace(/\/+$/, "");
  if (!formatted.startsWith("http://") && !formatted.startsWith("https://")) {
    formatted = `http://${formatted}`;
  }
  currentBackendUrl = formatted;
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("sovereign_backend_url", currentBackendUrl);
  }
  return currentBackendUrl;
}

export function getServerIP() {
  return getBackendUrl().replace(/^https?:\/\//, '');
}

export const USE_MOCK = false;

export const SovereignAPI = {
  // 1. Health Check
  async checkHealth(targetUrl = null) {
    const baseUrl = targetUrl ? targetUrl.trim().replace(/\/+$/, "") : getBackendUrl();
    const res = await fetch(`${baseUrl}/api/health`);
    if (!res.ok) {
      throw new Error(`Health check failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  // 2. Immediate Network Telemetry Probe
  async getNetworkStatus(targetUrl = null) {
    const baseUrl = targetUrl ? targetUrl.trim().replace(/\/+$/, "") : getBackendUrl();
    const res = await fetch(`${baseUrl}/api/telemetry/network`);
    if (!res.ok) {
      throw new Error(`Network probe failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  // 3. Upload Document
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${getBackendUrl()}/api/files/upload`, { method: "POST", body: formData });
    if (!res.ok) {
      throw new Error(`File upload failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  // 4. Streaming Chat with Live SSE
  async streamChat({ prompt, userRole = "senior", files = [], onConnected, onThought, onDeliverable, onDone, onError }) {
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("user_role", userRole);

    if (files && files.length > 0) {
      for (const f of files) {
        formData.append("files", f);
      }
    }

    try {
      const response = await fetch(`${getBackendUrl()}/api/chat`, { method: "POST", body: formData });

      if (!response.ok) {
        let errDetail = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errJson = await response.json();
          if (errJson.detail) errDetail = errJson.detail;
        } catch (_) {}
        if (onError) onError(new Error(errDetail));
        return;
      }

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
            if (eventType === "connected" && onConnected) onConnected(data);
            if (eventType === "thought" && onThought) onThought(data);
            if (eventType === "deliverable" && onDeliverable) onDeliverable(data);
            if (eventType === "done" && onDone) onDone(data);
            if (eventType === "error") {
              if (onError) onError(new Error(data.error || "Execution halted"));
              return;
            }
          } catch (err) {
            console.warn("SSE parse error:", err);
          }
        }
      }
    } catch (err) {
      if (onError) onError(err);
    }
  },

  // 5. List Files & Deliverables
  async listFiles() {
    const res = await fetch(`${getBackendUrl()}/api/files/list`);
    if (!res.ok) {
      throw new Error(`Cannot reach server at ${getBackendUrl()} (HTTP ${res.status})`);
    }
    return await res.json();
  },

  // 6. Download Deliverable URL
  getDownloadUrl(filename) {
    return `${getBackendUrl()}/api/files/download/${encodeURIComponent(filename)}`;
  },

  // 7. Network Telemetry Stream
  listenToTelemetry({ onTelemetry, onLockdown, onRestore, onError }) {
    const streamUrl = `${getBackendUrl()}/api/telemetry/network/stream`;
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onTelemetry) onTelemetry(data);
        if (data.is_air_gapped === false || data.external_gateway_detected === true || (data.outbound_wan_bytes_delta > 0)) {
          if (onLockdown) onLockdown(data);
        } else {
          if (onRestore) onRestore(data);
        }
      } catch (e) {
        console.error("Telemetry parse error:", e);
      }
    };

    eventSource.onerror = (err) => {
      if (onError) onError(err);
    };

    return eventSource;
  },

  // 8. Audit Chain
  async getAuditLedger() {
    const res = await fetch(`${getBackendUrl()}/api/telemetry/audit`);
    if (!res.ok) {
      throw new Error(`Cannot fetch audit ledger: HTTP ${res.status}`);
    }
    return await res.json();
  }
};
