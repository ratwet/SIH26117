import { SovereignAPI, USE_MOCK, setMockMode } from './api.js';

// Workspace Screen Element
const appView = document.getElementById('appView');

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
function init() {
  setupEventListeners();
  loadAuditLedger();
  startTelemetry();
  if (userDisplayName) userDisplayName.textContent = currentUser.name;
  if (userRoleLabel) userRoleLabel.textContent = currentUser.role;
  if (userAvatarChar) userAvatarChar.textContent = currentUser.name.charAt(0).toUpperCase();
  if (greetingTitle) greetingTitle.textContent = `Good morning, ${currentUser.name}`;
  console.log("🛡️ Aquanex UI Initialized. Mode:", USE_MOCK ? "MOCK" : "LIVE");
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

  // 4. Customize Modals
  btnCustomize.addEventListener('click', () => openCustomizeModal());
  btnOpenCustomizeTop.addEventListener('click', () => openCustomizeModal());
  btnCloseCustomize.addEventListener('click', () => customizeModal.style.display = 'none');
  modalMockToggle.addEventListener('change', (e) => {
    setMockMode(e.target.checked);
    loadAuditLedger();
  });

  btnSimulateBreachInModal.addEventListener('click', () => {
    customizeModal.style.display = 'none';
    triggerLockdown("Hotspot tether breach test triggered by evaluator.");
  });

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
    },
    onDone: (payload) => {
      finishAssistantResponse(payload, responseContainer);
    },
    onError: (err) => {
      console.error("Execution error:", err);
      isExecuting = false;
      btnChatSend.disabled = false;
      responseContainer.innerHTML = `<p style="color: var(--emergency-crimson);">Execution encountered an error. Please retry or check backend connection.</p>`;
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
  if (btnDocx) btnDocx.addEventListener('click', () => handleDownload('MRPL_Approval_Note_sim-2026.docx', 'docx'));
  if (btnXlsx) btnXlsx.addEventListener('click', () => handleDownload('Cost_Matrix_sim-2026.xlsx', 'xlsx'));

  scrollToBottom();
}

function handleDownload(filename, type) {
  if (USE_MOCK) {
    const text = type === 'docx'
      ? `MRPL REFINERY EXECUTIVE APPROVAL NOTE\nUnit: CDU-2\nLine: CDU-2-04-150-A1A\nStatus: Mandatory Replacement Required\nStatutory Code: API 570`
      : `Line Tag,Nominal,Measured,Corrosion Rate,Remaining Life,Capex (INR)\nCDU-2-04-150-A1A,4.80mm,3.20mm,0.35mm/yr,3.14 Yrs,1154400`;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    return;
  }
  window.open(SovereignAPI.getDownloadUrl(filename), '_blank');
}

function scrollToBottom() {
  workspaceCanvas.scrollTop = workspaceCanvas.scrollHeight;
}

function openCustomizeModal() {
  customizeModal.style.display = 'flex';
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
