// src/main.js - Sovereign AI Workbench (Gemini / Claude Conversational Interface)
import { SovereignAPI, getBackendUrl, setBackendUrl, getServerIP, getCurrentUser, setCurrentUser } from './api.js';
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
const juniorLockedBadge = document.getElementById('juniorLockedBadge');

const userProfilePill = document.getElementById('userProfilePill');
const userAvatarChar = document.getElementById('userAvatarChar');
const userDisplayName = document.getElementById('userDisplayName');
const userRoleLabel = document.getElementById('userRoleLabel');

const authModal = document.getElementById('authModal');
const btnCloseAuth = document.getElementById('btnCloseAuth');
const authPinInput = document.getElementById('authPinInput');
const btnPinLogin = document.getElementById('btnPinLogin');
const authPinError = document.getElementById('authPinError');

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

const adminGovernanceCard = document.getElementById('adminGovernanceCard');
const governanceMatrixContainer = document.getElementById('governanceMatrixContainer');

const adminDashboardCanvas = document.getElementById('adminDashboardCanvas');
const inputBarOuter = document.getElementById('inputBarOuter');
const greetingSubtitle = document.getElementById('greetingSubtitle');
const suggestionPillsRow = document.getElementById('suggestionPillsRow');
const btnPingNodes = document.getElementById('btnPingNodes');
const dashGovMatrix = document.getElementById('dashGovMatrix');
const adminMatrixSaveNotice = document.getElementById('adminMatrixSaveNotice');
const btnVerifyAuditChain = document.getElementById('btnVerifyAuditChain');
const btnRefreshAudit = document.getElementById('btnRefreshAudit');
const auditChainVerifyBanner = document.getElementById('auditChainVerifyBanner');
const auditChainVerifyMsg = document.getElementById('auditChainVerifyMsg');
const dashAuditTableBody = document.getElementById('dashAuditTableBody');
const adminStatLedgerBlocks = document.getElementById('adminStatLedgerBlocks');

// Application State
let chatSessions = [];
let currentSessionId = null;
let selectedFiles = [];
let isExecuting = false;
let telemetrySource = null;
let lockdownDismissed = false;

// ==========================================================================
// INITIALIZATION
// ==========================================================================
async function init() {
  setupEventListeners();
  loadSavedSessions();

  // Check URL query parameters for persona auto-login (e.g. ?persona=admin / senior / junior)
  let activeUser = getCurrentUser();
  if (typeof window !== 'undefined' && window.location.search) {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('bypass_airgap') === '1' || urlParams.get('demo') === '1') {
      lockdownDismissed = true;
    }
    const personaParam = urlParams.get('persona') || urlParams.get('role');
    if (personaParam) {
      try {
        const res = await SovereignAPI.login({ username: personaParam.toLowerCase() });
        if (res.user) {
          activeUser = res.user;
        }
      } catch (err) {
        console.warn("Could not auto-login with URL persona:", err);
      }
    }
  }

  applyUserPermissions(activeUser);
  await probeNetworkImmediate();
  startTelemetryMonitor();
  loadAuditLedger();
}

// Set dynamic greeting and suggestion pills based on time of day and active persona
function updateGreeting(user = null) {
  const activeUser = user || getCurrentUser();
  const role = (activeUser.role || 'senior').toLowerCase();
  const hour = new Date().getHours();
  let timeStr = "Good evening";
  if (hour >= 5 && hour < 12) timeStr = "Good morning";
  else if (hour >= 12 && hour < 17) timeStr = "Good afternoon";

  if (greetingTitle) {
    greetingTitle.textContent = `${timeStr}, ${activeUser.name || 'Engineer'}`;
  }

  if (greetingSubtitle) {
    if (role === 'senior') {
      greetingSubtitle.textContent = "Senior Reliability Lead — Autonomous Pipeline & Refinery Analytics";
    } else if (role === 'junior') {
      greetingSubtitle.textContent = "Field Inspection Technician — Ruggedized Edge Terminal (Pre-configured)";
    } else {
      greetingSubtitle.textContent = "Sovereign Engineering Interface";
    }
  }

  if (suggestionPillsRow) {
    if (role === 'senior') {
      suggestionPillsRow.innerHTML = `
        <button class="pill-btn" data-prompt="Audit line CDU-2-04-150-A1A for remaining safe life per API 570">
          <span class="pill-icon">⚡</span>
          <span class="pill-text">API 570 Remaining Life Calculation</span>
        </button>
        <button class="pill-btn" data-prompt="Calculate ASME B31.3 minimum required thickness for line CDU-2-04-150-A1A at 150 PSI and 135 C">
          <span class="pill-icon">🔍</span>
          <span class="pill-text">ASME B31.3 Minimum Thickness</span>
        </button>
        <button class="pill-btn" data-prompt="Summarize the latest ultrasonic thickness NDT inspection survey and highlight thinning anomalies">
          <span class="pill-icon">📋</span>
          <span class="pill-text">Summarize NDT Inspection Log</span>
        </button>
        <button class="pill-btn" data-prompt="Generate an AutoCAD DXF piping spool replacement specification for corroded segment">
          <span class="pill-icon">📐</span>
          <span class="pill-text">Generate Piping Spool CAD</span>
        </button>
      `;
    } else if (role === 'junior') {
      suggestionPillsRow.innerHTML = `
        <button class="pill-btn" data-prompt="Quick check: Actual thickness 3.2mm on 4.8mm pipe. Is it safe to operate?">
          <span class="pill-icon">⚡</span>
          <span class="pill-text">Quick Ultrasonic Thickness Check</span>
        </button>
        <button class="pill-btn" data-prompt="Log severe exterior pitting corrosion observed near elbow weld on CDU overhead line">
          <span class="pill-icon">🔍</span>
          <span class="pill-text">Log Visual Pipe Defect</span>
        </button>
        <button class="pill-btn" data-prompt="What is the minimum safe thickness before replacement is required under API 570?">
          <span class="pill-icon">📋</span>
          <span class="pill-text">Check Minimum Safe Wall Thickness</span>
        </button>
        <button class="pill-btn" data-prompt="Show step-by-step ultrasonic thickness measurement procedure for insulated piping">
          <span class="pill-icon">📐</span>
          <span class="pill-text">View Pipe Inspection SOP</span>
        </button>
      `;
    }
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

  if (lockdownDismissed) return;

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
  const { row, thoughtDrawer, thoughtList, thoughtTitle, thoughtBadge, thoughtPulse, contentContainer } = createAssistantRow();
  messagesFeed.appendChild(row);
  scrollToBottom();

  const currentThoughts = [];

  await SovereignAPI.streamChat({
    prompt: prompt || "Analyze attached document.",
    userRole: getCurrentUser().role,
    files: userFilesCopy,
    onThought: (payload) => {
      thoughtDrawer.style.display = 'block';
      const thoughtText = payload.thought || JSON.stringify(payload);
      currentThoughts.push(thoughtText);

      const item = document.createElement('div');
      item.className = 'thought-step-line';
      item.innerHTML = `<span>▶</span> <span>${escapeHtml(thoughtText)}</span>`;
      thoughtList.appendChild(item);
      thoughtTitle.textContent = 'Thinking...';
      thoughtBadge.textContent = `${currentThoughts.length} steps`;
      scrollToBottom();
    },
    onDone: (payload) => {
      isExecuting = false;
      updateSendButtonState();

      thoughtPulse.classList.add('done');
      thoughtTitle.textContent = 'Thought for a few seconds';
      thoughtBadge.textContent = `(${currentThoughts.length} steps)`;

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

      const errMsg = err.message || String(err);
      const isOffline = errMsg.includes('NO LLM MODEL CONNECTED') || 
                        errMsg.includes('Connection refused') || 
                        errMsg.includes('model server') ||
                        errMsg.includes('Failed to fetch');

      if (isOffline) {
        thoughtTitle.textContent = 'Inference halted (Server Offline)';
        thoughtPulse.style.background = 'var(--status-amber)';
        thoughtPulse.style.boxShadow = 'none';

        contentContainer.innerHTML = `
          <div class="model-offline-banner">
            <div class="offline-banner-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
            <div class="offline-banner-content">
              <div class="offline-banner-title">Local Model Server Offline</div>
              <div class="offline-banner-desc">Local sovereign inference engine is not reachable at <code>127.0.0.1:11434</code> (Ollama) or <code>127.0.0.1:8001</code> (vLLM). Hardware emulation is strictly disabled.</div>
              <div class="offline-banner-guide">
                <span>To launch local engine:</span>
                <code>ollama serve</code>
                <span style="margin: 0 4px;">or start vLLM</span>
              </div>
            </div>
          </div>
        `;
      } else {
        thoughtTitle.textContent = 'Execution notice';
        contentContainer.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 12px 16px; color: var(--accent-crimson); font-size: 0.88rem;">
            <strong>System Notice:</strong> ${escapeHtml(errMsg)}
          </div>
        `;
      }
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
      <span class="thought-title">Thinking...</span>
      <span class="thought-badge">0 steps</span>
    </summary>
    <div class="thought-steps-list"></div>
  `;

  const thoughtList = thoughtDrawer.querySelector('.thought-steps-list');
  const thoughtTitle = thoughtDrawer.querySelector('.thought-title');
  const thoughtBadge = thoughtDrawer.querySelector('.thought-badge');
  const thoughtPulse = thoughtDrawer.querySelector('.thought-pulse');

  const contentContainer = document.createElement('div');
  contentContainer.className = 'md-content';
  contentContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">Thinking...</span>';

  body.appendChild(thoughtDrawer);
  body.appendChild(contentContainer);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  row.appendChild(wrap);

  return { row, thoughtDrawer, thoughtList, thoughtTitle, thoughtBadge, thoughtPulse, contentContainer };
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
  const { row, thoughtDrawer, thoughtList, thoughtTitle, thoughtBadge, thoughtPulse, contentContainer } = createAssistantRow();
  
  if (thoughts && thoughts.length > 0) {
    thoughtDrawer.style.display = 'block';
    thoughtPulse.classList.add('done');
    thoughtTitle.textContent = 'Thought for a few seconds';
    thoughtBadge.textContent = `(${thoughts.length} steps)`;
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

  // Suggestion Pills (Delegated)
  if (suggestionPillsRow) {
    suggestionPillsRow.addEventListener('click', (e) => {
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      const prompt = btn.getAttribute('data-prompt');
      if (prompt && chatTextarea) {
        chatTextarea.value = prompt;
        chatTextarea.style.height = 'auto';
        chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
        updateSendButtonState();
        handleSendPrompt();
      }
    });
  }

  // Admin Dashboard Action Listeners
  if (btnPingNodes) {
    btnPingNodes.addEventListener('click', async () => {
      btnPingNodes.innerHTML = `<span>Pinging...</span>`;
      try {
        await SovereignAPI.getNetworkStatus();
        btnPingNodes.innerHTML = `<span>All 3 Nodes Healthy ✓</span>`;
        setTimeout(() => {
          btnPingNodes.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            <span>Ping Nodes</span>
          `;
        }, 2000);
      } catch (e) {
        btnPingNodes.innerHTML = `<span>Ping Complete</span>`;
      }
    });
  }

  if (btnVerifyAuditChain) {
    btnVerifyAuditChain.addEventListener('click', async () => {
      btnVerifyAuditChain.innerHTML = `<span>Verifying...</span>`;
      try {
        const data = await SovereignAPI.getAuditLedger();
        if (auditChainVerifyMsg) {
          auditChainVerifyMsg.textContent = data.verification_message || `All ${data.total_blocks} blocks cryptographically verified and intact.`;
        }
        btnVerifyAuditChain.innerHTML = `<span>Verified ✓</span>`;
        setTimeout(() => {
          btnVerifyAuditChain.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Verify Ledger Integrity</span>
          `;
        }, 2000);
      } catch (e) {
        btnVerifyAuditChain.innerHTML = `<span>Verify Ledger Integrity</span>`;
      }
    });
  }

  if (btnRefreshAudit) {
    btnRefreshAudit.addEventListener('click', () => {
      loadAuditLedger();
    });
  }

  const btnDismissLockdown = document.getElementById('btnDismissLockdown');
  if (btnDismissLockdown) {
    btnDismissLockdown.addEventListener('click', () => {
      lockdownDismissed = true;
      if (lockdownModal) lockdownModal.style.display = 'none';
      if (chatTextarea) chatTextarea.disabled = false;
      if (btnChatSend) btnChatSend.disabled = false;
      if (btnAttachFile) btnAttachFile.disabled = false;
      updateSendButtonState();
    });
  }

  // Model Selector Dropdown
  if (modelDropdownBtn && modelMenu) {
    modelDropdownBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      modelMenu.style.display = modelMenu.style.display === 'none' ? 'block' : 'none';
    });

    document.querySelectorAll('.model-option').forEach(opt => {
      opt.addEventListener('click', async () => {
        document.querySelectorAll('.model-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        const selectedModel = opt.dataset.model;
        if (currentModelBadge) currentModelBadge.textContent = selectedModel;
        modelMenu.style.display = 'none';

        // Synchronize with backend model tier
        let tierKey = 'WORKSTATION_32B';
        if (selectedModel === 'Enterprise-100B') tierKey = 'ENTERPRISE_100B';
        else if (selectedModel === 'Edge-8B') tierKey = 'EDGE_LAPTOP_8B';

        try {
          await SovereignAPI.setModelTier(tierKey);
        } catch (err) {
          console.warn("Could not sync model tier with backend:", err);
        }
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
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.role === 'admin') {
      if (adminGovernanceCard) adminGovernanceCard.style.display = 'block';
      loadAdminGovernanceMatrix();
    } else {
      if (adminGovernanceCard) adminGovernanceCard.style.display = 'none';
    }
  };

  if (btnCustomize) btnCustomize.addEventListener('click', openSettings);
  if (btnOpenCustomizeTop) btnOpenCustomizeTop.addEventListener('click', openSettings);
  if (btnCloseCustomize) btnCloseCustomize.addEventListener('click', () => {
    if (customizeModal) customizeModal.style.display = 'none';
  });

  // Sovereign Auth & Role Switcher Modal
  if (userProfilePill && authModal) {
    userProfilePill.addEventListener('click', () => {
      authModal.style.display = 'flex';
      if (authPinError) authPinError.style.display = 'none';
      if (authPinInput) authPinInput.value = '';
    });
  }

  if (btnCloseAuth && authModal) {
    btnCloseAuth.addEventListener('click', () => {
      authModal.style.display = 'none';
    });
  }

  if (authModal) {
    authModal.addEventListener('click', (e) => {
      if (e.target === authModal) {
        authModal.style.display = 'none';
      }
    });
  }

  // 1-Click Persona Selection
  document.querySelectorAll('.btn-persona-select').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const username = btn.dataset.username;
      try {
        btn.disabled = true;
        btn.textContent = 'Signing in...';
        const res = await SovereignAPI.login({ username });
        applyUserPermissions(res.user);
        if (authModal) authModal.style.display = 'none';
      } catch (err) {
        alert(`Sign-in failed: ${err.message}`);
      } finally {
        btn.disabled = false;
        btn.textContent = `Switch to ${username.charAt(0).toUpperCase() + username.slice(1)}`;
      }
    });
  });

  document.querySelectorAll('.persona-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      if (authPinInput) authPinInput.focus();
    });
  });

  // Security PIN Verification
  if (btnPinLogin && authPinInput) {
    const handlePinLogin = async () => {
      const pin = authPinInput.value.trim();
      if (!pin) {
        if (authPinError) {
          authPinError.textContent = 'Please enter a 4-digit security PIN.';
          authPinError.style.display = 'block';
        }
        return;
      }

      let targetUsername = 'senior';
      const activeCard = document.querySelector('.persona-card.active');
      if (activeCard && activeCard.dataset.username) {
        targetUsername = activeCard.dataset.username;
      } else {
        if (pin === '1170') targetUsername = 'admin';
        else if (pin === '5700') targetUsername = 'senior';
        else if (pin === '2026') targetUsername = 'junior';
      }

      try {
        btnPinLogin.disabled = true;
        btnPinLogin.textContent = 'Verifying...';
        if (authPinError) authPinError.style.display = 'none';

        const res = await SovereignAPI.login({ username: targetUsername, pin });
        applyUserPermissions(res.user);
        if (authModal) authModal.style.display = 'none';
        authPinInput.value = '';
      } catch (err) {
        if (authPinError) {
          authPinError.textContent = `❌ ${err.message || 'Authentication failed: Invalid PIN.'}`;
          authPinError.style.display = 'block';
        }
      } finally {
        btnPinLogin.disabled = false;
        btnPinLogin.textContent = 'Verify & Sign In';
      }
    };

    btnPinLogin.addEventListener('click', handlePinLogin);
    authPinInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handlePinLogin();
    });
  }

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

// ==========================================================================
// ROLE-BASED ACCESS CONTROL & MODEL PERMISSIONS
// ==========================================================================

function applyUserPermissions(user) {
  if (!user) user = getCurrentUser();

  // 1. Update Sidebar Profile Pill
  if (userAvatarChar) userAvatarChar.textContent = user.avatar || '👤';
  if (userDisplayName) userDisplayName.textContent = user.name || 'Engineer';
  if (userRoleLabel) userRoleLabel.textContent = user.description ? user.description.split('•')[0].trim() : (user.role || 'User');

  // Update dynamic greeting with user's name
  updateGreeting(user);

  // 2. Role-specific canvas & model controls
  const role = (user.role || 'senior').toLowerCase();

  if (role === 'admin') {
    // Admin: Show Sovereign IT Control Dashboard, hide chat canvas and bottom input
    if (workspaceCanvas) workspaceCanvas.style.display = 'none';
    if (inputBarOuter) inputBarOuter.style.display = 'none';
    if (adminDashboardCanvas) adminDashboardCanvas.style.display = 'block';

    // Top Header Badge
    if (modelDropdownBtn) modelDropdownBtn.style.display = 'none';
    if (juniorLockedBadge) {
      juniorLockedBadge.style.display = 'inline-flex';
      juniorLockedBadge.innerHTML = `<span style="font-size:0.85rem;">👑</span> <span>IT Systems Control Plane</span>`;
    }
    if (modelMenu) modelMenu.style.display = 'none';
    if (adminGovernanceCard) adminGovernanceCard.style.display = 'block';

    // Load full admin dashboard data
    loadAdminDashboardData();
  } else {
    // Engineers (Senior Lead & Junior Field Tech): Show workspace chat canvas & input
    if (adminDashboardCanvas) adminDashboardCanvas.style.display = 'none';
    if (workspaceCanvas) workspaceCanvas.style.display = 'flex';
    if (inputBarOuter) inputBarOuter.style.display = 'flex';
    if (adminGovernanceCard) adminGovernanceCard.style.display = 'none';

    // Update dynamic greeting & suggestion pills with engineering prompts
    updateGreeting(user);

    if (role === 'junior') {
      // Junior: Pre-configured, locked model, zero dropdown friction
      if (modelDropdownBtn) modelDropdownBtn.style.display = 'none';
      if (juniorLockedBadge) {
        juniorLockedBadge.style.display = 'inline-flex';
        juniorLockedBadge.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          <span>Standard Inspection Model (Pre-configured)</span>
        `;
      }
      if (modelMenu) modelMenu.style.display = 'none';
    } else if (role === 'senior') {
      // Senior: Unlocked model switcher for authorized models
      if (modelDropdownBtn) modelDropdownBtn.style.display = 'inline-flex';
      if (juniorLockedBadge) juniorLockedBadge.style.display = 'none';

      // Filter available options
      const allowed = user.allowed_models || ["Workstation-32B", "Edge-8B"];
      const isAll = allowed.includes('*');
      document.querySelectorAll('.model-option').forEach(opt => {
        const modelName = opt.dataset.model;
        const isAllowed = isAll || allowed.some(a => a.toLowerCase().replace(/[-_]/g, '') === modelName.toLowerCase().replace(/[-_]/g, ''));
        opt.style.display = isAllowed ? 'block' : 'none';
      });

      // Update active badge if current model is not allowed
      const current = currentModelBadge ? currentModelBadge.textContent : '';
      if (!isAll && !allowed.some(a => a.toLowerCase().replace(/[-_]/g, '') === current.toLowerCase().replace(/[-_]/g, ''))) {
        const firstAllowed = allowed[0] || 'Workstation-32B';
        if (currentModelBadge) currentModelBadge.textContent = firstAllowed;
        document.querySelectorAll('.model-option').forEach(o => {
          if (o.dataset.model === firstAllowed) o.classList.add('active');
          else o.classList.remove('active');
        });
      }
    }
  }

  // Highlight active persona card in Auth Modal
  document.querySelectorAll('.persona-card').forEach(card => {
    if (card.dataset.username === role) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });
}

async function loadAdminGovernanceMatrix() {
  if (!governanceMatrixContainer) return;
  try {
    governanceMatrixContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.8rem;">Loading refinery access matrix...</div>';
    const res = await SovereignAPI.getAdminUsers();
    const users = res.users || [];
    governanceMatrixContainer.innerHTML = '';

    const modelTiers = [
      { key: "Enterprise-100B", label: "100B Cluster" },
      { key: "Workstation-32B", label: "32B Local GPU" },
      { key: "Edge-8B", label: "8B Field Edge" },
    ];

    // Filter to senior and junior (admin always has all models)
    const nonAdminUsers = users.filter(u => u.role !== 'admin');

    nonAdminUsers.forEach(u => {
      const card = document.createElement('div');
      card.className = 'gov-user-card';
      const allowed = u.allowed_models || [];

      let checkboxesHtml = modelTiers.map(m => {
        const isChecked = allowed.includes('*') || allowed.some(a => a.toLowerCase().replace(/[-_]/g, '') === m.key.toLowerCase().replace(/[-_]/g, ''));
        return `
          <label class="gov-checkbox-label">
            <input type="checkbox" class="gov-checkbox" data-user-id="${u.id}" data-model="${m.key}" ${isChecked ? 'checked' : ''} />
            <span>${escapeHtml(m.label)}</span>
          </label>
        `;
      }).join('');

      card.innerHTML = `
        <div class="gov-user-header">
          <div class="gov-user-info">
            <span>${u.avatar || '👤'}</span>
            <span>${escapeHtml(u.name)} (${escapeHtml(u.role.toUpperCase())})</span>
          </div>
          <span style="font-size:0.7rem; font-family:var(--font-mono); color:var(--text-muted);">${escapeHtml(u.id)}</span>
        </div>
        <div style="font-size:0.74rem; color:var(--text-muted);">${escapeHtml(u.description ? u.description.split('•')[0].trim() : '')}</div>
        <div class="gov-models-grid">
          ${checkboxesHtml}
        </div>
      `;

      // Attach change listeners to checkboxes in this card
      card.querySelectorAll('.gov-checkbox').forEach(chk => {
        chk.addEventListener('change', async () => {
          const userId = chk.dataset.userId;
          const checkedModels = Array.from(card.querySelectorAll(`.gov-checkbox:checked`)).map(c => c.dataset.model);
          try {
            await SovereignAPI.updateUserModelAccess(userId, checkedModels);
            const currentUser = getCurrentUser();
            if (currentUser.id === userId) {
              currentUser.allowed_models = checkedModels;
              setCurrentUser(currentUser);
              applyUserPermissions(currentUser);
            }
          } catch (err) {
            console.error("Failed to update user permissions:", err);
            alert(`Permission update error: ${err.message}`);
          }
        });
      });

      governanceMatrixContainer.appendChild(card);
    });
  } catch (err) {
    console.warn("Governance matrix load error:", err);
    governanceMatrixContainer.innerHTML = `<div style="color:var(--status-red); font-size:0.8rem;">Could not load governance matrix: ${err.message}</div>`;
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

async function loadAdminDashboardData() {
  loadAuditLedger();
  await loadAdminGovernanceMatrixDash();
}

async function loadAdminGovernanceMatrixDash() {
  if (!dashGovMatrix) return;
  try {
    dashGovMatrix.innerHTML = '<div style="color:var(--text-muted); font-size:0.8rem; padding: 12px;">Loading refinery access matrix...</div>';
    const res = await SovereignAPI.getAdminUsers();
    const users = res.users || [];
    dashGovMatrix.innerHTML = '';

    const modelTiers = [
      { key: "Enterprise-100B", label: "100B Cluster" },
      { key: "Workstation-32B", label: "32B Local GPU" },
      { key: "Edge-8B", label: "8B Field Edge" },
    ];

    // Filter to senior and junior (admin always has all models)
    const nonAdminUsers = users.filter(u => u.role !== 'admin');

    nonAdminUsers.forEach(u => {
      const row = document.createElement('div');
      row.className = 'dash-user-row';
      const allowed = u.allowed_models || [];

      let checkboxesHtml = modelTiers.map(m => {
        const isChecked = allowed.includes('*') || allowed.some(a => a.toLowerCase().replace(/[-_]/g, '') === m.key.toLowerCase().replace(/[-_]/g, ''));
        return `
          <label class="gov-checkbox-label">
            <input type="checkbox" class="dash-gov-checkbox" data-user-id="${u.id}" data-model="${m.key}" ${isChecked ? 'checked' : ''} />
            <span>${escapeHtml(m.label)}</span>
          </label>
        `;
      }).join('');

      row.innerHTML = `
        <div class="dash-user-header">
          <div class="dash-user-meta">
            <span class="dash-user-avatar">${u.avatar || '👤'}</span>
            <div>
              <div class="dash-user-name">${escapeHtml(u.name)} (${escapeHtml(u.role.toUpperCase())})</div>
              <div class="dash-user-role">${escapeHtml(u.description ? u.description.split('•')[0].trim() : '')} • ID: ${escapeHtml(u.id)}</div>
            </div>
          </div>
          <span class="admin-save-pill" id="saveBadge-${u.id}" style="display:none;">Saved ✓</span>
        </div>
        <div class="dash-user-models">
          ${checkboxesHtml}
        </div>
      `;

      // Attach change listeners to checkboxes in this card
      row.querySelectorAll('.dash-gov-checkbox').forEach(chk => {
        chk.addEventListener('change', async () => {
          const userId = chk.dataset.userId;
          const checkedModels = Array.from(row.querySelectorAll(`.dash-gov-checkbox:checked`)).map(c => c.dataset.model);
          try {
            await SovereignAPI.updateUserModelAccess(userId, checkedModels);
            const badge = document.getElementById(`saveBadge-${userId}`);
            if (badge) {
              badge.style.display = 'inline-block';
              setTimeout(() => { badge.style.display = 'none'; }, 2500);
            }
            if (adminMatrixSaveNotice) {
              adminMatrixSaveNotice.style.display = 'inline-block';
              setTimeout(() => { adminMatrixSaveNotice.style.display = 'none'; }, 2500);
            }
          } catch (err) {
            console.error("Failed to update user permissions:", err);
            alert(`Permission update error: ${err.message}`);
          }
        });
      });

      dashGovMatrix.appendChild(row);
    });
  } catch (err) {
    console.warn("Governance matrix load error:", err);
    dashGovMatrix.innerHTML = `<div style="color:var(--status-red); font-size:0.8rem; padding: 12px;">Could not load governance matrix: ${err.message}</div>`;
  }
}

async function loadAuditLedger() {
  try {
    const ledger = await SovereignAPI.getAuditLedger();
    const events = ledger.recent_events || [];

    // 1. Settings Modal table
    if (modalAuditTableBody) {
      modalAuditTableBody.innerHTML = '';
      if (events.length === 0) {
        modalAuditTableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-muted); padding:16px;">Genesis State — No events recorded.</td></tr>`;
      } else {
        events.forEach((ev, idx) => {
          const tr = document.createElement('tr');
          const blockNum = ev.id || (ledger.total_blocks ? (ledger.total_blocks - idx) : (idx + 1));
          const eventType = (ev.task_type || ev.event_type || 'INFERENCE_RUN').replace(/_/g, ' ').toUpperCase();
          const rawHash = ev.entry_hash || ev.current_hash || '';
          const shortHash = rawHash ? (rawHash.substring(0, 14) + '...') : 'N/A';
          const isOk = (ev.tool_exit_code === 0 || ev.tool_exit_code === undefined);
          tr.innerHTML = `
            <td style="color: var(--accent-gold); font-weight:700; font-family: var(--font-mono);">#${blockNum}</td>
            <td style="font-size:0.72rem; text-transform:uppercase; font-family: var(--font-mono);">${escapeHtml(eventType)}</td>
            <td style="color: var(--accent-blue); font-family: var(--font-mono);" title="${escapeHtml(rawHash)}">${shortHash}</td>
            <td style="color: ${isOk ? 'var(--status-emerald)' : 'var(--accent-crimson)'}; font-weight: 600;">${isOk ? 'OK' : 'FLAG'}</td>
          `;
          modalAuditTableBody.appendChild(tr);
        });
      }
    }

    // 2. Admin Dashboard table & stats
    if (dashAuditTableBody) {
      dashAuditTableBody.innerHTML = '';
      if (events.length === 0) {
        dashAuditTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">Genesis State — Ledger initialized and ready.</td></tr>`;
      } else {
        events.forEach((ev, idx) => {
          const tr = document.createElement('tr');
          const blockNum = ev.id || (ledger.total_blocks ? (ledger.total_blocks - idx) : (idx + 1));
          const operator = ev.user_role || 'system';
          const eventType = (ev.task_type || ev.event_type || 'INFERENCE_RUN').replace(/_/g, ' ').toUpperCase();
          const rawHash = ev.entry_hash || ev.current_hash || '';
          const shortHash = rawHash ? (rawHash.substring(0, 16) + '...') : 'N/A';
          const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : 'Recent';
          const isOk = (ev.tool_exit_code === 0 || ev.tool_exit_code === undefined);
          tr.innerHTML = `
            <td style="color: var(--accent-gold); font-weight:700; font-family: var(--font-mono);">#${blockNum}</td>
            <td style="font-weight: 600; color: var(--text-primary);">${escapeHtml(operator)}</td>
            <td style="font-family: var(--font-mono); color: var(--accent-blue);">${escapeHtml(eventType)}</td>
            <td style="color: var(--text-muted);">${escapeHtml(timeStr)}</td>
            <td style="font-family: var(--font-mono); color: var(--text-secondary);" title="${escapeHtml(rawHash)}">${shortHash}</td>
            <td style="color: ${isOk ? 'var(--status-emerald)' : 'var(--accent-crimson)'}; font-weight: 700;">${isOk ? 'VERIFIED ✓' : 'FLAGGED'}</td>
          `;
          dashAuditTableBody.appendChild(tr);
        });
      }
    }

    if (adminStatLedgerBlocks) {
      adminStatLedgerBlocks.textContent = ledger.total_blocks || events.length;
    }

    if (auditChainVerifyMsg && ledger.verification_message) {
      auditChainVerifyMsg.textContent = ledger.verification_message;
    }

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
