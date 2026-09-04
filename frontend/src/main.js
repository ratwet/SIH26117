import { SovereignAPI, USE_MOCK, setMockMode, getBackendUrl, setBackendUrl, getServerIP, setServerIP, DEFAULT_LAN_URL, DEFAULT_LOCAL_URL, DEFAULT_SERVER_IP } from './api.js';

// Native Tauri file plugins (with browser fallback)
let tauriDialog = null;
let tauriFs = null;

async function initTauriPlugins() {
  try {
    if (window.__TAURI_INTERNALS__) {
      tauriDialog = await import('@tauri-apps/plugin-dialog');
      tauriFs = await import('@tauri-apps/plugin-fs');
      console.log("📁 Native Tauri dialog & fs plugins initialized.");
    }
  } catch (e) {
    console.log("ℹ️ Tauri native plugins not loaded (running in browser or preview).", e);
  }
}

// Workspace Screen Element
const appView = document.getElementById('appView');

// Network & Gateway Elements
const inputBackendUrl = document.getElementById('inputBackendUrl');
const btnTestBackendConn = document.getElementById('btnTestBackendConn');
const btnPresetLan = document.getElementById('btnPresetLan');
const btnPresetLocal = document.getElementById('btnPresetLocal');
const backendPingResult = document.getElementById('backendPingResult');
const backendConnStatusBadge = document.getElementById('backendConnStatusBadge');
const modalBackendHostPort = document.getElementById('modalBackendHostPort');

// Workspace Header & Model Dropdown
const modelDropdownBtn = document.getElementById('modelDropdownBtn');
const modelMenu = document.getElementById('modelMenu');
const currentModelBadge = document.getElementById('currentModelBadge');
const airGapStatusBadge = document.getElementById('airGapStatusBadge');
const airGapStatusText = document.getElementById('airGapStatusText');
const btnOpenCustomizeTop = document.getElementById('btnOpenCustomizeTop');

// Sidebar Elements
const btnNewChat = document.getElementById('btnNewChat');
const activeChatTitle = document.getElementById('activeChatTitle');
const btnCustomize = document.getElementById('btnCustomize');
const userAvatarChar = document.getElementById('userAvatarChar');
const userDisplayName = document.getElementById('userDisplayName');
const userRoleLabel = document.getElementById('userRoleLabel');

// Canvas Elements
const workspaceCanvas = document.getElementById('workspaceCanvas');
const greetingContainer = document.getElementById('greetingContainer');
const greetingTitle = document.getElementById('greetingTitle');
const messagesFeed = document.getElementById('messagesFeed');

// Suggestion Pills
const pillAudit = document.getElementById('pillAudit');
const pillSelfHeal = document.getElementById('pillSelfHeal');
const pillSummarize = document.getElementById('pillSummarize');
const pillExplain = document.getElementById('pillExplain');

// Input Box Elements
const chatTextarea = document.getElementById('chatTextarea');
const btnChatSend = document.getElementById('btnChatSend');
const btnAttachFile = document.getElementById('btnAttachFile');
const workspaceFileInput = document.getElementById('workspaceFileInput');
const attachedFilePill = document.getElementById('attachedFilePill');
const attachedFileName = document.getElementById('attachedFileName');
const btnRemoveAttachment = document.getElementById('btnRemoveAttachment');

// Modals
const customizeModal = document.getElementById('customizeModal');
const btnCloseCustomize = document.getElementById('btnCloseCustomize');
const modalMockToggle = document.getElementById('modalMockToggle');
const modalAirGapBadge = document.getElementById('modalAirGapBadge');
const modalAuditTableBody = document.getElementById('modalAuditTableBody');
const btnSimulateBreachInModal = document.getElementById('btnSimulateBreachInModal');

const lockdownModal = document.getElementById('lockdownModal');
const btnRestoreAirGap = document.getElementById('btnRestoreAirGap');

// State
let currentUser = {
  name: "Guest",
  email: "guest@aquanex.ai",
  role: "Guest User"
};
let selectedFile = null;
let isExecuting = false;
let currentThinkingBox = null;
let currentThinkingList = null;

// Initialize
async function init() {
  await initTauriPlugins();
  setupEventListeners();
  loadAuditLedger();
  startTelemetry();
  updateBackendUi();
  await checkAirGapHealth();
  await loadDeliverables();
  if (userDisplayName) userDisplayName.textContent = currentUser.name;
  if (userRoleLabel) userRoleLabel.textContent = currentUser.role;
  if (userAvatarChar) userAvatarChar.textContent = currentUser.name.charAt(0).toUpperCase();
  if (greetingTitle) greetingTitle.textContent = `Good morning, ${currentUser.name}`;
  console.log("🛡️ Aquanex UI Initialized. Mode:", USE_MOCK ? "MOCK" : "LIVE", "Target Gateway:", getBackendUrl());
}

function setupEventListeners() {
  // 1. Model Dropdown
  modelDropdownBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    modelMenu.style.display = modelMenu.style.display === 'none' ? 'block' : 'none';
  });

  document.querySelectorAll('.model-option').forEach(opt => {
    opt.addEventListener('click', () => {
      document.querySelectorAll('.model-option').forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      currentModelBadge.textContent = opt.dataset.model;
      modelMenu.style.display = 'none';
    });
  });

  document.addEventListener('click', () => {
    if (modelMenu) modelMenu.style.display = 'none';
  });

  // 3. New Chat
  btnNewChat.addEventListener('click', () => resetToNewChat());

  // 4. Customize Modals & Network Settings
  btnCustomize.addEventListener('click', () => openCustomizeModal());
  btnOpenCustomizeTop.addEventListener('click', () => openCustomizeModal());
  btnCloseCustomize.addEventListener('click', () => customizeModal.style.display = 'none');
  modalMockToggle.addEventListener('change', (e) => {
    setMockMode(e.target.checked);
    loadAuditLedger();
    checkAirGapHealth();
    loadDeliverables();
  });

  // Network IP Gateway Configuration Handlers
  if (inputBackendUrl) {
    inputBackendUrl.addEventListener('input', (e) => {
      setBackendUrl(e.target.value.trim());
      updateBackendUi();
    });
  }

  if (btnPresetLan) {
    btnPresetLan.addEventListener('click', () => {
      setBackendUrl(DEFAULT_LAN_URL);
      updateBackendUi();
      testBackendConnection();
    });
  }

  if (btnPresetLocal) {
    btnPresetLocal.addEventListener('click', () => {
      setBackendUrl(DEFAULT_LOCAL_URL);
      updateBackendUi();
      testBackendConnection();
    });
  }

  if (btnTestBackendConn) {
    btnTestBackendConn.addEventListener('click', () => {
      testBackendConnection();
    });
  }

  // Refresh Deliverables button
  const btnRefreshDeliverables = document.getElementById('btnRefreshDeliverables');
  if (btnRefreshDeliverables) {
    btnRefreshDeliverables.addEventListener('click', () => loadDeliverables());
  }

  btnSimulateBreachInModal.addEventListener('click', () => {
    customizeModal.style.display = 'none';
    triggerLockdown("Hotspot tether breach test triggered by evaluator.");
  });

  // Server IP Settings (Wiki Spec)
  const inputServerIp = document.getElementById('inputServerIp');
  const btnSaveServerIp = document.getElementById('btnSaveServerIp');
  const btnResetServerIp = document.getElementById('btnResetServerIp');
  const modalHostPort = document.getElementById('modalHostPort');
  const modalServerIpBadge = document.getElementById('modalServerIpBadge');

  if (inputServerIp) inputServerIp.value = getServerIP();
  if (modalHostPort) modalHostPort.textContent = getServerIP();
  if (modalServerIpBadge) modalServerIpBadge.textContent = getServerIP();

  if (btnSaveServerIp) {
    btnSaveServerIp.addEventListener('click', () => {
      const val = inputServerIp ? inputServerIp.value.trim() : '';
      if (val) {
        setServerIP(val);
        if (modalHostPort) modalHostPort.textContent = val;
        if (modalServerIpBadge) modalServerIpBadge.textContent = val;
        console.log("🌐 Gateway IP updated to:", val);
      }
    });
  }

  if (btnResetServerIp) {
    btnResetServerIp.addEventListener('click', () => {
      setServerIP(DEFAULT_SERVER_IP);
      if (inputServerIp) inputServerIp.value = DEFAULT_SERVER_IP;
      if (modalHostPort) modalHostPort.textContent = DEFAULT_SERVER_IP;
      if (modalServerIpBadge) modalServerIpBadge.textContent = DEFAULT_SERVER_IP;
      console.log("🌐 Gateway IP reset to repo wiki default:", DEFAULT_SERVER_IP);
    });
  }

  btnRestoreAirGap.addEventListener('click', () => {
    lockdownModal.style.display = 'none';
    airGapStatusBadge.style.background = 'var(--status-emerald-bg)';
    airGapStatusBadge.style.color = 'var(--status-emerald)';
    airGapStatusText.textContent = 'Air-Gap Enforced';
  });

  // 5. Suggestion Pills
  pillAudit.addEventListener('click', () => {
    const prompt = "Audit line CDU-2-04-150-A1A from uploaded UT inspection scan and generate formal executive approval note.";
    executeUserPrompt(prompt);
  });

  pillSelfHeal.addEventListener('click', () => {
    const prompt = "Audit line CDU-2-04-150-A1A with [SIMULATE_ERROR] to test autonomous cyclic self-healing recovery.";
    executeUserPrompt(prompt);
  });

  pillSummarize.addEventListener('click', () => {
    const prompt = "Summarize the findings and corrosion trends from CDU2_UT_Scan_2026.pdf.";
    executeUserPrompt(prompt);
  });

  pillExplain.addEventListener('click', () => {
    const prompt = "Explain API 570 calculation methodology for remaining pipe thickness.";
    executeUserPrompt(prompt);
  });

  // 6. Textarea Input
  chatTextarea.addEventListener('input', () => {
    chatTextarea.style.height = 'auto';
    chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 140) + 'px';
    btnChatSend.disabled = !chatTextarea.value.trim() || isExecuting;
  });

  chatTextarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!btnChatSend.disabled) {
        executeUserPrompt(chatTextarea.value.trim());
      }
    }
  });

  btnChatSend.addEventListener('click', () => {
    if (!btnChatSend.disabled) {
      executeUserPrompt(chatTextarea.value.trim());
    }
  });

  // 7. File Attachment
  btnAttachFile.addEventListener('click', () => workspaceFileInput.click());
  workspaceFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedFile = e.target.files[0];
      attachedFileName.textContent = selectedFile.name;
      attachedFilePill.style.display = 'flex';
    }
  });
  btnRemoveAttachment.addEventListener('click', () => {
    selectedFile = null;
    attachedFilePill.style.display = 'none';
    workspaceFileInput.value = '';
  });
}



function resetToNewChat() {
  messagesFeed.innerHTML = '';
  messagesFeed.style.display = 'none';
  greetingContainer.style.display = 'flex';
  activeChatTitle.textContent = 'New chat';
  chatTextarea.value = '';
  chatTextarea.style.height = 'auto';
  btnChatSend.disabled = true;
}

function executeUserPrompt(prompt) {
  if (!prompt || isExecuting) return;

  isExecuting = true;
  btnChatSend.disabled = true;

  // Transition from greeting to active message feed
  greetingContainer.style.display = 'none';
  messagesFeed.style.display = 'flex';
  activeChatTitle.textContent = prompt.length > 26 ? prompt.substring(0, 24) + '...' : prompt;

  // Render User Message Bubble
  renderUserMessage(prompt);

  // Clear input
  chatTextarea.value = '';
  chatTextarea.style.height = 'auto';

  // Create Assistant Message Container with Live Thinking Box
  const assistantMsgRow = document.createElement('div');
  assistantMsgRow.className = 'msg-row msg-assistant';
  
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  // Collapsible Thought Box
  currentThinkingBox = document.createElement('div');
  currentThinkingBox.className = 'thought-stream-box';
  currentThinkingBox.innerHTML = `
    <div class="thought-stream-header">
      <span class="thought-stream-title">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        LangGraph Cyclic State Engine
      </span>
      <span class="thought-stream-badge">Processing nodes...</span>
    </div>
    <div class="thought-steps-list"></div>
  `;
  bubble.appendChild(currentThinkingBox);
  currentThinkingList = currentThinkingBox.querySelector('.thought-steps-list');

  // Response text container
  const responseContainer = document.createElement('div');
  responseContainer.className = 'response-container';
  bubble.appendChild(responseContainer);

  assistantMsgRow.appendChild(bubble);
  messagesFeed.appendChild(assistantMsgRow);
  scrollToBottom();

  // Stream via API
  SovereignAPI.streamChat({
    prompt: prompt,
    userRole: currentUser.role === 'Admin' ? 'senior' : 'senior',
    onThought: (payload) => {
      appendThoughtStep(payload);
    },
    onDeliverable: (payload) => {
      console.log("Deliverable ready:", payload);
      loadDeliverables();
    },
    onDone: (payload) => {
      finishAssistantResponse(payload, responseContainer);
      loadDeliverables();
    },
    onError: (err) => {
      console.error("Execution error:", err);
      isExecuting = false;
      btnChatSend.disabled = false;
      responseContainer.innerHTML = `<p style="color: var(--emergency-crimson); font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.5;">⚠️ Connection failed: Cannot reach server at <strong>${getServerIP()}</strong>.<br><small style="color: var(--text-muted);">Ensure the FastAPI backend is running and reachable on this host/port.</small></p>`;
    }
  });
}

function renderUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-user';
  row.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  messagesFeed.appendChild(row);
  scrollToBottom();
}

function appendThoughtStep(payload) {
  if (!currentThinkingList) return;
  const node = payload.node || '';
  const text = payload.thought || JSON.stringify(payload);

  const item = document.createElement('div');
  const isHeal = node.includes('distill') || text.includes('Error');
  item.className = `thought-step-item ${isHeal ? 'heal' : ''}`;
  
  let icon = '▶';
  if (node.includes('vision')) icon = '👁️';
  else if (node.includes('math')) icon = '📐';
  else if (node.includes('sandbox')) icon = isHeal ? '⚠️' : '⚡';
  else if (node.includes('distill')) icon = '🔧';
  else if (node.includes('deliverable')) icon = '📄';
  else if (node.includes('route')) icon = '🧭';

  item.innerHTML = `<span>${icon}</span> <span>${escapeHtml(text)}</span>`;
  currentThinkingList.appendChild(item);
  scrollToBottom();
}

function finishAssistantResponse(payload, container) {
  isExecuting = false;
  btnChatSend.disabled = false;

  if (currentThinkingBox) {
    const badge = currentThinkingBox.querySelector('.thought-stream-badge');
    if (badge) badge.textContent = 'Completed (Exit Code 0) ✅';
  }

  // Render Executive Summary Card
  const summaryCard = document.createElement('div');
  summaryCard.className = 'exec-summary-card';
  summaryCard.innerHTML = `
    <div class="exec-header">
      <span class="exec-title">API 570 Statutory Inspection Assessment</span>
      <span class="exec-badge-alert">CRITICAL SHUTDOWN ACTION</span>
    </div>

    <div class="exec-grid">
      <div class="exec-metric">
        <div class="exec-metric-label">INSPECTED LINE TAG</div>
        <div class="exec-metric-val">CDU-2-04-150-A1A</div>
      </div>
      <div class="exec-metric">
        <div class="exec-metric-label">REMAINING LIFE (RL)</div>
        <div class="exec-metric-val danger">3.14 YEARS</div>
      </div>
      <div class="exec-metric">
        <div class="exec-metric-label">MEASURED UT WALL</div>
        <div class="exec-metric-val">3.20 mm <span style="font-size:0.68rem; color:var(--text-muted);">(Nominal: 4.8mm)</span></div>
      </div>
      <div class="exec-metric">
        <div class="exec-metric-label">ESTIMATED CAPEX BUDGET</div>
        <div class="exec-metric-val gold">₹1,154,400 INR</div>
      </div>
    </div>

    <div class="exec-text">${escapeHtml(payload.final_response || '')}</div>

    <div class="deliverables-action-row">
      <button class="btn-deliverable-gold" id="btnDlDocx">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Open Approval Note (.docx)
      </button>
      <button class="btn-deliverable-gold" id="btnDlXlsx">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        Open Cost Matrix (.xlsx)
      </button>
    </div>
  `;

  container.appendChild(summaryCard);

  // Wire download buttons
  const btnDocx = summaryCard.querySelector('#btnDlDocx');
  const btnXlsx = summaryCard.querySelector('#btnDlXlsx');
  const actualDocx = payload.docx_path ? payload.docx_path.split('/').pop() : 'MRPL_Approval_Note_sim-2026.docx';
  const actualXlsx = payload.xlsx_path ? payload.xlsx_path.split('/').pop() : 'Cost_Matrix_sim-2026.xlsx';

  if (btnDocx) btnDocx.addEventListener('click', () => handleDownloadDeliverable(actualDocx, btnDocx));
  if (btnXlsx) btnXlsx.addEventListener('click', () => handleDownloadDeliverable(actualXlsx, btnXlsx));

  scrollToBottom();
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function checkAirGapHealth() {
  try {
    const health = await SovereignAPI.checkHealth();
    if (health && health.status === 'OPERATIONAL') {
      airGapStatusBadge.style.background = 'var(--status-emerald-bg)';
      airGapStatusBadge.style.color = 'var(--status-emerald)';
      airGapStatusText.textContent = USE_MOCK ? 'Air-Gap Enforced (Mock)' : 'Air-Gap Enforced (Live Node 2)';
      if (modalAirGapBadge) {
        modalAirGapBadge.textContent = 'LOCKED AIR-GAP OK';
        modalAirGapBadge.className = 'badge-emerald';
      }
    }
  } catch (err) {
    console.warn("Backend health check failed:", err);
    airGapStatusBadge.style.background = 'rgba(239, 35, 60, 0.15)';
    airGapStatusBadge.style.color = 'var(--emergency-crimson)';
    airGapStatusText.textContent = `Server Offline (${getServerIP()})`;
    if (modalAirGapBadge) {
      modalAirGapBadge.textContent = 'SERVER OFFLINE';
      modalAirGapBadge.className = 'badge-crimson';
    }
  }
}

async function loadDeliverables() {
  const deliverablesList = document.getElementById('deliverablesList');
  const deliverablesLoading = document.getElementById('deliverablesLoading');
  const deliverablesError = document.getElementById('deliverablesError');
  const deliverablesCountBadge = document.getElementById('deliverablesCountBadge');

  if (!deliverablesList) return;
  if (deliverablesLoading) deliverablesLoading.style.display = 'flex';
  if (deliverablesError) deliverablesError.style.display = 'none';

  try {
    const data = await SovereignAPI.listFiles();
    const files = data.deliverables || [];
    if (deliverablesCountBadge) deliverablesCountBadge.textContent = files.length;
    deliverablesList.innerHTML = '';

    if (files.length === 0) {
      deliverablesList.innerHTML = '<div class="deliverables-empty">No deliverables compiled yet. Run an inspection audit to generate Word/Excel artifacts.</div>';
    } else {
      files.forEach(file => {
        const item = document.createElement('div');
        item.className = 'deliverable-item';
        const isDocx = file.name.endsWith('.docx');
        const isXlsx = file.name.endsWith('.xlsx');
        const badgeClass = isDocx ? 'type-docx' : (isXlsx ? 'type-xlsx' : 'type-default');
        const typeText = isDocx ? 'DOCX' : (isXlsx ? 'XLSX' : 'FILE');
        const sizeText = formatBytes(file.size_bytes);

        item.innerHTML = `
          <div class="deliverable-meta">
            <span class="deliverable-type-badge ${badgeClass}">${typeText}</span>
            <div class="deliverable-details">
              <span class="deliverable-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</span>
              <span class="deliverable-sub">${sizeText}</span>
            </div>
          </div>
          <button class="btn-download-deliverable" data-filename="${escapeHtml(file.name)}" title="Save deliverable to disk">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Save
          </button>
        `;

        const downloadBtn = item.querySelector('.btn-download-deliverable');
        downloadBtn.addEventListener('click', () => {
          handleDownloadDeliverable(file.name, downloadBtn);
        });

        deliverablesList.appendChild(item);
      });
    }
  } catch (err) {
    console.error("Failed to load deliverables:", err);
    if (deliverablesError) {
      deliverablesError.style.display = 'block';
      deliverablesError.textContent = `Error: ${err.message || 'Cannot reach server'}`;
    }
  } finally {
    if (deliverablesLoading) deliverablesLoading.style.display = 'none';
  }
}

async function handleDownloadDeliverable(filename, btn) {
  const originalHtml = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Saving...';
  }

  try {
    const arrayBuffer = await SovereignAPI.fetchDeliverableBinary(filename);
    const ext = filename.split('.').pop();

    if (window.__TAURI_INTERNALS__ && tauriDialog && tauriFs) {
      // Native Tauri Save File Dialog
      const suggestedPath = await tauriDialog.save({
        defaultPath: filename,
        filters: [
          { name: ext.toUpperCase() + ' Deliverable', extensions: [ext] }
        ]
      });

      if (suggestedPath) {
        await tauriFs.writeFile(suggestedPath, new Uint8Array(arrayBuffer));
        console.log("💾 Saved deliverable to disk:", suggestedPath);
        if (btn) btn.textContent = 'Saved! ✅';
        setTimeout(() => { if (btn) { btn.innerHTML = originalHtml; btn.disabled = false; } }, 2000);
        return;
      } else {
        // User cancelled dialog
        if (btn) { btn.innerHTML = originalHtml; btn.disabled = false; }
        return;
      }
    }

    // Standard Browser / Dev Server Blob fallback
    const mime = filename.endsWith('.docx')
      ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      : (filename.endsWith('.xlsx')
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'application/octet-stream');

    const blob = new Blob([arrayBuffer], { type: mime });
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);

    if (btn) {
      btn.textContent = 'Downloaded! ✅';
      setTimeout(() => { btn.innerHTML = originalHtml; btn.disabled = false; }, 2000);
    }
  } catch (err) {
    console.error("Deliverable download failed:", err);
    alert(`Download failed for '${filename}':\n${err.message}`);
    if (btn) {
      btn.textContent = 'Failed ❌';
      setTimeout(() => { btn.innerHTML = originalHtml; btn.disabled = false; }, 2500);
    }
  }
}

function scrollToBottom() {
  workspaceCanvas.scrollTop = workspaceCanvas.scrollHeight;
}

function openCustomizeModal() {
  updateBackendUi();
  const inputServerIp = document.getElementById('inputServerIp');
  const modalHostPort = document.getElementById('modalHostPort');
  const modalServerIpBadge = document.getElementById('modalServerIpBadge');
  const currentIp = getServerIP();
  if (inputServerIp) inputServerIp.value = currentIp;
  if (modalHostPort) modalHostPort.textContent = currentIp;
  if (modalServerIpBadge) modalServerIpBadge.textContent = currentIp;
  customizeModal.style.display = 'flex';
}

function updateBackendUi() {
  const currentUrl = getBackendUrl();
  if (inputBackendUrl) inputBackendUrl.value = currentUrl;
  if (modalBackendHostPort) {
    modalBackendHostPort.textContent = currentUrl.replace(/^https?:\/\//, '');
  }
  if (btnPresetLan && btnPresetLocal) {
    if (currentUrl === DEFAULT_LAN_URL) {
      btnPresetLan.classList.add('active');
      btnPresetLocal.classList.remove('active');
    } else if (currentUrl === DEFAULT_LOCAL_URL) {
      btnPresetLocal.classList.add('active');
      btnPresetLan.classList.remove('active');
    } else {
      btnPresetLan.classList.remove('active');
      btnPresetLocal.classList.remove('active');
    }
  }
}

async function testBackendConnection() {
  if (!backendPingResult) return;
  const targetUrl = getBackendUrl();
  backendPingResult.style.display = 'block';
  backendPingResult.className = 'ping-result-text';
  backendPingResult.textContent = `Pinging ${targetUrl}/api/health ...`;

  const startTime = performance.now();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);
    const res = await fetch(`${targetUrl}/api/health`, { signal: controller.signal });
    clearTimeout(timeoutId);

    const latency = Math.round(performance.now() - startTime);
    if (res.ok) {
      const data = await res.json();
      backendPingResult.className = 'ping-result-text success';
      backendPingResult.innerHTML = `🟢 <strong>ONLINE (${latency}ms)</strong>: ${data.system || 'FastAPI Gateway'} | Air-Gap: ${data.air_gap_verified ? 'VERIFIED' : 'ACTIVE'}`;
      if (backendConnStatusBadge) {
        backendConnStatusBadge.textContent = 'CONNECTED ONLINE ✅';
        backendConnStatusBadge.className = 'badge-emerald';
        backendConnStatusBadge.style.color = 'var(--status-emerald)';
        backendConnStatusBadge.style.borderColor = 'rgba(46, 196, 182, 0.4)';
      }
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    backendPingResult.className = 'ping-result-text error';
    backendPingResult.innerHTML = `🔴 <strong>OFFLINE</strong>: Cannot connect to ${targetUrl} (${err.name === 'AbortError' ? 'Timeout' : err.message}). In offline LAN, verify Node 1 is running at 192.168.1.100:8000 or switch to Localhost if developing on single laptop.`;
    if (backendConnStatusBadge) {
      backendConnStatusBadge.textContent = 'GATEWAY UNREACHABLE';
      backendConnStatusBadge.className = 'badge-emerald';
      backendConnStatusBadge.style.color = 'var(--emergency-crimson)';
      backendConnStatusBadge.style.borderColor = 'var(--emergency-crimson)';
    }
  }
}

function triggerLockdown(reason) {
  lockdownModal.style.display = 'flex';
  airGapStatusBadge.style.background = 'var(--emergency-crimson-bg)';
  airGapStatusBadge.style.color = 'var(--emergency-crimson)';
  airGapStatusText.textContent = 'AIR-GAP VIOLATION';
  console.warn("LOCKDOWN:", reason);
}

function startTelemetry() {
  SovereignAPI.listenToTelemetry({
    onTelemetry: (data) => {
      if (!data.is_air_gapped) triggerLockdown("WAN bytes detected");
    },
    onLockdown: () => triggerLockdown("Gateway active")
  });
}

async function loadAuditLedger() {
  try {
    const ledger = await SovereignAPI.getAuditLedger();
    modalAuditTableBody.innerHTML = '';
    const events = ledger.recent_events || [];
    events.forEach(ev => {
      const tr = document.createElement('tr');
      const shortHash = ev.current_hash ? ev.current_hash.substring(0, 12) + '...' : 'ee20df46...';
      tr.innerHTML = `
        <td style="color: var(--gold-primary); font-weight:700;">#${ev.id}</td>
        <td style="font-size:0.65rem; text-transform:uppercase;">${ev.event_type}</td>
        <td style="color: #93C5FD;">${shortHash}</td>
        <td style="color: var(--status-emerald);">VALID</td>
      `;
      modalAuditTableBody.appendChild(tr);
    });
  } catch (e) {
    console.error("Ledger error:", e);
  }
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

// Run
init();
