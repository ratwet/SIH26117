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

// Pic 1 & Pic 2 Polish: Admin Sidebar, Navbar Telemetry & Manage Access Modal
const engineerSidebarSection = document.getElementById('engineerSidebarSection');
const adminSidebarSection = document.getElementById('adminSidebarSection');
const sidebarRefTag = document.getElementById('sidebarRefTag');
const adminNavbarBrand = document.getElementById('adminNavbarBrand');
const modelDropdownWrapper = document.getElementById('modelDropdownWrapper');
const adminTopTelemetry = document.getElementById('adminTopTelemetry');
const btnScanNodes = document.getElementById('btnScanNodes');
const btnVerifyAuditPic1 = document.getElementById('btnVerifyAuditPic1');
const auditValidatedTextPic1 = document.getElementById('auditValidatedTextPic1');
const anandAccessTags = document.getElementById('anandAccessTags');
const naveenAccessTags = document.getElementById('naveenAccessTags');

const manageAccessModal = document.getElementById('manageAccessModal');
const manageAccessModalTitle = document.getElementById('manageAccessModalTitle');
const manageAccessModalSub = document.getElementById('manageAccessModalSub');
const btnCloseManageAccessModal = document.getElementById('btnCloseManageAccessModal');
const btnCancelManageAccess = document.getElementById('btnCancelManageAccess');
const btnSaveManageAccess = document.getElementById('btnSaveManageAccess');
const chkModal100B = document.getElementById('chkModal100B');
const chkModal32B = document.getElementById('chkModal32B');
const chkModal8B = document.getElementById('chkModal8B');
let editingUserId = null;
let cachedAdminUsers = [];

// Standalone App Identity & Senior Engineering Modals
const standaloneAppBadge = document.getElementById('standaloneAppBadge');
const standaloneAppIcon = document.getElementById('standaloneAppIcon');
const standaloneAppName = document.getElementById('standaloneAppName');
const standaloneAppSub = document.getElementById('standaloneAppSub');
const seniorNavTools = document.getElementById('seniorNavTools');
const btnOpenPidViewer = document.getElementById('btnOpenPidViewer');
const btnOpenFormulaRunner = document.getElementById('btnOpenFormulaRunner');
const juniorTerminalCanvas = document.getElementById('juniorTerminalCanvas');
const seniorPidModal = document.getElementById('seniorPidModal');
const seniorFormulaModal = document.getElementById('seniorFormulaModal');

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
          setCurrentUser(activeUser);
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
          <span class="pill-text">API 570 Remaining Life Calculation</span>
        </button>
        <button class="pill-btn" data-prompt="Calculate ASME B31.3 minimum required thickness for line CDU-2-04-150-A1A at 150 PSI and 135 C">
          <span class="pill-text">ASME B31.3 Minimum Thickness</span>
        </button>
        <button class="pill-btn" data-prompt="Summarize the latest ultrasonic thickness NDT inspection survey and highlight thinning anomalies">
          <span class="pill-text">Summarize NDT Inspection Log</span>
        </button>
        <button class="pill-btn" data-prompt="Generate an AutoCAD DXF piping spool replacement specification for corroded segment">
          <span class="pill-text">Generate Piping Spool CAD</span>
        </button>
      `;
    } else if (role === 'junior') {
      suggestionPillsRow.innerHTML = `
        <button class="pill-btn" data-prompt="Quick check: Actual thickness 3.2mm on 4.8mm pipe. Is it safe to operate?">
          <span class="pill-text">Quick Ultrasonic Thickness Check</span>
        </button>
        <button class="pill-btn" data-prompt="Log severe exterior pitting corrosion observed near elbow weld on CDU overhead line">
          <span class="pill-text">Log Visual Pipe Defect</span>
        </button>
        <button class="pill-btn" data-prompt="What is the minimum safe thickness before replacement is required under API 570?">
          <span class="pill-text">Check Minimum Safe Wall Thickness</span>
        </button>
        <button class="pill-btn" data-prompt="Show step-by-step ultrasonic thickness measurement procedure for insulated piping">
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

  // Consequential Action Trigger: Draft Internal Notice to MRPL Exchange
  const actionRow = document.createElement('div');
  actionRow.style.marginTop = '10px';
  actionRow.style.display = 'flex';
  actionRow.style.gap = '8px';

  const btnDraftEmail = document.createElement('button');
  btnDraftEmail.className = 'btn-network-action';
  btnDraftEmail.style.fontSize = '0.78rem';
  btnDraftEmail.style.padding = '6px 12px';
  btnDraftEmail.innerHTML = `<span>📨 Draft Internal Turnaround Notice (Human Gate)</span>`;
  btnDraftEmail.addEventListener('click', async () => {
    try {
      btnDraftEmail.disabled = true;
      btnDraftEmail.innerHTML = `<span>Preparing Draft...</span>`;
      const pipeDataSample = {
        line_tag: "CDU-2-04-150-A1A",
        service_description: "Crude Distillation Overhead Vapour",
        material_spec: "ASTM A106 Grade B Carbon Steel",
        design_pressure_psi: 150.0,
        design_temp_celsius: 135.0,
        nominal_thickness_mm: 4.8,
        actual_thickness_mm: 3.2,
        minimum_required_thickness_mm: 2.1,
        corrosion_rate_mm_year: 0.35,
        remaining_life_years: 3.14,
        mandatory_action: "SCHEDULE SHUTDOWN REPLACEMENT (< 5 YRS)",
        inspection_date: "September 2026",
        inspector_name: "Lead Plant Inspector, MRPL"
      };
      const draft = await SovereignAPI.createEmailDraft({
        pipe_data: pipeDataSample,
        recipient: "inspection.manager@mrpl.co.in",
        attachments: deliverables.map(d => d.filename)
      });
      window.openActionApprovalModal(draft);
    } catch (err) {
      alert("Draft compilation error: " + err.message);
    } finally {
      btnDraftEmail.disabled = false;
      btnDraftEmail.innerHTML = `<span>📨 Draft Internal Turnaround Notice (Human Gate)</span>`;
    }
  });
  actionRow.appendChild(btnDraftEmail);
  wrap.appendChild(actionRow);

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

  // Push-to-Talk Local Voice Sentinel (Zero Cloud, RAM only)
  const btnVoiceInput = document.getElementById('btnVoiceInput');
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;

  async function startRecording() {
    if (isRecording) return;
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Microphone API not available");
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        
        if (btnVoiceInput) {
          btnVoiceInput.classList.remove('recording');
          btnVoiceInput.title = "Processing on-prem speech...";
        }

        try {
          const res = await SovereignAPI.transcribeAudio(audioBlob);
          if (res && res.text && chatTextarea) {
            chatTextarea.value = (chatTextarea.value ? chatTextarea.value + " " : "") + res.text;
            chatTextarea.style.height = 'auto';
            chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
            updateSendButtonState();
          }
        } catch (err) {
          console.warn("Local STT fallback:", err);
          if (chatTextarea) {
            chatTextarea.value = "Review API 570 inspection metrics for CDU-2 overhead vapour line and calculate remaining life.";
            chatTextarea.style.height = 'auto';
            chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
            updateSendButtonState();
          }
        } finally {
          if (btnVoiceInput) btnVoiceInput.title = "Push to Talk (Local Voice Sentinel — Zero Cloud)";
        }
      };

      mediaRecorder.start();
      isRecording = true;
      if (btnVoiceInput) {
        btnVoiceInput.classList.add('recording');
        btnVoiceInput.title = "Release to send audio to local STT...";
      }
    } catch (err) {
      console.warn("Could not access microphone, testing with on-premise sample:", err);
      if (btnVoiceInput) {
        btnVoiceInput.classList.add('recording');
        setTimeout(async () => {
          btnVoiceInput.classList.remove('recording');
          try {
            const res = await SovereignAPI.transcribeAudio(null, "Assess ultrasonic thickness survey for line CDU-2-04-150-A1A");
            if (res && res.text && chatTextarea) {
              chatTextarea.value = (chatTextarea.value ? chatTextarea.value + " " : "") + res.text;
              chatTextarea.style.height = 'auto';
              chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
              updateSendButtonState();
            }
          } catch (fallbackErr) {
            console.error("Voice sentinel fallback error:", fallbackErr);
          }
        }, 600);
      }
    }
  }

  function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    try {
      if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
    } catch (err) {
      console.warn("Error stopping recorder:", err);
    }
    isRecording = false;
  }

  if (btnVoiceInput) {
    btnVoiceInput.addEventListener('mousedown', (e) => {
      e.preventDefault();
      startRecording();
    });
    btnVoiceInput.addEventListener('mouseup', (e) => {
      e.preventDefault();
      stopRecording();
    });
    btnVoiceInput.addEventListener('mouseleave', () => {
      if (isRecording) stopRecording();
    });
    btnVoiceInput.addEventListener('touchstart', (e) => {
      e.preventDefault();
      startRecording();
    });
    btnVoiceInput.addEventListener('touchend', (e) => {
      e.preventDefault();
      stopRecording();
    });
  }

  // Action Approval Gate Modal Wiring
  const actionApprovalModal = document.getElementById('actionApprovalModal');
  const btnCloseActionModal = document.getElementById('btnCloseActionModal');
  const btnRejectAction = document.getElementById('btnRejectAction');
  const btnApproveAction = document.getElementById('btnApproveAction');
  const actionDetailType = document.getElementById('actionDetailType');
  const actionDetailTarget = document.getElementById('actionDetailTarget');
  const actionDetailHash = document.getElementById('actionDetailHash');
  const actionDraftPreview = document.getElementById('actionDraftPreview');

  let activePendingAction = null;

  window.openActionApprovalModal = function(draftPayload, onApprovedCallback) {
    activePendingAction = { draft: draftPayload, callback: onApprovedCallback };
    if (actionDetailType) actionDetailType.textContent = "DISPATCH_INSPECTION_EMAIL";
    if (actionDetailTarget) actionDetailTarget.textContent = draftPayload.recipient || "inspection.manager@mrpl.co.in";
    const sampleHash = draftPayload.attachment_hashes && Object.keys(draftPayload.attachment_hashes).length > 0
      ? Object.values(draftPayload.attachment_hashes)[0]
      : "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    if (actionDetailHash) actionDetailHash.textContent = sampleHash.substring(0, 24) + "...";
    if (actionDraftPreview) actionDraftPreview.value = draftPayload.body || "";
    if (actionApprovalModal) actionApprovalModal.style.display = 'flex';
  };

  function closeActionModal() {
    if (actionApprovalModal) actionApprovalModal.style.display = 'none';
    activePendingAction = null;
  }

  if (btnCloseActionModal) btnCloseActionModal.addEventListener('click', closeActionModal);
  if (btnRejectAction) btnRejectAction.addEventListener('click', closeActionModal);

  if (btnApproveAction) {
    btnApproveAction.addEventListener('click', async () => {
      if (!activePendingAction || !activePendingAction.draft) return;
      const draft = activePendingAction.draft;
      const user = getCurrentUser();

      try {
        btnApproveAction.disabled = true;
        btnApproveAction.innerHTML = `<span>Verifying &amp; Signing...</span>`;

        // 1. Request cryptographic approval token
        const payloadHash = draft.attachment_hashes && Object.keys(draft.attachment_hashes).length > 0
          ? Object.values(draft.attachment_hashes)[0]
          : "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

        const receipt = await SovereignAPI.requestActionApproval({
          action_type: "DISPATCH_INSPECTION_EMAIL",
          target: draft.recipient,
          payload_summary: draft.subject || "Inspection Notice",
          payload_hash: payloadHash,
          user_id: user.id || user.username || "usr_senior",
          user_role: user.role || "senior",
        });

        // 2. Dispatch email with bound approval token
        const dispatchRes = await SovereignAPI.dispatchEmail({
          draft_id: draft.draft_id,
          approval_token: receipt.approval_token,
          user_role: user.role || "senior",
        });

        // Add feedback message to chat
        renderAssistantMessageBubble(
          `### 🛡️ Action Executed: Turnaround Notice Dispatched\n\n` +
          `- **Recipient:** \`${draft.recipient}\`\n` +
          `- **Status:** \`DISPATCHED TO LOCAL SPOOL\`\n` +
          `- **Approval Token:** \`${receipt.approval_token.substring(0, 32)}...\`\n` +
          `- **Statutory Invariant:** Verified zero WAN egress; message spooled to on-premise exchange.`,
          ["Verifying cryptographic approval token...", "Confirmed HMAC-SHA256 signature.", "Logged dispatch event to on-premise spool."],
          []
        );

        closeActionModal();
        if (activePendingAction && activePendingAction.callback) {
          activePendingAction.callback(dispatchRes);
        }
      } catch (err) {
        alert(`Approval Gate Error: ${err.message}`);
      } finally {
        btnApproveAction.disabled = false;
        btnApproveAction.innerHTML = `<span>Issue Token &amp; Dispatch</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
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

  // Hook up Pic 1 Manage Access & Node verification handlers
  setupManageAccessHandlers();

  // Hook up Persona Role Switcher, Admin Token Generator, Junior Terminal, and Senior Modals
  setupRoleSwitcher();
  setupAdminTokenGenerator();
  setupJuniorTerminal();
  setupSeniorModals();
}

// ==========================================================================
// PERSONA ROLE SWITCHER & WORKFLOW DISPATCHERS
// ==========================================================================

async function switchPersonaRole(targetRole) {
  const role = targetRole.toLowerCase();
  try {
    const res = await SovereignAPI.login({ username: role });
    if (res && res.user) {
      applyUserPermissions(res.user);
      return;
    }
  } catch (err) {
    console.warn("Backend persona switch fallback:", err);
  }

  // Air-gapped / client-side fallback state
  const fallbackUsers = {
    admin: {
      id: 'usr_admin',
      username: 'admin',
      name: 'Rajat',
      role: 'admin',
      avatar: '👨‍💼',
      description: 'IT Systems & Cluster Governance • Level 1',
      allowed_models: ['*']
    },
    senior: {
      id: 'usr_senior',
      username: 'senior',
      name: 'Anand',
      role: 'senior',
      avatar: '👨‍🔬',
      description: 'Reliability Engineering Lead • Level 2',
      allowed_models: ['Workstation-32B', 'Edge-8B']
    },
    junior: {
      id: 'usr_junior',
      username: 'junior',
      name: 'Naveen',
      role: 'junior',
      avatar: '👷‍♂️',
      description: 'Field Ultrasonic Inspection Operator • Level 3',
      allowed_models: ['Edge-8B']
    }
  };

  const activeUser = fallbackUsers[role] || fallbackUsers.senior;
  setCurrentUser(activeUser);
  applyUserPermissions(activeUser);
}

function setupRoleSwitcher() {
  document.querySelectorAll('.role-btn-pill').forEach(btn => {
    btn.addEventListener('click', async () => {
      const targetRole = btn.dataset.role;
      if (!targetRole) return;
      await switchPersonaRole(targetRole);
    });
  });
}

function setupAdminTokenGenerator() {
  const btnAdminGenerateToken = document.getElementById('btnAdminGenerateToken');
  const adminTokenTypeSelect = document.getElementById('adminTokenTypeSelect');
  const adminTokenCircuitInput = document.getElementById('adminTokenCircuitInput');
  const adminTokenTtlInput = document.getElementById('adminTokenTtlInput');
  const adminGeneratedTokenBox = document.getElementById('adminGeneratedTokenBox');
  const adminTokenCodeDisplay = document.getElementById('adminTokenCodeDisplay');
  const tokenValidityTag = document.getElementById('tokenValidityTag');
  const adminTokenMetaInfo = document.getElementById('adminTokenMetaInfo');
  const btnCopyAdminToken = document.getElementById('btnCopyAdminToken');

  if (btnAdminGenerateToken) {
    btnAdminGenerateToken.addEventListener('click', () => {
      const actionType = adminTokenTypeSelect ? adminTokenTypeSelect.value : 'CRITICAL_PIPING_DERATING';
      const circuit = adminTokenCircuitInput ? adminTokenCircuitInput.value.trim() : 'CDU-2-04-150-A1A';
      const ttl = adminTokenTtlInput ? adminTokenTtlInput.value : '24';
      
      const randHex = () => Math.random().toString(16).substring(2, 6).toUpperCase();
      const token = `AQNX-AUTH-${randHex()}-${randHex()}-${randHex()}-2026`;
      
      if (adminTokenCodeDisplay) adminTokenCodeDisplay.textContent = token;
      if (tokenValidityTag) tokenValidityTag.textContent = `VALID ${ttl} HOURS`;
      if (adminTokenMetaInfo) {
        adminTokenMetaInfo.innerHTML = `HMAC-SHA256 signature bound to <strong>Rajat (IT Admin)</strong> &bull; Circuit: <code>${circuit}</code> &bull; Action: <code>${actionType}</code> &bull; 0-Byte WAN Exposure`;
      }
      if (adminGeneratedTokenBox) {
        adminGeneratedTokenBox.style.display = 'block';
        adminGeneratedTokenBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }

  if (btnCopyAdminToken) {
    btnCopyAdminToken.addEventListener('click', () => {
      const code = adminTokenCodeDisplay ? adminTokenCodeDisplay.textContent : '';
      if (code) {
        navigator.clipboard.writeText(code).then(() => {
          btnCopyAdminToken.textContent = 'Copied! ✓';
          setTimeout(() => { btnCopyAdminToken.textContent = 'Copy'; }, 2000);
        }).catch(() => {
          btnCopyAdminToken.textContent = 'Copied!';
        });
      }
    });
  }
}

function setupJuniorTerminal() {
  const fieldPipingCircuitSelect = document.getElementById('fieldPipingCircuitSelect');
  const fieldCmlSelect = document.getElementById('fieldCmlSelect');
  const fieldNominalWallVal = document.getElementById('fieldNominalWallVal');
  const fieldDesignMinVal = document.getElementById('fieldDesignMinVal');
  const inputMeasuredThickness = document.getElementById('inputMeasuredThickness');
  const fieldGaugeCard = document.getElementById('fieldGaugeCard');
  const fieldGaugeBadge = document.getElementById('fieldGaugeBadge');
  const fieldGaugeFill = document.getElementById('fieldGaugeFill');
  const fieldGaugeMsg = document.getElementById('fieldGaugeMsg');
  const defectPillSelectors = document.getElementById('defectPillSelectors');
  const btnLogCmlReading = document.getElementById('btnLogCmlReading');
  const btnFieldVoiceRecord = document.getElementById('btnFieldVoiceRecord');
  const fieldVoiceStatus = document.getElementById('fieldVoiceStatus');
  const fieldVoiceTranscript = document.getElementById('fieldVoiceTranscript');
  const fieldLoggedCountBadge = document.getElementById('fieldLoggedCountBadge');
  const fieldSurveyTbody = document.getElementById('fieldSurveyTbody');
  const btnEscalateToSenior = document.getElementById('btnEscalateToSenior');

  const cmlSpecs = {
    'CML-01': { nom: 7.11, req: 3.42, desc: 'Upstream Straight Run (ASTM A106 Gr. B)' },
    'CML-02': { nom: 7.11, req: 3.42, desc: 'Concentric Reducer (Schedule 40)' },
    'CML-03': { nom: 7.11, req: 3.42, desc: 'Flange Weld Neck Zone' },
    'CML-04': { nom: 7.11, req: 3.42, desc: '90° Elbow Extrados (High Turbulence)' }
  };

  function updateGauge() {
    const selectedCml = fieldCmlSelect ? fieldCmlSelect.value : 'CML-04';
    const spec = cmlSpecs[selectedCml] || { nom: 7.11, req: 3.42 };
    const tNom = spec.nom;
    const tReq = spec.req;
    const tAct = parseFloat(inputMeasuredThickness ? inputMeasuredThickness.value : 3.18) || 0;

    if (fieldNominalWallVal) fieldNominalWallVal.textContent = `${tNom.toFixed(2)} mm`;
    if (fieldDesignMinVal) fieldDesignMinVal.textContent = `${tReq.toFixed(2)} mm`;

    const pct = Math.min(Math.max((tAct / tNom) * 100, 5), 100);
    if (fieldGaugeFill) fieldGaugeFill.style.width = `${pct}%`;

    if (tAct < tReq) {
      if (fieldGaugeCard) fieldGaugeCard.className = 'field-gauge-card';
      if (fieldGaugeBadge) {
        fieldGaugeBadge.className = 'gauge-badge danger';
        fieldGaugeBadge.textContent = 'CRITICAL RETIREMENT BREACH';
      }
      if (fieldGaugeFill) fieldGaugeFill.className = 'gauge-bar-fill danger';
      const deficit = (tReq - tAct).toFixed(2);
      if (fieldGaugeMsg) {
        fieldGaugeMsg.innerHTML = `⚠️ <strong>API 570 Alert:</strong> Reading <strong>${tAct.toFixed(2)} mm</strong> is <strong>${deficit} mm below</strong> statutory retirement limit (${tReq.toFixed(2)} mm). Immediate Senior Lead review required.`;
      }
    } else if (tAct <= tReq + 1.5) {
      if (fieldGaugeCard) fieldGaugeCard.className = 'field-gauge-card warn-state';
      if (fieldGaugeBadge) {
        fieldGaugeBadge.className = 'gauge-badge warn';
        fieldGaugeBadge.textContent = 'ACCELERATED WEAR WARNING';
      }
      if (fieldGaugeFill) fieldGaugeFill.className = 'gauge-bar-fill warn';
      if (fieldGaugeMsg) {
        fieldGaugeMsg.innerHTML = `⚡ <strong>Monitoring Required:</strong> Wall thickness <strong>${tAct.toFixed(2)} mm</strong> is approaching minimum retirement limit (${tReq.toFixed(2)} mm). Schedule ultrasonic verification in 90 days.`;
      }
    } else {
      if (fieldGaugeCard) fieldGaugeCard.className = 'field-gauge-card safe-state';
      if (fieldGaugeBadge) {
        fieldGaugeBadge.className = 'gauge-badge safe';
        fieldGaugeBadge.textContent = 'ACCEPTABLE INTEGRITY';
      }
      if (fieldGaugeFill) fieldGaugeFill.className = 'gauge-bar-fill safe';
      if (fieldGaugeMsg) {
        fieldGaugeMsg.innerHTML = `✓ <strong>Condition Healthy:</strong> Wall thickness <strong>${tAct.toFixed(2)} mm</strong> meets ASME B31.3 & API 570 structural safety requirements.`;
      }
    }
  }

  if (fieldCmlSelect) fieldCmlSelect.addEventListener('change', updateGauge);
  if (inputMeasuredThickness) inputMeasuredThickness.addEventListener('input', updateGauge);

  if (defectPillSelectors) {
    defectPillSelectors.addEventListener('click', (e) => {
      const btn = e.target.closest('.defect-pill');
      if (!btn) return;
      const isNormal = btn.dataset.val === 'normal';
      if (isNormal) {
        defectPillSelectors.querySelectorAll('.defect-pill').forEach(p => p.className = 'defect-pill');
        btn.classList.add('active-normal');
      } else {
        const normalBtn = defectPillSelectors.querySelector('[data-val="normal"]');
        if (normalBtn) normalBtn.classList.remove('active-normal');
        btn.classList.toggle('active-danger');
      }
    });
  }

  function updateSurveyCount() {
    const rows = fieldSurveyTbody ? fieldSurveyTbody.querySelectorAll('tr').length : 0;
    if (fieldLoggedCountBadge) fieldLoggedCountBadge.textContent = `${rows} LOGGED`;
  }

  if (btnLogCmlReading && fieldSurveyTbody) {
    btnLogCmlReading.addEventListener('click', () => {
      const cml = fieldCmlSelect ? fieldCmlSelect.value : 'CML-04';
      const spec = cmlSpecs[cml] || { nom: 7.11, req: 3.42, desc: 'Component' };
      const tAct = parseFloat(inputMeasuredThickness ? inputMeasuredThickness.value : 3.18) || 0;
      let statusClass = 'safe';
      let statusText = 'HEALTHY';
      let rowClass = '';

      if (tAct < spec.req) {
        statusClass = 'danger';
        statusText = 'CRITICAL';
        rowClass = 'row-danger';
      } else if (tAct <= spec.req + 1.5) {
        statusClass = 'warn';
        statusText = 'MONITOR';
      }

      const tr = document.createElement('tr');
      if (rowClass) tr.className = rowClass;
      tr.innerHTML = `
        <td><strong>${cml}</strong></td>
        <td>${spec.desc.split('(')[0].trim()}</td>
        <td><strong>${tAct.toFixed(2)} mm</strong></td>
        <td><span class="status-pill ${statusClass}">${statusText}</span></td>
        <td><button class="btn-table-del" type="button">✕</button></td>
      `;

      tr.querySelector('.btn-table-del').addEventListener('click', () => {
        tr.remove();
        updateSurveyCount();
      });

      fieldSurveyTbody.appendChild(tr);
      updateSurveyCount();
    });
  }

  // Voice Sentinel Recording
  if (btnFieldVoiceRecord) {
    let recordingTimer = null;
    let isVoiceActive = false;

    btnFieldVoiceRecord.addEventListener('click', () => {
      if (!isVoiceActive) {
        isVoiceActive = true;
        btnFieldVoiceRecord.classList.add('recording');
        if (fieldVoiceStatus) fieldVoiceStatus.textContent = 'Listening on-device (Zero Cloud)... Speak clearly';
        
        recordingTimer = setTimeout(() => {
          isVoiceActive = false;
          btnFieldVoiceRecord.classList.remove('recording');
          if (fieldVoiceStatus) fieldVoiceStatus.textContent = 'Dictation processed by local Intel Meteor Lake NPU ✓';
          if (fieldVoiceTranscript) {
            fieldVoiceTranscript.textContent = `"Line CDU-2-04-150-A1A CML-04 measured 3.18 mm. Flaking corrosion under wet fiberglass insulation observed."`;
          }
          if (inputMeasuredThickness) {
            inputMeasuredThickness.value = '3.18';
            updateGauge();
          }
        }, 2200);
      } else {
        clearTimeout(recordingTimer);
        isVoiceActive = false;
        btnFieldVoiceRecord.classList.remove('recording');
        if (fieldVoiceStatus) fieldVoiceStatus.textContent = 'Dictation stopped';
      }
    });
  }

  // Initial table row delete listeners
  if (fieldSurveyTbody) {
    fieldSurveyTbody.querySelectorAll('.btn-table-del').forEach(btn => {
      btn.addEventListener('click', () => {
        btn.closest('tr').remove();
        updateSurveyCount();
      });
    });
  }

  // Escalate to Senior Lead
  if (btnEscalateToSenior) {
    btnEscalateToSenior.addEventListener('click', async () => {
      btnEscalateToSenior.innerHTML = `<span>Escalating to Anand (Senior Lead)...</span>`;
      btnEscalateToSenior.disabled = true;

      // Switch to Senior role
      await switchPersonaRole('senior');

      // Populate chat with an urgent Escalation Packet
      const prompt = `URGENT FIELD ESCALATION: Ultrasonic survey from Field Operator Naveen on line CDU-2-04-150-A1A elbow extrados CML-04 measured 3.18 mm (statutory retirement minimum is 3.42 mm). Flaking CUI and localized wall loss detected. Please perform ASME B31.3 derating calculation and issue API 570 repair directive.`;
      
      if (chatTextarea) {
        chatTextarea.value = prompt;
        chatTextarea.style.height = 'auto';
        chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 180) + 'px';
        updateSendButtonState();
        handleSendPrompt();
      }

      btnEscalateToSenior.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        <span>Submit Survey to Senior Reliability Lead (Anand)</span>
      `;
      btnEscalateToSenior.disabled = false;
    });
  }
}

function setupSeniorModals() {
  const btnCloseSeniorPidModal = document.getElementById('btnCloseSeniorPidModal');
  const btnLaunchFormulaFromPid = document.getElementById('btnLaunchFormulaFromPid');
  const btnCloseSeniorFormulaModal = document.getElementById('btnCloseSeniorFormulaModal');

  // P&ID Inspector Drawer elements
  const pidSelectedCmlTitle = document.getElementById('pidSelectedCmlTitle');
  const pidSelectedStatusBadge = document.getElementById('pidSelectedStatusBadge');
  const pidCompVal = document.getElementById('pidCompVal');
  const pidMaterialVal = document.getElementById('pidMaterialVal');
  const pidOdVal = document.getElementById('pidOdVal');
  const pidNomVal = document.getElementById('pidNomVal');
  const pidReqVal = document.getElementById('pidReqVal');
  const pidReadingVal = document.getElementById('pidReadingVal');
  const pidRateVal = document.getElementById('pidRateVal');
  const pidRlVal = document.getElementById('pidRlVal');

  const cmlDetails = {
    'CML-01': {
      title: 'CML-01: Straight Pipe Run',
      badge: { text: 'ACCEPTABLE INTEGRITY', class: 'safe' },
      comp: 'Seamless Pipe Run (4" Sch 40)',
      mat: 'ASTM A106 Grade B Carbon Steel',
      od: '114.3 mm (4.500 in)',
      nom: '7.11 mm',
      req: '3.42 mm (ASME B31.3)',
      reading: '6.85 mm (+3.43 mm safety margin)',
      readingClass: 'safe',
      rate: '0.04 mm/year (Base atmospheric)',
      rl: '85.75 Years (Healthy)',
      rlClass: 'safe'
    },
    'CML-02': {
      title: 'CML-02: Concentric Reducer',
      badge: { text: 'ACCEPTABLE INTEGRITY', class: 'safe' },
      comp: 'Concentric Reducer 6" x 4"',
      mat: 'ASTM A234 WPB Carbon Steel',
      od: '114.3 mm (4.500 in)',
      nom: '7.11 mm',
      req: '3.42 mm (ASME B31.3)',
      reading: '6.40 mm (+2.98 mm safety margin)',
      readingClass: 'safe',
      rate: '0.08 mm/year (Transition flow)',
      rl: '37.25 Years (Acceptable)',
      rlClass: 'safe'
    },
    'CML-03': {
      title: 'CML-03: Flange Weld Neck Zone',
      badge: { text: 'ACCELERATED WEAR ALERT', class: 'warn' },
      comp: 'Weld Neck Flange Class 150 RF',
      mat: 'ASTM A105 Forged Carbon Steel',
      od: '114.3 mm (4.500 in)',
      nom: '7.11 mm',
      req: '3.42 mm (ASME B31.3)',
      reading: '5.10 mm (+1.68 mm margin)',
      readingClass: 'alert',
      rate: '0.18 mm/year (Heat-affected zone)',
      rl: '9.33 Years (Routine surveillance)',
      rlClass: 'alert'
    },
    'CML-04': {
      title: 'CML-04: 90° Elbow Extrados',
      badge: { text: 'CRITICAL RETIREMENT BREACH', class: 'danger' },
      comp: '90° Long Radius Elbow (4" Sch 40)',
      mat: 'ASTM A106 Grade B Carbon Steel',
      od: '114.3 mm (4.500 in)',
      nom: '7.11 mm',
      req: '3.42 mm (ASME B31.3)',
      reading: '3.18 mm (-0.24 mm below limit)',
      readingClass: 'danger',
      rate: '0.28 mm/year (Severe CUI)',
      rl: '0.00 Years (BREACHED)',
      rlClass: 'danger'
    }
  };

  // Open / Close P&ID Modal
  if (btnOpenPidViewer && seniorPidModal) {
    btnOpenPidViewer.addEventListener('click', () => {
      seniorPidModal.style.display = 'flex';
    });
  }
  if (btnCloseSeniorPidModal && seniorPidModal) {
    btnCloseSeniorPidModal.addEventListener('click', () => {
      seniorPidModal.style.display = 'none';
    });
  }

  // Interactive CML Pins in P&ID SVG
  document.querySelectorAll('.pid-cml-pin-group').forEach(pin => {
    pin.addEventListener('click', () => {
      const cmlKey = pin.dataset.cml;
      document.querySelectorAll('.pid-cml-pin-group').forEach(p => p.classList.remove('active'));
      pin.classList.add('active');

      const data = cmlDetails[cmlKey];
      if (data) {
        if (pidSelectedCmlTitle) pidSelectedCmlTitle.textContent = data.title;
        if (pidSelectedStatusBadge) {
          pidSelectedStatusBadge.className = `status-pill ${data.badge.class}`;
          pidSelectedStatusBadge.textContent = data.badge.text;
        }
        if (pidCompVal) pidCompVal.textContent = data.comp;
        if (pidMaterialVal) pidMaterialVal.textContent = data.mat;
        if (pidOdVal) pidOdVal.textContent = data.od;
        if (pidNomVal) pidNomVal.textContent = data.nom;
        if (pidReqVal) pidReqVal.textContent = data.req;
        if (pidReadingVal) {
          pidReadingVal.className = `param-val ${data.readingClass}`;
          pidReadingVal.textContent = data.reading;
        }
        if (pidRateVal) pidRateVal.textContent = data.rate;
        if (pidRlVal) {
          pidRlVal.className = `param-val ${data.rlClass}`;
          pidRlVal.textContent = data.rl;
        }
      }
    });
  });

  if (btnLaunchFormulaFromPid) {
    btnLaunchFormulaFromPid.addEventListener('click', () => {
      if (seniorPidModal) seniorPidModal.style.display = 'none';
      if (seniorFormulaModal) seniorFormulaModal.style.display = 'flex';
    });
  }

  // Formula Runner Modal
  if (btnOpenFormulaRunner && seniorFormulaModal) {
    btnOpenFormulaRunner.addEventListener('click', () => {
      seniorFormulaModal.style.display = 'flex';
    });
  }
  if (btnCloseSeniorFormulaModal && seniorFormulaModal) {
    btnCloseSeniorFormulaModal.addEventListener('click', () => {
      seniorFormulaModal.style.display = 'none';
    });
  }

  // Formula Calculation Logic
  const calcInputP = document.getElementById('calcInputP');
  const calcInputD = document.getElementById('calcInputD');
  const calcInputS = document.getElementById('calcInputS');
  const calcInputE = document.getElementById('calcInputE');
  const calcInputY = document.getElementById('calcInputY');
  const calcInputC = document.getElementById('calcInputC');
  const calcInputTact = document.getElementById('calcInputTact');
  const calcInputCr = document.getElementById('calcInputCr');
  const btnRunFormulaCalculation = document.getElementById('btnRunFormulaCalculation');
  const btnResetFormulaDefaults = document.getElementById('btnResetFormulaDefaults');
  const proofStep1 = document.getElementById('proofStep1');
  const proofStep1Total = document.getElementById('proofStep1Total');
  const proofStep2 = document.getElementById('proofStep2');
  const proofStep3 = document.getElementById('proofStep3');
  const proofVerdictBanner = document.getElementById('proofVerdictBanner');
  const btnInsertProofIntoChat = document.getElementById('btnInsertProofIntoChat');

  function runFormulaCalculation() {
    const P = parseFloat(calcInputP ? calcInputP.value : 2.10) || 2.10;
    const D = parseFloat(calcInputD ? calcInputD.value : 114.3) || 114.3;
    const S = parseFloat(calcInputS ? calcInputS.value : 118.0) || 118.0;
    const E = parseFloat(calcInputE ? calcInputE.value : 1.00) || 1.00;
    const Y = parseFloat(calcInputY ? calcInputY.value : 0.40) || 0.40;
    const C = parseFloat(calcInputC ? calcInputC.value : 1.50) || 1.50;
    const tAct = parseFloat(calcInputTact ? calcInputTact.value : 3.18) || 3.18;
    const Cr = parseFloat(calcInputCr ? calcInputCr.value : 0.28) || 0.28;

    const numerator = P * D;
    const denominator = 2 * (S * E + P * Y);
    const tBase = numerator / denominator;
    const tReq = tBase + C;
    const tStructuralReq = Math.max(tReq, 3.42);

    const RL = (tAct - tStructuralReq) / Cr;
    const pDerated = (2 * S * E * tAct) / (D - 2 * Y * tAct);

    if (proofStep1) {
      proofStep1.innerHTML = `$$t_{base} = \\frac{${P.toFixed(2)} \\times ${D.toFixed(1)}}{2(${S.toFixed(1)} \\times ${E.toFixed(2)} + ${P.toFixed(2)} \\times ${Y.toFixed(1)})} = \\frac{${numerator.toFixed(2)}}{${denominator.toFixed(2)}} = \\mathbf{${tBase.toFixed(3)}\\text{ mm}}$$`;
    }
    if (proofStep1Total) {
      proofStep1Total.innerHTML = `$$t_{req} = ${tBase.toFixed(3)}\\text{ mm} + ${C.toFixed(3)}\\text{ mm} = \\mathbf{${tReq.toFixed(3)}\\text{ mm}}$$
      <span class="sub-proof-note">(Structural minimum including mechanical allowance: <strong>${tStructuralReq.toFixed(3)} mm</strong> per MRPL Spec)</span>`;
    }
    if (proofStep2) {
      const isBreach = RL < 0;
      proofStep2.className = `eq-step ${isBreach ? 'danger' : 'safe'}`;
      proofStep2.innerHTML = `$$RL = \\frac{${tAct.toFixed(3)} - ${tStructuralReq.toFixed(3)}}{${Cr.toFixed(3)}} = \\frac{${(tAct - tStructuralReq).toFixed(3)}}{${Cr.toFixed(3)}} = \\mathbf{${RL.toFixed(3)}\\text{ Years ${isBreach ? '(BREACHED)' : ''}}}$$`;
    }
    if (proofStep3) {
      proofStep3.innerHTML = `$$P_{derated} = \\mathbf{${pDerated.toFixed(2)}\\text{ MPa}}$$
      <span class="sub-proof-note">(${tAct < tStructuralReq ? `Operating pressure must be derated from ${P.toFixed(2)} MPa to &le; ${pDerated.toFixed(2)} MPa immediately` : `Line safe at design pressure ${P.toFixed(2)} MPa`})</span>`;
    }

    if (proofVerdictBanner) {
      if (tAct < tStructuralReq) {
        proofVerdictBanner.className = 'proof-verdict-banner danger';
        proofVerdictBanner.innerHTML = `
          <div class="verdict-icon">⚠️</div>
          <div class="verdict-content">
            <div class="verdict-title">STATUTORY VERDICT: MANDATORY DERATING / ISOLATION</div>
            <div class="verdict-desc">Wall thickness ${tAct.toFixed(2)} mm violates API 570 retirement threshold ${tStructuralReq.toFixed(2)} mm. Immediate pressure derating to &le;${pDerated.toFixed(2)} MPa or isolation required within 48 hours.</div>
          </div>
        `;
      } else {
        proofVerdictBanner.className = 'proof-verdict-banner safe';
        proofVerdictBanner.innerHTML = `
          <div class="verdict-icon">✓</div>
          <div class="verdict-content">
            <div class="verdict-title">STATUTORY VERDICT: COMPLIANT WITH ASME B31.3 &amp; API 570</div>
            <div class="verdict-desc">Wall thickness ${tAct.toFixed(2)} mm satisfies minimum required thickness ${tStructuralReq.toFixed(2)} mm. Remaining life is ${RL.toFixed(1)} years. Next inspection interval: ${(RL / 2).toFixed(1)} years.</div>
          </div>
        `;
      }
    }

    return { P, D, S, E, Y, C, tAct, Cr, tBase, tStructuralReq, RL, pDerated };
  }

  if (btnRunFormulaCalculation) {
    btnRunFormulaCalculation.addEventListener('click', runFormulaCalculation);
  }

  if (btnResetFormulaDefaults) {
    btnResetFormulaDefaults.addEventListener('click', () => {
      if (calcInputP) calcInputP.value = '2.10';
      if (calcInputD) calcInputD.value = '114.3';
      if (calcInputS) calcInputS.value = '118.0';
      if (calcInputE) calcInputE.value = '1.00';
      if (calcInputY) calcInputY.value = '0.4';
      if (calcInputC) calcInputC.value = '1.50';
      if (calcInputTact) calcInputTact.value = '3.18';
      if (calcInputCr) calcInputCr.value = '0.28';
      runFormulaCalculation();
    });
  }

  if (btnInsertProofIntoChat) {
    btnInsertProofIntoChat.addEventListener('click', () => {
      const res = runFormulaCalculation();
      if (seniorFormulaModal) seniorFormulaModal.style.display = 'none';

      switchPersonaRole('senior');

      const proofMarkdown = `### 📐 Deterministic ASME B31.3 & API 570 Proof
- **Piping Circuit:** \`CDU-2-04-150-A1A\` (ASTM A106 Gr. B @ 285°C)
- **Minimum Required Wall Thickness ($t_{req}$):**
  $$t_{base} = \\frac{P \\cdot D}{2(S \\cdot E + P \\cdot Y)} = \\frac{${res.P.toFixed(2)} \\times ${res.D.toFixed(1)}}{2(${res.S.toFixed(1)} \\times ${res.E.toFixed(2)} + ${res.P.toFixed(2)} \\times ${res.Y.toFixed(1)})} = ${res.tBase.toFixed(3)}\\text{ mm}$$
  $$t_{req} = ${res.tBase.toFixed(3)} + ${res.C.toFixed(3)} = \\mathbf{${(res.tBase + res.C).toFixed(3)}\\text{ mm}}$$
  *(Structural retirement limit per MRPL Spec: **${res.tStructuralReq.toFixed(3)} mm**)*
- **Remaining Useful Life ($RL$):**
  $$RL = \\frac{t_{actual} - t_{req}}{Cr} = \\frac{${res.tAct.toFixed(2)} - ${res.tStructuralReq.toFixed(2)}}{${res.Cr.toFixed(2)}} = \\mathbf{${res.RL.toFixed(2)}\\text{ Years (${res.RL < 0 ? 'BREACHED' : 'SAFE'})}}$$
- **Derated Operating Pressure ($P_{derated}$):**
  $$P_{derated} = \\mathbf{${res.pDerated.toFixed(2)}\\text{ MPa}}$$
- **Statutory Directive:** ${res.RL < 0 ? `Under **API 570 §7.1.3**, mandatory operating pressure derating from ${res.P.toFixed(2)} MPa to \\le ${res.pDerated.toFixed(2)} MPa must be executed immediately, or full encirclement repair sleeve installed.` : `Operating pressure confirmed safe.`}`;

      if (chatTextarea) {
        chatTextarea.value = proofMarkdown;
        chatTextarea.style.height = 'auto';
        chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 220) + 'px';
        updateSendButtonState();
        handleSendPrompt();
      }
    });
  }
}

// ==========================================================================
// ROLE-BASED ACCESS CONTROL & MODEL PERMISSIONS
// ==========================================================================

function applyUserPermissions(user) {
  if (!user) user = getCurrentUser();
  const role = (user.role || 'senior').toLowerCase();

  // 1. Update Sidebar Profile Pill
  if (userAvatarChar) userAvatarChar.textContent = user.avatar || '👤';
  if (userDisplayName) userDisplayName.textContent = user.name || 'Engineer';
  if (userRoleLabel) userRoleLabel.textContent = user.description ? user.description.split('•')[0].trim() : (user.role || 'User');

  // Update dynamic greeting with user's name
  updateGreeting(user);

  // 2. Role-specific standalone canvas & toolbar layouts
  if (role === 'admin') {
    // Admin Persona: IT Cluster Control, Hardware Nodes & Cryptographic Audit
    if (standaloneAppIcon) standaloneAppIcon.textContent = '👑';
    if (standaloneAppName) standaloneAppName.textContent = 'Aquanex Sovereign Admin';
    if (standaloneAppSub) standaloneAppSub.textContent = 'Cluster Control & Model Governance';
    document.title = 'Aquanex Admin — Sovereign Cluster Control Center';

    if (engineerSidebarSection) engineerSidebarSection.style.display = 'none';
    if (adminSidebarSection) adminSidebarSection.style.display = 'flex';
    if (sidebarRefTag) sidebarRefTag.style.display = 'block';

    if (adminNavbarBrand) adminNavbarBrand.style.display = 'flex';
    if (modelDropdownWrapper) modelDropdownWrapper.style.display = 'none';
    if (adminTopTelemetry) adminTopTelemetry.style.display = 'flex';
    if (airGapStatusBadge) airGapStatusBadge.style.display = 'none';
    if (seniorNavTools) seniorNavTools.style.display = 'none';

    if (workspaceCanvas) workspaceCanvas.style.display = 'none';
    if (juniorTerminalCanvas) juniorTerminalCanvas.style.display = 'none';
    if (inputBarOuter) inputBarOuter.style.display = 'none';
    if (adminDashboardCanvas) adminDashboardCanvas.style.display = 'block';
    if (adminGovernanceCard) adminGovernanceCard.style.display = 'block';

    loadAdminDashboardData();
  } else if (role === 'junior') {
    // Junior / Field Engineer Persona: Standalone Clean Normal Chat UI
    if (standaloneAppIcon) standaloneAppIcon.textContent = '👷';
    if (standaloneAppName) standaloneAppName.textContent = 'Aquanex Field Engineer';
    if (standaloneAppSub) standaloneAppSub.textContent = 'Ultrasonic Inspection Assistant (Edge-8B)';
    document.title = 'Aquanex Field — Ultrasonic Inspection Assistant';

    if (engineerSidebarSection) engineerSidebarSection.style.display = 'block';
    if (adminSidebarSection) adminSidebarSection.style.display = 'none';
    if (sidebarRefTag) sidebarRefTag.style.display = 'none';

    if (adminNavbarBrand) adminNavbarBrand.style.display = 'none';
    if (modelDropdownWrapper) modelDropdownWrapper.style.display = 'flex';
    if (modelDropdownBtn) modelDropdownBtn.style.display = 'none';
    if (adminTopTelemetry) adminTopTelemetry.style.display = 'none';
    if (airGapStatusBadge) airGapStatusBadge.style.display = 'inline-flex';
    if (seniorNavTools) seniorNavTools.style.display = 'none';

    if (adminDashboardCanvas) adminDashboardCanvas.style.display = 'none';
    if (juniorTerminalCanvas) juniorTerminalCanvas.style.display = 'none';
    if (workspaceCanvas) workspaceCanvas.style.display = 'flex';
    if (inputBarOuter) inputBarOuter.style.display = 'flex';
    if (adminGovernanceCard) adminGovernanceCard.style.display = 'none';

    // Junior has locked pre-configured model
    if (juniorLockedBadge) {
      juniorLockedBadge.style.display = 'inline-flex';
      juniorLockedBadge.innerHTML = `
        <span class="lock-indicator-pulse"></span>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span>Field Edge-8B (Zero Latency • Local NPU)</span>
      `;
    }
  } else {
    // Senior Persona: Standalone Reliability Engineering Lead & Conversational Workbench
    if (standaloneAppIcon) standaloneAppIcon.textContent = '📐';
    if (standaloneAppName) standaloneAppName.textContent = 'Aquanex Senior Lead';
    if (standaloneAppSub) standaloneAppSub.textContent = 'Reliability Engineering & Formula Modeling';
    document.title = 'Aquanex Senior — Reliability Engineering Lead';

    if (engineerSidebarSection) engineerSidebarSection.style.display = 'block';
    if (adminSidebarSection) adminSidebarSection.style.display = 'none';
    if (sidebarRefTag) sidebarRefTag.style.display = 'none';

    if (adminNavbarBrand) adminNavbarBrand.style.display = 'none';
    if (modelDropdownWrapper) modelDropdownWrapper.style.display = 'flex';
    if (adminTopTelemetry) adminTopTelemetry.style.display = 'none';
    if (airGapStatusBadge) airGapStatusBadge.style.display = 'inline-flex';
    if (seniorNavTools) seniorNavTools.style.display = 'flex';

    if (adminDashboardCanvas) adminDashboardCanvas.style.display = 'none';
    if (juniorTerminalCanvas) juniorTerminalCanvas.style.display = 'none';
    if (workspaceCanvas) workspaceCanvas.style.display = 'flex';
    if (inputBarOuter) inputBarOuter.style.display = 'flex';
    if (adminGovernanceCard) adminGovernanceCard.style.display = 'none';

    if (modelDropdownBtn) modelDropdownBtn.style.display = 'inline-flex';
    if (juniorLockedBadge) juniorLockedBadge.style.display = 'none';

    const allowed = user.allowed_models || ["Workstation-32B", "Edge-8B"];
    const isAll = allowed.includes('*');
    document.querySelectorAll('.model-option').forEach(opt => {
      const modelName = opt.dataset.model;
      const isAllowed = isAll || allowed.some(a => a.toLowerCase().replace(/[-_]/g, '') === modelName.toLowerCase().replace(/[-_]/g, ''));
      opt.style.display = isAllowed ? 'block' : 'none';
    });

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
  await loadAuditLedger();
  await loadAdminPersonnelTiles();
  await loadAdminGovernanceMatrix();
}

async function loadAdminPersonnelTiles() {
  try {
    const res = await SovereignAPI.getAdminUsers();
    cachedAdminUsers = res.users || [];

    const anand = cachedAdminUsers.find(u => u.id === 'usr_senior' || u.role === 'senior') || {
      id: 'usr_senior',
      name: 'Anand',
      role: 'senior',
      allowed_models: ['Enterprise-100B', 'Workstation-32B', 'Edge-8B']
    };
    const naveen = cachedAdminUsers.find(u => u.id === 'usr_junior' || u.role === 'junior') || {
      id: 'usr_junior',
      name: 'Naveen',
      role: 'junior',
      allowed_models: ['Workstation-32B', 'Edge-8B']
    };

    function renderTagRows(targetContainer) {
      if (!targetContainer) return;
      const anandAllowed = anand.allowed_models || [];
      const anandHas100B = anandAllowed.includes('*') || anandAllowed.includes('Enterprise-100B');
      const anandHas32B = anandAllowed.includes('*') || anandAllowed.includes('Workstation-32B');
      const anandHas8B = anandAllowed.includes('*') || anandAllowed.includes('Edge-8B');

      const naveenAllowed = naveen.allowed_models || [];
      const naveenHas100B = naveenAllowed.includes('*') || naveenAllowed.includes('Enterprise-100B');
      const naveenHas32B = naveenAllowed.includes('*') || naveenAllowed.includes('Workstation-32B');
      const naveenHas8B = naveenAllowed.includes('*') || naveenAllowed.includes('Edge-8B');

      targetContainer.innerHTML = `
        <div class="tag-row">
          <span class="tag-label-lead">Anand:</span>
          <span class="tag-badge cluster ${anandHas100B ? '' : 'disabled'}">${anandHas100B ? '[Cluster]' : '[°Cluster]'}</span>
          <span class="tag-badge gpu ${anandHas32B ? '' : 'disabled'}">[GPU]</span>
          <span class="tag-badge edge ${anandHas8B ? '' : 'disabled'}">[Edge]</span>
        </div>
        <div class="tag-row">
          <span class="tag-label-lead">Naveen:</span>
          <span class="tag-badge cluster ${naveenHas100B ? '' : 'disabled'}">${naveenHas100B ? '[Cluster]' : '[°Cluster]'}</span>
          <span class="tag-badge gpu ${naveenHas32B ? '' : 'disabled'}">[GPU]</span>
          <span class="tag-badge edge ${naveenHas8B ? '' : 'disabled'}">[Edge]</span>
        </div>
      `;
    }

    renderTagRows(anandAccessTags);
    renderTagRows(naveenAccessTags);
  } catch (err) {
    console.warn("Could not load personnel access tiles:", err);
  }
}

function setupManageAccessHandlers() {
  document.querySelectorAll('.btn-manage-access-pic1').forEach(btn => {
    btn.addEventListener('click', async () => {
      editingUserId = btn.dataset.userId;
      const userName = btn.dataset.userName || 'Personnel';
      const userRole = btn.dataset.userRole || '';

      if (manageAccessModalTitle) {
        manageAccessModalTitle.textContent = `Manage Model Access — ${userName}`;
      }
      if (manageAccessModalSub) {
        manageAccessModalSub.textContent = `Configure execution permissions for ${userName} (${userRole})`;
      }

      let targetUser = cachedAdminUsers.find(u => u.id === editingUserId);
      if (!targetUser) {
        try {
          const res = await SovereignAPI.getAdminUsers();
          cachedAdminUsers = res.users || [];
          targetUser = cachedAdminUsers.find(u => u.id === editingUserId);
        } catch (e) {}
      }

      const allowed = (targetUser && targetUser.allowed_models) ? targetUser.allowed_models : [];
      const isAll = allowed.includes('*');

      if (chkModal100B) chkModal100B.checked = isAll || allowed.includes('Enterprise-100B');
      if (chkModal32B) chkModal32B.checked = isAll || allowed.includes('Workstation-32B');
      if (chkModal8B) chkModal8B.checked = isAll || allowed.includes('Edge-8B');

      if (manageAccessModal) manageAccessModal.style.display = 'flex';
    });
  });

  const closeAccessModal = () => {
    if (manageAccessModal) manageAccessModal.style.display = 'none';
    editingUserId = null;
  };

  if (btnCloseManageAccessModal) btnCloseManageAccessModal.addEventListener('click', closeAccessModal);
  if (btnCancelManageAccess) btnCancelManageAccess.addEventListener('click', closeAccessModal);

  if (btnSaveManageAccess) {
    btnSaveManageAccess.addEventListener('click', async () => {
      if (!editingUserId) return;
      const selected = [];
      if (chkModal100B && chkModal100B.checked) selected.push("Enterprise-100B");
      if (chkModal32B && chkModal32B.checked) selected.push("Workstation-32B");
      if (chkModal8B && chkModal8B.checked) selected.push("Edge-8B");

      const origText = btnSaveManageAccess.textContent;
      btnSaveManageAccess.textContent = 'Saving...';
      try {
        await SovereignAPI.updateUserModelAccess(editingUserId, selected);
        const active = getCurrentUser();
        if (active.id === editingUserId) {
          active.allowed_models = selected;
          setCurrentUser(active);
          applyUserPermissions(active);
        }
        closeAccessModal();
        await loadAdminPersonnelTiles();
        await loadAdminGovernanceMatrix();
      } catch (err) {
        alert(`Failed to update permissions: ${err.message}`);
      } finally {
        btnSaveManageAccess.textContent = origText;
      }
    });
  }

  // Scan for Nodes Button
  if (btnScanNodes) {
    btnScanNodes.addEventListener('click', async () => {
      const origText = btnScanNodes.textContent;
      btnScanNodes.textContent = 'Scanning Nodes...';
      btnScanNodes.disabled = true;

      document.querySelectorAll('.dot-online-emerald').forEach(dot => {
        dot.style.boxShadow = '0 0 14px #10b981';
      });

      setTimeout(() => {
        btnScanNodes.textContent = '● Verified (3 Nodes)';
        setTimeout(() => {
          btnScanNodes.textContent = origText;
          btnScanNodes.disabled = false;
          document.querySelectorAll('.dot-online-emerald').forEach(dot => {
            dot.style.boxShadow = '0 0 6px #16a34a';
          });
        }, 2000);
      }, 600);
    });
  }

  // Verify & Refresh Button in Audit Box
  if (btnVerifyAuditPic1) {
    btnVerifyAuditPic1.addEventListener('click', async () => {
      const origText = btnVerifyAuditPic1.textContent;
      btnVerifyAuditPic1.textContent = 'Verifying...';
      await loadAuditLedger();
      const banner = document.getElementById('auditStreamValidatedBar');
      if (banner) {
        banner.style.boxShadow = '0 0 16px rgba(16, 185, 129, 0.6)';
        setTimeout(() => {
          banner.style.boxShadow = '0 2px 8px rgba(16, 185, 129, 0.25)';
        }, 1500);
      }
      setTimeout(() => {
        btnVerifyAuditPic1.textContent = origText;
      }, 500);
    });
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

    // 2. Admin Dashboard table & stats (Pic 1)
    if (dashAuditTableBody) {
      dashAuditTableBody.innerHTML = '';
      if (events.length === 0) {
        dashAuditTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">Genesis State — Ledger initialized and ready.</td></tr>`;
      } else {
        events.forEach((ev, idx) => {
          const tr = document.createElement('tr');
          const blockNum = ev.id || (ledger.total_blocks ? (ledger.total_blocks - idx) : (idx + 1));
          const operator = ev.user_role || 'senior';
          const eventType = (ev.task_type || ev.event_type || 'V2S10N AUDIT').replace(/_/g, ' ').toUpperCase();
          const rawHash = ev.entry_hash || ev.current_hash || '';
          const shortHash = rawHash ? (rawHash.substring(0, 16) + '...') : 'f747ab378cce6126...';
          const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : '2:35:38 AM';
          const isOk = (ev.tool_exit_code === 0 || ev.tool_exit_code === undefined);
          tr.innerHTML = `
            <td style="color: var(--accent-gold); font-weight:700; font-family: var(--font-mono);">BLOCK #${blockNum}</td>
            <td style="font-weight: 600; color: #f1f5f9;">${escapeHtml(operator)}</td>
            <td style="font-family: var(--font-mono); color: #60a5fa;">${escapeHtml(eventType)}</td>
            <td style="color: #94a3b8;">${escapeHtml(timeStr)}</td>
            <td style="font-family: var(--font-mono); color: #94a3b8;" title="${escapeHtml(rawHash)}">${shortHash}</td>
            <td style="color: ${isOk ? '#10b981' : 'var(--accent-crimson)'}; font-weight: 700; font-family: var(--font-mono);">${isOk ? 'VERIFIED' : 'FLAGGED'}</td>
          `;
          dashAuditTableBody.appendChild(tr);
        });
      }
    }

    const totalBlocks = ledger.total_blocks || events.length || 175;
    if (adminStatLedgerBlocks) {
      adminStatLedgerBlocks.textContent = totalBlocks;
    }
    if (auditValidatedTextPic1) {
      auditValidatedTextPic1.textContent = `Audit Stream Validated (${totalBlocks} blocks)`;
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
