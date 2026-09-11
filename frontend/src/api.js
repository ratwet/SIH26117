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

export const DEFAULT_SENIOR_USER = {
  id: "usr_senior",
  username: "senior",
  name: "Anand",
  role: "senior",
  avatar: "📐",
  allowed_models: ["Enterprise-100B", "Workstation-32B", "Edge-8B"],
  default_model: "Workstation-32B",
  description: "Senior Reliability Lead • Level 2 Statutory Approval & Model Switcher"
};

export function getCurrentUser() {
  if (typeof localStorage !== "undefined") {
    const saved = localStorage.getItem("aquanex_user");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (_) {}
    }
  }
  return DEFAULT_SENIOR_USER;
}

export function setCurrentUser(user) {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("aquanex_user", JSON.stringify(user));
  }
  return user;
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
  async streamChat({ prompt, userRole = null, files = [], onConnected, onThought, onDeliverable, onDone, onError }) {
    const activeUser = getCurrentUser();
    const effectiveRole = userRole || activeUser.role || "senior";
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("user_role", effectiveRole);
    formData.append("user_id", activeUser.id || "usr_senior");

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
  },

  // 9. Sovereign Authentication & Personas
  async getAuthUsers() {
    const res = await fetch(`${getBackendUrl()}/api/admin/auth/users`);
    if (!res.ok) {
      throw new Error(`Cannot fetch personas: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async login({ username, pin = null }) {
    const res = await fetch(`${getBackendUrl()}/api/admin/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, pin }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Sign-in failed: HTTP ${res.status}`);
    }
    const data = await res.json();
    if (data.user) {
      setCurrentUser(data.user);
    }
    return data;
  },

  // 10. Admin Model Governance
  async getAdminUsers() {
    const active = getCurrentUser();
    const res = await fetch(`${getBackendUrl()}/api/admin/users`, {
      headers: { "X-User-Role": active.role || "admin", "X-User-Id": active.id || "usr_admin" },
    });
    if (!res.ok) {
      throw new Error(`Cannot fetch users for governance: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async updateUserModelAccess(userId, allowedModels) {
    const active = getCurrentUser();
    const res = await fetch(`${getBackendUrl()}/api/admin/users/${encodeURIComponent(userId)}/permissions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": active.role || "admin",
        "X-User-Id": active.id || "usr_admin",
      },
      body: JSON.stringify({ allowed_models: allowedModels }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Permission update failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async setModelTier(tier) {
    const active = getCurrentUser();
    const res = await fetch(`${getBackendUrl()}/api/admin/model-tier`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": active.role || "admin",
        "X-User-Id": active.id || "usr_admin",
      },
      body: JSON.stringify({ tier }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Model tier update failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  // 11. Local Voice Sentinel (Zero Cloud, RAM only)
  async getVoiceStatus() {
    const res = await fetch(`${getBackendUrl()}/api/voice/status`);
    if (!res.ok) throw new Error(`Cannot fetch voice status: HTTP ${res.status}`);
    return await res.json();
  },

  async transcribeAudio(audioBlob = null, mockPrompt = null) {
    const formData = new FormData();
    if (audioBlob) {
      formData.append("file", audioBlob, "recording.wav");
    }
    if (mockPrompt) {
      formData.append("mock_prompt", mockPrompt);
    }
    const res = await fetch(`${getBackendUrl()}/api/voice/transcribe`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Transcription failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async synthesizeSpeech(text) {
    const res = await fetch(`${getBackendUrl()}/api/voice/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`Speech synthesis failed: HTTP ${res.status}`);
    return await res.blob();
  },

  // 12. Human Gate Action Approvals & CoWork Connectors
  async requestActionApproval({ action_type, target, payload_summary, payload_hash, user_id, user_role }) {
    const res = await fetch(`${getBackendUrl()}/api/actions/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action_type, target, payload_summary, payload_hash, user_id, user_role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Approval request rejected: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async createEmailDraft({ pipe_data, recipient = "inspection.lead@mrpl.co.in", attachments = [] }) {
    const res = await fetch(`${getBackendUrl()}/api/actions/email/draft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pipe_data, recipient, attachments }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Email draft creation failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async dispatchEmail({ draft_id, approval_token, user_role = "senior" }) {
    const res = await fetch(`${getBackendUrl()}/api/actions/email/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ draft_id, approval_token, user_role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Email dispatch failed: HTTP ${res.status}`);
    }
    return await res.json();
  },

  async getVaultList() {
    const res = await fetch(`${getBackendUrl()}/api/actions/vault/list`);
    if (!res.ok) throw new Error(`Cannot fetch vault listing: HTTP ${res.status}`);
    return await res.json();
  }
};
