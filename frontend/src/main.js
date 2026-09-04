// src/main.js - Sovereign AI Workbench (Gemini / Claude Conversational Interface)
import { SovereignAPI, getBackendUrl, setBackendUrl, getServerIP } from './api.js';
import { renderMarkdown } from './markdown.js';

// DOM Elements
const sidebar = document.getElementById('sidebar');
const btnToggleSidebar = document.getElementById('btnToggleSidebar');
const btnNewChat = document.getElementById('btnNewChat');
const chatHistoryList = document.getElementById('chatHistoryList');
const chatHistoryEmpty = document.getElementById('chatHistoryEmpty');

const workspaceCanvas = document.getElementById('workspaceCanvas');
const greetingContainer = document.getElementById('greetingContainer');
const greetingTitle = document.getElementById('greetingTitle');
const messagesFeed = document.getElementById('messagesFeed');

const chatTextarea = document.getElementById('chatTextarea');
const btnChatSend = document.getElementById('btnChatSend');
const btnAttachFile = document.getElementById('btnAttachFile');
const workspaceFileInput = document.getElementById('workspaceFileInput');
const attachedFilesContainer = document.getElementById('attachedFilesContainer');

const airGapStatusBadge = document.getElementById('airGapStatusBadge');
const airGapStatusText = document.getElementById('airGapStatusText');
const lockdownModal = document.getElementById('lockdownModal');

const modelDropdownBtn = document.getElementById('modelDropdownBtn');
const modelMenu = document.getElementById('modelMenu');
const currentModelBadge = document.getElementById('currentModelBadge');

const btnCustomize = document.getElementById('btnCustomize');
const btnOpenCustomizeTop = document.getElementById('btnOpenCustomizeTop');
const customizeModal = document.getElementById('customizeModal');
const btnCloseCustomize = document.getElementById('btnCloseCustomize');
const inputBackendUrl = document.getElementById('inputBackendUrl');
const btnTestBackendConn = document.getElementById('btnTestBackendConn');
const backendPingResult = document.getElementById('backendPingResult');
const btnPresetLocal = document.getElementById('btnPresetLocal');
const btnPresetLan = document.getElementById('btnPresetLan');
const modalAirGapBadge = document.getElementById('modalAirGapBadge');
const modalBackendHostPort = document.getElementById('modalBackendHostPort');
const statWanBytes = document.getElementById('statWanBytes');
const statIsolation = document.getElementById('statIsolation');
const modalAuditTableBody = document.getElementById('modalAuditTableBody');

// Application State
let chatSessions = [];
let currentSessionId = null;
let selectedFiles = [];
let isExecuting = false;
let telemetrySource = null;

// ==========================================================================
// INITIALIZATION
// ==========================================================================
async function init() {
  setupEventListeners();
  loadSavedSessions();
  updateGreeting();
  await probeNetworkImmediate();
  startTelemetryMonitor();
  loadAuditLedger();
}

// Set dynamic greeting based on time of day
function updateGreeting() {
  const hour = new Date().getHours();
  let timeStr = "Good evening";
  if (hour >= 5 && hour < 12) timeStr = "Good morning";
  else if (hour >= 12 && hour < 17) timeStr = "Good afternoon";

  if (greetingTitle) {
    greetingTitle.textContent = `${timeStr}, Cyanide`;
  }
}

// ==========================================================================
// AIR-GAP LOCKDOWN & TELEMETRY
// ==========================================================================
async function probeNetworkImmediate() {
  try {
    const data = await SovereignAPI.getNetworkStatus();
    updateAirGapUI(data);
  } catch (err) {
    console.warn("Immediate network probe check failed:", err);
  }
}

function startTelemetryMonitor() {
  if (telemetrySource) {
    telemetrySource.close();
  }

  telemetrySource = SovereignAPI.listenToTelemetry({
    onTelemetry: (data) => {
      updateAirGapUI(data);
    },
    onLockdown: (data) => {
      triggerLockdown();
    },
    onRestore: (data) => {
      restoreAirGap();
    },
    onError: (err) => {
      // Background retry handled by browser EventSource
    }
  });
}

function updateAirGapUI(data) {
  if (!data) return;

  const isViolated = !data.is_air_gapped || data.external_gateway_detected || (data.outbound_wan_bytes_delta > 0);

  if (isViolated) {
    triggerLockdown();
  } else {
    restoreAirGap();
  }

  if (statWanBytes) {
    statWanBytes.textContent = `${(data.outbound_wan_bytes_delta || 0).toLocaleString()} BYTES`;
    statWanBytes.style.color = isViolated ? 'var(--status-red)' : 'var(--status-emerald)';
  }

  if (modalAirGapBadge) {
    modalAirGapBadge.textContent = isViolated ? 'VIOLATION DETECTED' : 'LOCKED AIR-GAP OK';
    modalAirGapBadge.className = isViolated ? 'badge-crimson' : 'badge-emerald';
  }

  if (statIsolation) {
    statIsolation.textContent = isViolated ? 'UNSAFE WAN' : 'STRICT SOVEREIGN';
    statIsolation.style.color = isViolated ? 'var(--status-red)' : 'var(--status-emerald)';
  }
}

function triggerLockdown() {
  if (airGapStatusBadge) {
    airGapStatusBadge.className = 'air-gap-pill danger';
  }
  if (airGapStatusText) {
    airGapStatusText.textContent = 'Internet Detected (Locked)';
  }
  if (lockdownModal) {
    lockdownModal.style.display = 'flex';
  }

  // Freeze user inputs to prevent data exfiltration
  if (chatTextarea) chatTextarea.disabled = true;
  if (btnChatSend) btnChatSend.disabled = true;
  if (btnAttachFile) btnAttachFile.disabled = true;
}

function restoreAirGap() {
  if (airGapStatusBadge) {
    airGapStatusBadge.className = 'air-gap-pill';
  }
  if (airGapStatusText) {
    airGapStatusText.textContent = 'Air-Gap Protected';
  }
  if (lockdownModal) {
    lockdownModal.style.display = 'none';
  }

  // Re-enable inputs
  if (chatTextarea) chatTextarea.disabled = false;
  if (btnAttachFile) btnAttachFile.disabled = false;
  updateSendButtonState();
}

// ==========================================================================
// CHAT SESSION MANAGEMENT (LOCALSTORAGE)
// ==========================================================================
function loadSavedSessions() {
  try {
    const raw = localStorage.getItem('aquanex_chat_sessions');
    if (raw) {
      chatSessions = JSON.parse(raw);
    }
  } catch (e) {
    chatSessions = [];
  }

  renderSidebarSessions();

  if (chatSessions.length > 0) {
    loadSession(chatSessions[0].id);
  } else {
    resetToNewChat();
  }
}

function saveSessionsToStorage() {
  try {
    localStorage.setItem('aquanex_chat_sessions', JSON.stringify(chatSessions));
  } catch (e) {
    console.error("Failed to save sessions:", e);
  }
}

function renderSidebarSessions() {
  if (!chatHistoryList) return;
  chatHistoryList.innerHTML = '';

  if (chatSessions.length === 0) {
    if (chatHistoryEmpty) chatHistoryList.appendChild(chatHistoryEmpty);
    return;
  }

  chatSessions.forEach(session => {
    const item = document.createElement('div');
    item.className = `chat-session-item ${session.id === currentSessionId ? 'active' : ''}`;
    item.innerHTML = `
      <span class="chat-session-title">${escapeHtml(session.title || 'Conversation')}</span>
      <button class="btn-delete-session" title="Delete conversation">✕</button>
    `;

    item.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-delete-session')) {
        e.stopPropagation();
        deleteSession(session.id);
        return;
      }
      loadSession(session.id);
    });

    chatHistoryList.appendChild(item);
  });
}

function resetToNewChat() {
  currentSessionId = 'session_' + Date.now();
  messagesFeed.innerHTML = '';
  messagesFeed.style.display = 'none';
  greetingContainer.style.display = 'flex';
  chatTextarea.value = '';
  chatTextarea.style.height = 'auto';
  selectedFiles = [];
  renderAttachedFilesPreview();
  updateSendButtonState();
  renderSidebarSessions();
  chatTextarea.focus();
}

function loadSession(sessionId) {
  const session = chatSessions.find(s => s.id === sessionId);
  if (!session) {
    resetToNewChat();
    return;
  }

  currentSessionId = sessionId;
  messagesFeed.innerHTML = '';

  if (!session.messages || session.messages.length === 0) {
    greetingContainer.style.display = 'flex';
    messagesFeed.style.display = 'none';
  } else {
    greetingContainer.style.display = 'none';
    messagesFeed.style.display = 'flex';

    session.messages.forEach(msg => {
      if (msg.role === 'user') {
        renderUserMessageBubble(msg.text, msg.files);
      } else if (msg.role === 'assistant') {
        renderAssistantMessageBubble(msg.text, msg.thoughts, msg.deliverables);
      }
    });
    scrollToBottom();
  }

  renderSidebarSessions();
}

function deleteSession(sessionId) {
  chatSessions = chatSessions.filter(s => s.id !== sessionId);
  saveSessionsToStorage();
  if (currentSessionId === sessionId) {
    if (chatSessions.length > 0) {
      loadSession(chatSessions[0].id);
    } else {
      resetToNewChat();
    }
  } else {
    renderSidebarSessions();
  }
}

// ==========================================================================
// CONVERSATION FLOW (PROMPT DISPATCH & REAL SSE STREAM)
// ==========================================================================
async function handleSendPrompt() {
  const prompt = chatTextarea.value.trim();
  if ((!prompt && selectedFiles.length === 0) || isExecuting) return;

  isExecuting = true;
  updateSendButtonState();

  // Ensure active session
  let session = chatSessions.find(s => s.id === currentSessionId);
  if (!session) {
    session = {
      id: currentSessionId,
      title: prompt ? (prompt.length > 28 ? prompt.substring(0, 26) + '...' : prompt) : "Inspection Session",
      timestamp: Date.now(),
      messages: []
    };
    chatSessions.unshift(session);
  }

  // Switch to messages view
  greetingContainer.style.display = 'none';
  messagesFeed.style.display = 'flex';

  // Render User Message
  const userFilesCopy = [...selectedFiles];
  renderUserMessageBubble(prompt, userFilesCopy);
  session.messages.push({ role: 'user', text: prompt, files: userFilesCopy.map(f => f.name) });
  saveSessionsToStorage();
  renderSidebarSessions();

  // Clear Inputs
  chatTextarea.value = '';
  chatTextarea.style.height = 'auto';
  selectedFiles = [];
  renderAttachedFilesPreview();
  updateSendButtonState();

  // Create Assistant Message Row
  const { row, thoughtDrawer, thoughtList, thoughtBadge, thoughtPulse, contentContainer } = createAssistantRow();
  messagesFeed.appendChild(row);
  scrollToBottom();

  const currentThoughts = [];

  await SovereignAPI.streamChat({
    prompt: prompt || "Analyze attached document.",
    userRole: "senior",
    files: userFilesCopy,
    onThought: (payload) => {
      thoughtDrawer.style.display = 'block';
      const thoughtText = payload.thought || JSON.stringify(payload);
      currentThoughts.push(thoughtText);

      const item = document.createElement('div');
      item.className = 'thought-step-line';
      item.innerHTML = `<span>▶</span> <span>${escapeHtml(thoughtText)}</span>`;
      thoughtList.appendChild(item);
      thoughtBadge.textContent = `${currentThoughts.length} steps`;
      scrollToBottom();
    },
    onDone: (payload) => {
      isExecuting = false;
      updateSendButtonState();

      thoughtPulse.classList.add('done');
      thoughtBadge.textContent = `Completed (${currentThoughts.length} steps)`;

      const finalResponse = payload.final_response || "Analysis completed.";
      contentContainer.innerHTML = renderMarkdown(finalResponse);

      // Render Real Deliverables if any were generated
      const delivs = extractDeliverables(payload);
      if (delivs.length > 0) {
        renderRealDeliverablesChips(contentContainer, delivs);
      }

      session.messages.push({
        role: 'assistant',
        text: finalResponse,
        thoughts: currentThoughts,
        deliverables: delivs
      });
      saveSessionsToStorage();
      scrollToBottom();
    },
    onError: (err) => {
      isExecuting = false;
      updateSendButtonState();

      thoughtPulse.classList.add('done');
      const errMessage = err.message || "Connection failed";

      const errCard = document.createElement('div');
      errCard.className = 'model-error-card';
      errCard.innerHTML = `
        <h4>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Sovereign Engine Message
        </h4>
        <p>${escapeHtml(errMessage)}</p>
        <p style="margin-top: 8px; font-size: 0.8rem; color: #cbd5e1;">
          Ensure your local LLM is running via <code>ollama run qwen2.5:3b</code> or your vLLM server is reachable at <code>http://127.0.0.1:8001/v1</code>.
        </p>
      `;
      contentContainer.appendChild(errCard);
      scrollToBottom();
    }
  });
}

function createAssistantRow() {
  const row = document.createElement('div');
  row.className = 'msg-row msg-assistant';

  const wrap = document.createElement('div');
  wrap.className = 'msg-assistant-wrap';

  const avatar = document.createElement('img');
  avatar.src = '/aquanex-logo.png';
  avatar.alt = 'Aquanex';
  avatar.className = 'assistant-avatar';

  const body = document.createElement('div');
  body.className = 'assistant-body';

  const thoughtDrawer = document.createElement('details');
  thoughtDrawer.className = 'thought-drawer';
  thoughtDrawer.style.display = 'none';
  thoughtDrawer.innerHTML = `
    <summary class="thought-summary">
      <span class="thought-pulse"></span>
      <span>Thinking Process</span>
      <span class="thought-badge">0 steps</span>
    </summary>
    <div class="thought-steps-list"></div>
  `;

  const thoughtList = thoughtDrawer.querySelector('.thought-steps-list');
  const thoughtBadge = thoughtDrawer.querySelector('.thought-badge');
  const thoughtPulse = thoughtDrawer.querySelector('.thought-pulse');

  const contentContainer = document.createElement('div');
  contentContainer.className = 'md-content';
  contentContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">Connecting to Sovereign engine...</span>';

  body.appendChild(thoughtDrawer);
  body.appendChild(contentContainer);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  row.appendChild(wrap);

  return { row, thoughtDrawer, thoughtList, thoughtBadge, thoughtPulse, contentContainer };
}

function renderUserMessageBubble(text, files = []) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-user';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (files && files.length > 0) {
    const filesHeader = document.createElement('div');
    filesHeader.style.cssText = 'display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px;';
    files.forEach(f => {
      const pill = document.createElement('span');
      pill.style.cssText = 'font-size:0.75rem; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:10px;';
      pill.textContent = `📎 ${typeof f === 'string' ? f : f.name}`;
      filesHeader.appendChild(pill);
    });
    bubble.appendChild(filesHeader);
  }

  if (text) {
    const textNode = document.createElement('div');
    textNode.textContent = text;
    bubble.appendChild(textNode);
  }

  row.appendChild(bubble);
  messagesFeed.appendChild(row);
  scrollToBottom();
}

function renderAssistantMessageBubble(text, thoughts = [], deliverables = []) {
  const { row, thoughtDrawer, thoughtList, thoughtBadge, thoughtPulse, contentContainer } = createAssistantRow();
  
  if (thoughts && thoughts.length > 0) {
    thoughtDrawer.style.display = 'block';
    thoughtPulse.classList.add('done');
    thoughtBadge.textContent = `${thoughts.length} steps`;
    thoughts.forEach(t => {
      const item = document.createElement('div');
      item.className = 'thought-step-line';
      item.innerHTML = `<span>▶</span> <span>${escapeHtml(t)}</span>`;
      thoughtList.appendChild(item);
    });
  }

  contentContainer.innerHTML = renderMarkdown(text || '');

  if (deliverables && deliverables.length > 0) {
    renderRealDeliverablesChips(contentContainer, deliverables);
  }

  messagesFeed.appendChild(row);
}

function extractDeliverables(payload) {
  const items = [];
  const keys = [
    { key: 'docx_path', ext: 'DOCX', label: 'Executive Note (.docx)' },
    { key: 'xlsx_path', ext: 'XLSX', label: 'Cost Matrix (.xlsx)' },
    { key: 'pptx_path', ext: 'PPTX', label: 'Pitch Deck (.pptx)' },
    { key: 'pdf_path', ext: 'PDF', label: 'Inspection Cert (.pdf)' },
    { key: 'cad_path', ext: 'CAD', label: 'Spool Drawing (.dxf)' },
    { key: 'stl_path', ext: '3D', label: '3D Mesh (.stl)' },
    { key: 'image_path', ext: 'MAP', label: 'Corrosion Heatmap (.png)' },
    { key: 'csv_path', ext: 'CSV', label: 'Ultrasonic Log (.csv)' },
    { key: 'script_path', ext: 'CODE', label: 'Math Script (.py)' },
    { key: 'manifest_path', ext: 'HASH', label: 'Audit Manifest (.json)' },
  ];

  keys.forEach(({ key, ext, label }) => {
    if (payload[key]) {
      const filename = payload[key].split('/').pop();
      items.push({ filename, ext, label });
    }
  });

  return items;
}

function renderRealDeliverablesChips(container, deliverables) {
  const wrap = document.createElement('div');
  wrap.className = 'real-artifacts-container';

  const title = document.createElement('div');
  title.className = 'artifacts-title';
  title.textContent = `Generated Artifacts (${deliverables.length})`;
  wrap.appendChild(title);

  const grid = document.createElement('div');
  grid.className = 'artifacts-chips-grid';

  deliverables.forEach(d => {
    const chip = document.createElement('a');
    chip.className = 'artifact-chip';
    chip.href = SovereignAPI.getDownloadUrl(d.filename);
    chip.download = d.filename;
    chip.target = '_blank';
    chip.innerHTML = `
      <span class="artifact-chip-badge">${d.ext}</span>
      <span>${escapeHtml(d.filename)}</span>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
    `;
    grid.appendChild(chip);
  });

  wrap.appendChild(grid);
  container.appendChild(wrap);
}

// ==========================================================================
// EVENT LISTENERS & UI INTERACTIONS
// ==========================================================================
function setupEventListeners() {
  // Sidebar Toggle
  if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // New Chat
  if (btnNewChat) {
    btnNewChat.addEventListener('click', () => {
      resetToNewChat();
    });
  }

  // Auto-expanding textarea & Enter key dispatch
  if (chatTextarea) {
    chatTextarea.addEventListener('input', () => {
      chatTextarea.style.height = 'auto';
      chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
      updateSendButtonState();
    });

    chatTextarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendPrompt();
      }
    });
  }

  // Send Button
  if (btnChatSend) {
    btnChatSend.addEventListener('click', () => {
      handleSendPrompt();
    });
  }

  // File Upload Attach
  if (btnAttachFile && workspaceFileInput) {
    btnAttachFile.addEventListener('click', () => {
      workspaceFileInput.click();
    });

    workspaceFileInput.addEventListener('change', () => {
      if (workspaceFileInput.files && workspaceFileInput.files.length > 0) {
        for (let i = 0; i < workspaceFileInput.files.length; i++) {
          selectedFiles.push(workspaceFileInput.files[i]);
        }
        renderAttachedFilesPreview();
        updateSendButtonState();
      }
    });
  }

  // Suggestion Pills
  document.querySelectorAll('.pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const prompt = btn.getAttribute('data-prompt');
      if (prompt && chatTextarea) {
        chatTextarea.value = prompt;
        chatTextarea.style.height = 'auto';
        chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
        updateSendButtonState();
        handleSendPrompt();
      }
    });
  });

  // Model Selector Dropdown
  if (modelDropdownBtn && modelMenu) {
    modelDropdownBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      modelMenu.style.display = modelMenu.style.display === 'none' ? 'block' : 'none';
    });

    document.querySelectorAll('.model-option').forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll('.model-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        if (currentModelBadge) currentModelBadge.textContent = opt.dataset.model;
        modelMenu.style.display = 'none';
      });
    });

    document.addEventListener('click', () => {
      modelMenu.style.display = 'none';
    });
  }

  // Settings Modal Triggers
  const openSettings = () => {
    if (customizeModal) customizeModal.style.display = 'flex';
    if (inputBackendUrl) inputBackendUrl.value = getBackendUrl();
    if (modalBackendHostPort) modalBackendHostPort.textContent = getServerIP();
    loadAuditLedger();
  };

  if (btnCustomize) btnCustomize.addEventListener('click', openSettings);
  if (btnOpenCustomizeTop) btnOpenCustomizeTop.addEventListener('click', openSettings);
  if (btnCloseCustomize) btnCloseCustomize.addEventListener('click', () => {
    if (customizeModal) customizeModal.style.display = 'none';
  });

  // Backend URL configuration
  if (btnTestBackendConn) {
    btnTestBackendConn.addEventListener('click', async () => {
      const target = inputBackendUrl.value.trim();
      btnTestBackendConn.disabled = true;
      btnTestBackendConn.textContent = 'Pinging...';
      if (backendPingResult) {
        backendPingResult.style.display = 'block';
        backendPingResult.textContent = 'Testing connectivity...';
      }

      try {
        const res = await SovereignAPI.checkHealth(target);
        setBackendUrl(target);
        if (backendPingResult) {
          backendPingResult.style.color = 'var(--status-emerald)';
          backendPingResult.textContent = `✅ Connected successfully to ${target} (Uptime: ${res.uptime_seconds}s)`;
        }
        startTelemetryMonitor();
      } catch (err) {
        if (backendPingResult) {
          backendPingResult.style.color = 'var(--status-red)';
          backendPingResult.textContent = `❌ Connection failed: ${err.message}`;
        }
      } finally {
        btnTestBackendConn.disabled = false;
        btnTestBackendConn.textContent = 'Test Ping';
      }
    });
  }

  if (btnPresetLocal) {
    btnPresetLocal.addEventListener('click', () => {
      if (inputBackendUrl) inputBackendUrl.value = 'http://127.0.0.1:8000';
      btnPresetLocal.classList.add('active');
      if (btnPresetLan) btnPresetLan.classList.remove('active');
    });
  }

  if (btnPresetLan) {
    btnPresetLan.addEventListener('click', () => {
      if (inputBackendUrl) inputBackendUrl.value = 'http://192.168.1.100:8000';
      btnPresetLan.classList.add('active');
      if (btnPresetLocal) btnPresetLocal.classList.remove('active');
    });
  }
}

function updateSendButtonState() {
  const hasText = chatTextarea && chatTextarea.value.trim().length > 0;
  const hasFiles = selectedFiles.length > 0;
  if (btnChatSend) {
    btnChatSend.disabled = isExecuting || (!hasText && !hasFiles);
  }
}

function renderAttachedFilesPreview() {
  if (!attachedFilesContainer) return;
  attachedFilesContainer.innerHTML = '';

  if (selectedFiles.length === 0) {
    attachedFilesContainer.style.display = 'none';
    return;
  }

  attachedFilesContainer.style.display = 'flex';
  selectedFiles.forEach((f, idx) => {
    const pill = document.createElement('div');
    pill.className = 'file-preview-pill';
    pill.innerHTML = `
      <span>📎</span>
      <span>${escapeHtml(f.name)}</span>
      <button class="btn-remove" data-idx="${idx}" title="Remove file">✕</button>
    `;

    pill.querySelector('.btn-remove').addEventListener('click', (e) => {
      const removeIdx = parseInt(e.target.dataset.idx, 10);
      selectedFiles.splice(removeIdx, 1);
      renderAttachedFilesPreview();
      updateSendButtonState();
    });

    attachedFilesContainer.appendChild(pill);
  });
}

function scrollToBottom() {
  if (workspaceCanvas) {
    workspaceCanvas.scrollTop = workspaceCanvas.scrollHeight;
  }
}

async function loadAuditLedger() {
  if (!modalAuditTableBody) return;
  try {
    const ledger = await SovereignAPI.getAuditLedger();
    modalAuditTableBody.innerHTML = '';
    const events = ledger.recent_events || [];
    events.forEach(ev => {
      const tr = document.createElement('tr');
      const shortHash = ev.current_hash ? ev.current_hash.substring(0, 14) + '...' : '00000000...';
      tr.innerHTML = `
        <td style="color: var(--accent-gold); font-weight:700;">#${ev.id}</td>
        <td style="font-size:0.72rem; text-transform:uppercase;">${escapeHtml(ev.event_type)}</td>
        <td style="color: var(--accent-blue);">${shortHash}</td>
        <td style="color: var(--status-emerald);">OK</td>
      `;
      modalAuditTableBody.appendChild(tr);
    });
  } catch (e) {
    console.warn("Ledger load error:", e);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

// Start application
init();
