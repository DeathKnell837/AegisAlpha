/**
 * web/index.js  —  LexAudit front-end
 * Features: live event polling, upload panel (PDF/DOCX), framework selector,
 *           reset/new-audit, audit history, severity breakdown, findings filter,
 *           agent-online indicator, export (JSON + text), status pill update.
 */
'use strict';

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const CONFIG = Object.freeze({
  EVENTS_URL:      'events.json',
  POLL_INTERVAL_MS: 1000,
  LINE_REVEAL_MS:   35,
  AGENT_ORDER:      ['planner', 'executor', 'reviewer'],
  AGENT_TIMEOUT_MS: 120_000,   // 2 min — if no new event, show "offline"
  MAX_CONTRACT_CHARS: 15_000,
  MAX_HISTORY:      5,
});

const BAND = {
  get REST_URL() { return localStorage.getItem('lexaudit_rest_url') || 'https://app.band.ai'; },
  get ROOM_ID()  { return localStorage.getItem('lexaudit_room_id')  || '15c71300-086d-4f1d-a6f2-a14fc04e398d'; },
  get API_KEY()  { return localStorage.getItem('lexaudit_api_key')  || 'band_a_1781282587_R_qQWK_569pK8JHbIr0sEKOY1VNTjXAS'; }
};

function getBackendUrl(path) {
  const customUrl = localStorage.getItem('lexaudit_backend_url') || 'https://lexaudit-wfmf.onrender.com';
  if (customUrl) {
    const base = customUrl.replace(/\/$/, '');
    return `${base}/${path.replace(/^\//, '')}`;
  }
  return path;
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

function el(tag, opts = {}) {
  const node = document.createElement(tag);
  if (opts.className) node.className = opts.className;
  if (opts.text  != null) node.textContent = opts.text;
  if (opts.html  != null) node.innerHTML   = opts.html;
  if (opts.attrs) for (const [k,v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
  return node;
}

function cleanContent(text) {
  if (!text) return '';
  text = text.replace(/@\[\[7b4960ce-0f45-4ca3-a4ab-52e40923e53a\]\]/g, '@Planner');
  text = text.replace(/@\[\[c174a118-a7a4-43c3-a56f-c98bc300b4b4\]\]/g, '@Executor');
  text = text.replace(/@\[\[b94d5ff2-d8df-488c-9cb5-e19cac8054ac\]\]/g, '@Reviewer');
  text = text.replace(/@\[\[53e0060e-23d5-4db0-a382-899c1f0b54af\]\]/g, '@Rogie');
  text = text.replace(/@\[\[[a-f0-9\-]+\]\]/g, '@User');
  text = text.replace(/@rogiebacanto2002\/planner-agent/ig,  '@Planner');
  text = text.replace(/@rogiebacanto2002\/executor-agent/ig, '@Executor');
  text = text.replace(/@rogiebacanto2002\/reviewer-agent/ig, '@Reviewer');
  // Strip all emojis from content
  text = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '');
  return text;
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined' && marked.parse) return marked.parse(text);
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g,     '<em>$1</em>')
    .replace(/`(.*?)`/g,       '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

// ─── APP STATE ───────────────────────────────────────────────────────────────
const state = {
  lastEventIndex:   0,
  loopCount:        0,
  docTotalLines:    0,
  docRenderedLines: 0,
  eventTimes:       [],
  lastSenderAgent:  null,
  lastEventAt:      null,
  currentAudit:     null,   // { name, verdict, score, findings, timestamp }
  auditHistory:     [],     // last N audits
  activeFilter:     'ALL',
  allFindings:      [],
  isSimulating:     false,
};
const processedEvents = new Set();

// ─── DOCUMENT VIEWER ─────────────────────────────────────────────────────────
function initDocumentViewer(rawText) {
  const container = $('#document-lines');
  if (!container) return;
  container.innerHTML = '';
  const lines = rawText.split('\n');
  state.docTotalLines    = lines.length;
  state.docRenderedLines = 0;
  lines.forEach((lineText, i) => {
    const lineNo  = i + 1;
    const lineDiv = el('div', { className: 'doc-line pending', attrs: { 'data-line-no': String(lineNo) } });
    lineDiv.appendChild(el('span', { className: 'doc-line-no',  text: String(lineNo) }));
    lineDiv.appendChild(el('span', { className: 'doc-line-text', text: lineText }));
    container.appendChild(lineDiv);
  });
  updateDocProgress(0);
}

async function scanContractLines(from, to) {
  const container = $('#document-lines');
  if (!container || !state.docTotalLines) return;
  const start = clamp(from, 1, state.docTotalLines);
  const end   = clamp(to,   start, state.docTotalLines);
  for (let n = start; n <= end; n++) {
    const lineEl = $(`.doc-line[data-line-no="${n}"]`, container);
    if (!lineEl || lineEl.classList.contains('scanned')) continue;
    lineEl.classList.replace('pending', 'scanning');
    lineEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    await sleep(CONFIG.LINE_REVEAL_MS);
    lineEl.classList.replace('scanning', 'scanned');
    state.docRenderedLines++;
    updateDocProgress((state.docRenderedLines / state.docTotalLines) * 100);
  }
}

function flagContractLine(lineNo, severity) {
  const lineEl = $(`.doc-line[data-line-no="${lineNo}"]`, $('#document-lines'));
  if (!lineEl) return;
  lineEl.classList.add('flagged', `flag-${severity}`);
}

function updateDocProgress(pct) {
  const bar = $('#document-progress-bar');
  if (bar) bar.style.width = `${clamp(pct, 0, 100)}%`;
}

// ─── AGENT NODES ─────────────────────────────────────────────────────────────
const NODE_COORDINATES = {
  planner:  { x: 34, y: 34 },
  executor: { x: 34, y: 134 },
  reviewer: { x: 34, y: 234 },
};

function setAgentNodeState(agent, stateStr) {
  $$('.agent-node').forEach(node => {
    node.setAttribute('data-state', 'idle');
    node.classList.remove('state-thinking', 'state-working');
    const lbl = $('.node-state-label', node);
    if (lbl && lbl.textContent !== 'Idle') lbl.textContent = 'Idle';
  });
  const activeNode = $(`#agent-${agent}`);
  if (activeNode) {
    activeNode.setAttribute('data-state', stateStr);
    activeNode.classList.add(`state-${stateStr}`);
    const lbl = $('.node-state-label', activeNode);
    if (lbl) lbl.textContent = stateStr.charAt(0).toUpperCase() + stateStr.slice(1);
  }
}

function resetAgentNodes() {
  $$('.agent-node').forEach(node => {
    node.setAttribute('data-state', 'idle');
    node.className = 'agent-node';
    const lbl = $('.node-state-label', node);
    if (lbl) lbl.textContent = 'Idle';
  });
}

function animateHandoff(fromAgent, toAgent) {
  const packet = $('#connector-packet');
  if (!packet) return;
  const start = NODE_COORDINATES[fromAgent];
  const end   = NODE_COORDINATES[toAgent];
  if (!start || !end) return;
  const color = getComputedStyle(document.documentElement).getPropertyValue(`--${fromAgent}`).trim();
  packet.style.background = color;
  packet.classList.add('is-visible');
  const yDist = end.y - start.y;
  packet.style.transform  = `translateY(${yDist}px)`;
  packet.style.transition = 'transform 700ms cubic-bezier(0.4,0,0.2,1)';
  setTimeout(() => {
    packet.classList.remove('is-visible');
    packet.style.transform  = 'translateY(0)';
    packet.style.transition = 'none';
    const tgt = $(`#agent-${toAgent}`);
    if (tgt) {
      tgt.style.transform = 'scale(1.04)';
      setTimeout(() => { tgt.style.transform = 'scale(1)'; }, 200);
    }
  }, 720);
}

// ─── RISK GAUGE & STATUS ──────────────────────────────────────────────────────
function updateRiskGauge(score, band, verdict) {
  const fill   = $('#risk-gauge-fill');
  const label  = $('#risk-gauge-label');
  const status = $('#overall-status');
  if (!fill || !label) return;

  label.textContent = String(score);
  const maxStroke = 326.7;
  fill.style.strokeDashoffset = String(maxStroke - (score / 100) * maxStroke);

  const colorMap = { LOW: '--risk-low', MEDIUM: '--risk-med', HIGH: '--risk-high', CRITICAL: '--risk-crit' };
  const hexColor = getComputedStyle(document.documentElement).getPropertyValue(colorMap[band] || '--risk-safe').trim();
  fill.style.stroke = hexColor;

  if (status && verdict) {
    status.className = 'pill';
    const v = (verdict || '').toUpperCase();
    if (v.includes('REJECT'))             { status.classList.add('status-fail');       status.innerHTML = '<i data-lucide="x-circle"></i> REJECTED'; }
    else if (v.includes('CONDITIONS'))    { status.classList.add('status-pass-cond');  status.innerHTML = '<i data-lucide="alert-triangle"></i> APPROVED WITH CONDITIONS'; }
    else if (v.includes('APPROVED'))      { status.classList.add('status-pass');       status.innerHTML = '<i data-lucide="check-circle-2"></i> APPROVED'; }
    else if (v.includes('REVISION'))      { status.classList.add('status-pending');    status.innerHTML = '<i data-lucide="refresh-cw"></i> REVISION REQUIRED'; }
    else { status.classList.add('status-pending'); status.textContent = `${band} RISK`; }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

// ─── SEVERITY BREAKDOWN ───────────────────────────────────────────────────────
function updateSeverityBreakdown(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const map = { CRITICAL: 'crit', HIGH: 'high', MEDIUM: 'med', LOW: 'low', COMPLIANT: 'pass' };
  for (const [key, suffix] of Object.entries(map)) {
    const val = counts[key] || 0;
    const bar = $(`#sev-${suffix}`);
    const cnt = $(`#sev-${suffix}-count`);
    if (bar) bar.style.width = `${(val / total) * 100}%`;
    if (cnt) cnt.textContent  = String(val);
  }
}

// ─── CHECKLIST ───────────────────────────────────────────────────────────────
function renderChecklist(items) {
  const container = $('#checklist-container');
  if (!container) return;
  container.innerHTML = '';
  items.forEach(item => {
    const li  = el('li');
    const lbl = item.title.length > 6 ? item.title.slice(0, 6) : item.title;
    li.appendChild(el('span', { className: 'check-title', text: item.title }));
    let cls = 'pending', txt = 'PENDING';
    if (item.status === 'pass')  { cls = 'confirmed'; txt = 'PASS'; }
    if (item.status === 'fail')  { cls = 'rejected';  txt = 'FAIL'; }
    li.appendChild(el('span', { className: `badge-status ${cls}`, text: txt }));
    container.appendChild(li);
  });
}

// ─── FINDINGS ────────────────────────────────────────────────────────────────
function renderFindings(findings) {
  const container = $('#findings-container');
  if (!container) return;
  container.innerHTML = '';
  state.allFindings = findings;

  // Calculate total exposure for the summary
  let totalExposureLow = 0, totalExposureHigh = 0;

  findings.forEach(f => {
    const sev      = (f.severity || 'LOW').toLowerCase();
    const item     = el('li', { className: 'finding-item', attrs: { 'data-severity': (f.severity||'LOW').toUpperCase() } });

    // Title row with severity badge + verdict status badge
    const titleRow = el('div', { className: 'finding-title' });
    titleRow.appendChild(el('span', { text: f.title }));
    const badgeRow = el('div', { className: 'finding-badges' });
    badgeRow.appendChild(el('span', { className: `badge-status ${sev}`, text: f.severity || 'LOW' }));
    // Verdict status badge (CONFIRMED/REJECTED/CHALLENGED/ADDED)
    if (f.verdict_status) {
      const vsCls = f.verdict_status.toLowerCase();
      badgeRow.appendChild(el('span', { className: `badge-verdict badge-verdict--${vsCls}`, text: f.verdict_status }));
    }
    titleRow.appendChild(badgeRow);
    item.appendChild(titleRow);

    // Confidence bar
    const conf = f.confidence || 0;
    const execConf = f.executor_confidence || 0;
    if (conf > 0) {
      const confRow = el('div', { className: 'finding-confidence' });
      const confBarOuter = el('div', { className: 'confidence-bar-outer' });
      const confBarInner = el('div', { className: `confidence-bar-inner confidence-${conf >= 80 ? 'high' : conf >= 50 ? 'med' : 'low'}` });
      confBarInner.style.width = `${conf}%`;
      confBarOuter.appendChild(confBarInner);
      confRow.appendChild(el('span', { className: 'confidence-label', text: `Confidence: ${conf}%` }));
      if (execConf > 0) confRow.appendChild(el('span', { className: 'confidence-exec', text: `(Executor: ${execConf}%)` }));
      confRow.appendChild(confBarOuter);
      item.appendChild(confRow);
    }

    item.appendChild(el('div', { className: 'finding-meta', text: `Clause: ${f.clause_ref || 'N/A'}` }));
    item.appendChild(el('div', { className: 'finding-desc', text: f.description || '' }));

    // Devil's Advocate section
    if (f.devils_advocate) {
      const daSection = el('div', { className: 'finding-devils-advocate' });
      daSection.appendChild(el('div', { className: 'da-header', html: '<i data-lucide="swords"></i> Devil\'s Advocate' }));
      daSection.appendChild(el('div', { className: 'da-content', text: f.devils_advocate }));
      item.appendChild(daSection);
    }

    // Dollar exposure
    if (f.exposure_low != null && f.exposure_high != null && (f.exposure_low > 0 || f.exposure_high > 0)) {
      const fmtLow = '$' + Number(f.exposure_low).toLocaleString();
      const fmtHigh = '$' + Number(f.exposure_high).toLocaleString();
      item.appendChild(el('div', { className: 'finding-exposure', html: `<i data-lucide="dollar-sign"></i> Est. Exposure: ${fmtLow}–${fmtHigh}` }));
      totalExposureLow += Number(f.exposure_low) || 0;
      totalExposureHigh += Number(f.exposure_high) || 0;
    }

    if (f.recommendation) {
      item.appendChild(el('div', { className: 'finding-recommendation', html: `<i data-lucide="lightbulb"></i> ${f.recommendation}` }));
    }
    container.appendChild(item);
  });

  // Update total exposure display
  const totalEl = $('#total-exposure');
  if (totalEl && (totalExposureLow > 0 || totalExposureHigh > 0)) {
    totalEl.innerHTML = `<i data-lucide="trending-up"></i> Total Est. Exposure: $${totalExposureLow.toLocaleString()}–$${totalExposureHigh.toLocaleString()}`;
    totalEl.style.display = 'flex';
  } else if (totalEl) {
    totalEl.style.display = 'none';
  }

  applyFindingsFilter(state.activeFilter);
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function applyFindingsFilter(filter) {
  state.activeFilter = filter;
  $$('.finding-item').forEach(item => {
    const sev = item.getAttribute('data-severity') || '';
    const hidden = filter !== 'ALL' && sev !== filter;
    item.setAttribute('data-hidden', hidden ? 'true' : 'false');
  });
  $$('.filter-chip').forEach(chip => {
    chip.classList.toggle('active', chip.dataset.filter === filter);
  });
}

// ─── CHAT LOG ────────────────────────────────────────────────────────────────
function appendChatMessage(agent, content, timestamp) {
  const container = $('#message-log');
  if (!container) return;
  const entry  = el('div', { className: `log-entry ${agent}` });
  const header = el('div', { className: 'log-header' });
  header.appendChild(el('span', { className: 'log-agent-name', text: `${agent.toUpperCase()} AGENT` }));
  header.appendChild(el('span', { className: 'log-ts', text: new Date(timestamp).toLocaleTimeString() }));
  entry.appendChild(header);
  entry.appendChild(el('div', { className: 'log-body', html: renderMarkdown(cleanContent(content)) }));
  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
}

// ─── AGENT STATUS INDICATOR ───────────────────────────────────────────────────
function updateAgentStatus(online) {
  const indicator = $('#agent-status-indicator');
  const label     = indicator ? $('.agent-status-label', indicator) : null;
  if (!indicator) return;
  indicator.className = `agent-status agent-status--${online ? 'online' : 'offline'}`;
  if (label) label.textContent = online ? 'Agents Online' : 'Agents Offline';
}

function checkAgentStatus() {
  if (!state.lastEventAt) { updateAgentStatus(false); return; }
  const elapsed = Date.now() - state.lastEventAt.getTime();
  updateAgentStatus(elapsed < CONFIG.AGENT_TIMEOUT_MS);
}

// ─── AUDIT HISTORY ────────────────────────────────────────────────────────────
function saveAuditToHistory(audit) {
  // Prevent duplicate audits during event replay on page load
  const isDuplicate = state.auditHistory.some(existing => 
    (existing.timestamp === audit.timestamp && existing.name === audit.name) ||
    (existing.score === audit.score && existing.verdict === audit.verdict && existing.name === audit.name)
  );
  if (isDuplicate) return;

  state.auditHistory.unshift(audit);
  if (state.auditHistory.length > CONFIG.MAX_HISTORY) state.auditHistory.pop();
  renderAuditHistory();
  try {
    localStorage.setItem('lexaudit_history', JSON.stringify(state.auditHistory));
    localStorage.setItem('lexaudit_lastEventIndex', String(state.lastEventIndex));
  } catch(e){}
}

function loadAuditHistory() {
  try {
    const saved = localStorage.getItem('lexaudit_history');
    if (saved) { state.auditHistory = JSON.parse(saved); renderAuditHistory(); }
    // Restore lastEventIndex to prevent replay of already-processed events
    const savedIdx = localStorage.getItem('lexaudit_lastEventIndex');
    if (savedIdx) { state.lastEventIndex = parseInt(savedIdx, 10) || 0; }
  } catch(e){}
}

function loadAudit(audit) {
  state.currentAudit = audit;
  
  // Set headers
  const contractName = $('#contract-name');
  const contractType = $('#contract-type');
  if (contractName) contractName.textContent = audit.name || 'Contract';
  if (contractType) contractType.textContent = audit.contractType || 'NDA';
  
  // Set document viewer
  if (audit.contractText) {
    initDocumentViewer(audit.contractText);
  }
  
  // Set risk gauge and overall status
  updateRiskGauge(audit.score, audit.band, audit.verdict);
  
  // Set checklist
  if (audit.checklist) {
    renderChecklist(audit.checklist);
  } else {
    const chk = $('#checklist-container');
    if (chk) chk.innerHTML = '';
  }
  
  // Set findings
  if (audit.findings) {
    renderFindings(audit.findings);
  } else {
    const fnd = $('#findings-container');
    if (fnd) fnd.innerHTML = '';
  }
  
  // Set severity breakdown counts
  let counts = audit.severityCounts;
  if (!counts && audit.findings) {
    counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, COMPLIANT: 0 };
    audit.findings.forEach(f => {
      const sev = (f.severity || 'LOW').toUpperCase();
      const mappedKey = sev === 'PASS' || sev === 'COMPLIANT' ? 'COMPLIANT' : sev;
      if (counts[mappedKey] !== undefined) counts[mappedKey]++;
    });
  }
  if (counts) {
    updateSeverityBreakdown(counts);
  }
  
  // Highlight contract lines based on findings
  if (audit.findings) {
    audit.findings.forEach(f => {
      const m = (f.clause_ref || '').match(/\d+/);
      if (m) flagContractLine(parseInt(m[0], 10), (f.severity || 'low').toLowerCase());
    });
  }

  // Add system message to collaboration stream
  const logContainer = $('#message-log');
  if (logContainer) {
    const entry = el('div', { className: 'log-entry system', html: `<div class="log-desc">Loaded historical audit report for "${audit.name}" (Risk Score: ${audit.score}/100)</div>` });
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  // Hide upload zone and show contract viewer style
  showUploadState('upload-sent');
  
  // Enable export button
  const btnExport = $('#btn-export-report');
  if (btnExport) btnExport.disabled = false;
}

function renderAuditHistory() {
  const container = $('#audit-history-list');
  if (!container) return;
  if (!state.auditHistory.length) {
    container.innerHTML = '<p class="history-empty">No previous audits this session.</p>';
    return;
  }
  container.innerHTML = '';
  state.auditHistory.forEach(audit => {
    const item    = el('div', { className: 'history-item' });
    const verdict = (audit.verdict || '').toUpperCase();
    let verdictCls = 'conditions', verdictTxt = audit.verdict || '—';
    if (verdict.includes('REJECT'))        { verdictCls = 'fail'; }
    else if (verdict.includes('APPROVED') && !verdict.includes('CONDITIONS')) { verdictCls = 'pass'; }

    item.appendChild(el('div', { className: 'history-item-name', text: audit.name || 'Contract' }));
    const meta = el('div', { className: 'history-item-meta' });
    meta.appendChild(el('span', { className: `history-item-verdict ${verdictCls}`, text: verdictTxt }));
    meta.appendChild(el('span', { className: 'history-item-score',   text: `Risk: ${audit.score ?? '—'}/100` }));
    item.appendChild(meta);

    // Make history item clickable to load audit
    item.addEventListener('click', () => {
      loadAudit(audit);
    });

    container.appendChild(item);
  });
}

// ─── EXPORT ───────────────────────────────────────────────────────────────────
function generateTextReport() {
  if (!state.currentAudit) return 'No audit data available.';
  const a = state.currentAudit;
  const lines = [
    '====================================',
    '       LEXAUDIT COMPLIANCE REPORT   ',
    '====================================',
    `Contract:   ${a.name || '—'}`,
    `Verdict:    ${a.verdict || '—'}`,
    `Risk Score: ${a.score ?? '—'} / 100`,
    `Generated:  ${new Date(a.timestamp).toLocaleString()}`,
    '',
    '── FINDINGS ─────────────────────────',
    ...(a.findings || []).map(f =>
      `[${f.severity}] ${f.title} — ${f.clause_ref}\n  ${f.description}\n  ${f.recommendation ? '→ ' + f.recommendation : ''}`
    ),
    '',
    '====================================',
    'Generated by LexAudit v1.0',
  ];
  return lines.join('\n');
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ─── RESET DASHBOARD ─────────────────────────────────────────────────────────
async function resetDashboard() {
  // 1. Reset DOM instantly for immediate visual feedback
  const clear = id => { const el = document.getElementById(id); if (el) el.innerHTML = ''; };
  clear('document-lines');
  clear('message-log');
  clear('findings-container');
  clear('checklist-container');
  // NOTE: We do NOT clear 'severity-breakdown' layout wrapper as that deletes the HTML grid structure!

  updateDocProgress(0);
  updateRiskGauge(0, 'NONE', null);
  resetAgentNodes();

  const contractName = $('#contract-name');
  const contractType = $('#contract-type');
  const status       = $('#overall-status');
  if (contractName) contractName.textContent = '—';
  if (contractType) contractType.textContent = '—';
  if (status)       { status.className = 'pill status-pending'; status.textContent = 'PENDING SCAN'; }

  // Reset severity bars
  ['crit','high','med','low','pass'].forEach(s => {
    const bar = $(`#sev-${s}`);
    const cnt = $(`#sev-${s}-count`);
    if (bar) bar.style.width = '0%';
    if (cnt) cnt.textContent = '0';
  });

  // Disable export
  const btnExport = $('#btn-export-report');
  if (btnExport) btnExport.disabled = true;

  // Reset upload panel
  showUploadState('upload-idle');
  _extractedText     = '';
  _extractedFilename = '';
  _referenceText     = '';
  _referenceFilename = '';
  const fileInput = $('#file-input');
  if (fileInput) fileInput.value = '';
  const refFileInput = $('#ref-file-input');
  if (refFileInput) refFileInput.value = '';
  const refLabel = $('#ref-status-label');
  if (refLabel) refLabel.textContent = 'Audit contract against custom rules (PDF, DOCX, TXT)';
  const btnChooseRef = $('#btn-choose-ref');
  if (btnChooseRef) btnChooseRef.style.display = 'inline-block';
  const btnClearRef = $('#btn-clear-ref');
  if (btnClearRef) btnClearRef.style.display = 'none';

  // 2. Reset JS state variables
  state.lastSenderAgent  = null;
  state.eventTimes       = [];
  state.lastEventAt      = null;
  state.currentAudit     = null;
  state.allFindings      = [];
  state.activeFilter     = 'ALL';
  state.isSimulating     = false;
  processedEvents.clear();

  // 3. Clear events.json via POST (awaited for reliability)
  try {
    await fetch(getBackendUrl('reset'), { method: 'POST' });
  } catch(e) { console.warn('Reset endpoint failed:', e); }

  // 4. Fetch current size of event log on server to skip replaying past events
  try {
    const res = await fetch(getBackendUrl(`${CONFIG.EVENTS_URL}?t=${Date.now()}`));
    if (res.ok) {
      const events = await res.json();
      state.lastEventIndex = events.length;
    } else {
      state.lastEventIndex = 0;
    }
  } catch(e) {
    state.lastEventIndex = 0;
  }
}

// ─── EVENT PROCESSING ─────────────────────────────────────────────────────────
async function processEvent(ev) {
  const sig = `${ev.timestamp}_${ev.agent}_${ev.type}`;
  if (processedEvents.has(sig)) return;
  processedEvents.add(sig);

  state.lastEventAt = new Date();
  updateAgentStatus(true);

  // Footer
  const label = $('#socket-label');
  const dot   = $('#connection-status');
  const evCnt = $('#statusbar-event-count');
  const evLst = $('#statusbar-last-event');
  if (dot)   dot.className = 'dot dot--on';
  if (label) label.textContent = 'Connected';
  if (evCnt) evCnt.textContent = `${state.lastEventIndex} events`;
  if (evLst) evLst.textContent = `Last: ${new Date(ev.timestamp).toLocaleTimeString()}`;

  // 1. THINKING
  if (ev.type === 'thinking') {
    setAgentNodeState(ev.agent, 'thinking');
    if (ev.agent === 'executor' && state.lastSenderAgent === 'planner')   animateHandoff('planner',   'executor');
    if (ev.agent === 'reviewer' && state.lastSenderAgent === 'executor')  animateHandoff('executor',  'reviewer');
  }

  // 2. MESSAGE
  else if (ev.type === 'message') {
    setAgentNodeState(ev.agent, 'idle');
    appendChatMessage(ev.agent, ev.content, ev.timestamp);
    state.lastSenderAgent = ev.agent;
  }

  // 3. STRUCTURED EVENTS
  else if (ev.type === 'event') {
    const meta = ev.metadata || {};

    if (ev.message_type === 'compliance_plan_created') {
      const nameEl = $('#contract-name');
      const typeEl = $('#contract-type');
      if (nameEl) nameEl.textContent = meta.contract || '—';
      if (typeEl) typeEl.textContent = meta.contract_type || 'NDA';

      if (meta.contract_text) {
        initDocumentViewer(meta.contract_text);
      } else if (!state.docTotalLines) {
        const rawText = 'MUTUAL NON-DISCLOSURE AGREEMENT\n1. Purpose: evaluate partnership.\n14. Liability: Neither party limits liability.\n16. Governing Law: Laws of North Korea.';
        initDocumentViewer(rawText);
      }

      renderChecklist((meta.checkpoints || []).map(cp => ({ title: cp, status: 'pending' })));
    }

    else if (ev.message_type === 'compliance_analysis_completed') {
      renderChecklist((meta.findings || []).map(f => ({
        title:  f.checkpoint || 'Clause check',
        status: (['CRITICAL','HIGH'].includes(f.severity)) ? 'fail' : 'pass',
      })));
      await scanContractLines(1, state.docTotalLines);
      (meta.findings || []).forEach(f => {
        const m = (f.clause || '').match(/\d+/);
        if (m) flagContractLine(parseInt(m[0], 10), (f.severity || 'low').toLowerCase());
      });
      updateSeverityBreakdown(meta.severity_counts || {});
    }

    else if (ev.message_type === 'compliance_review_completed') {
      const score   = meta.risk_score || 0;
      const verdict = meta.verdict    || 'APPROVED';
      let band = 'LOW';
      if (score > 80) band = 'CRITICAL';
      else if (score > 50) band = 'HIGH';
      else if (score > 20) band = 'MEDIUM';

      updateRiskGauge(score, band, verdict);

      const findings = (meta.findings || []).map(f => ({
        title:              f.title             || 'Legal Defect',
        severity:           f.severity          || 'LOW',
        clause_ref:         f.clause_ref        || 'N/A',
        description:        f.description       || '',
        recommendation:     f.recommendation    || '',
        verdict_status:     f.verdict_status    || null,
        confidence:         f.confidence        || 0,
        executor_confidence:f.executor_confidence|| 0,
        devils_advocate:    f.devils_advocate    || '',
        exposure_low:       f.exposure_low      || null,
        exposure_high:      f.exposure_high     || null,
      }));
      renderFindings(findings);

      // Save to history
      const auditRecord = {
        name:      meta.contract   || $('#contract-name')?.textContent || 'Contract',
        verdict:   verdict,
        score:     score,
        band:      band,
        findings:  findings,
        timestamp: ev.timestamp,
        contractText: $('#document-lines')?.innerText || '',
        contractType: $('#contract-type')?.textContent || 'NDA',
        checklist: $$('#checklist-container li').map(li => {
          const title = $('.check-title', li)?.textContent || '';
          const badge = $('.badge-status', li);
          let status = 'pending';
          if (badge) {
            if (badge.classList.contains('confirmed')) status = 'pass';
            else if (badge.classList.contains('rejected')) status = 'fail';
          }
          return { title, status };
        }),
        severityCounts: {
          CRITICAL: parseInt($('#sev-crit-count')?.textContent || '0', 10),
          HIGH: parseInt($('#sev-high-count')?.textContent || '0', 10),
          MEDIUM: parseInt($('#sev-med-count')?.textContent || '0', 10),
          LOW: parseInt($('#sev-low-count')?.textContent || '0', 10),
          COMPLIANT: parseInt($('#sev-pass-count')?.textContent || '0', 10),
        }
      };
      state.currentAudit = auditRecord;
      saveAuditToHistory(auditRecord);

      // Enable export
      const btnExport = $('#btn-export-report');
      if (btnExport) btnExport.disabled = false;
    }
  }
}

// ─── EVENT POLLER ─────────────────────────────────────────────────────────────
async function pollEvents() {
  if (state.isSimulating) return;
  try {
    const res = await fetch(getBackendUrl(`${CONFIG.EVENTS_URL}?t=${Date.now()}`));
    if (!res.ok) return;
    const events = await res.json();

    // Auto-reset on cleared events
    if (events.length < state.lastEventIndex) {
      await resetDashboard();
    }

    if (events.length > state.lastEventIndex) {
      const newEvents = events.slice(state.lastEventIndex);
      state.lastEventIndex = events.length;
      for (const ev of newEvents) await processEvent(ev);
    }
  } catch(err) {
    console.warn('Poller error:', err);
    updateAgentStatus(false);
  }
}

// ─── UPLOAD PANEL ─────────────────────────────────────────────────────────────
let _extractedText     = '';
let _extractedFilename = '';
let _referenceText     = '';
let _referenceFilename = '';

function showUploadState(id) {
  ['upload-idle','upload-loading','upload-ready','upload-sending','upload-sent']
    .forEach(s => {
      const el = document.getElementById(s);
      if (el) el.style.display = (s === id) ? 'flex' : 'none';
    });
}

async function extractPdfText(file) {
  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
  }
  const buf = await file.arrayBuffer();
  const pdf = await window.pdfjsLib.getDocument({ data: buf }).promise;
  let text = '';
  for (let i = 1; i <= pdf.numPages; i++) {
    const page    = await pdf.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map(it => it.str).join(' ') + '\n';
  }
  return text.trim();
}

async function extractDocxText(file) {
  const buf    = await file.arrayBuffer();
  const result = await window.mammoth.extractRawText({ arrayBuffer: buf });
  return result.value.trim();
}

async function handleFile(file) {
  if (!file) return;
  const name = file.name.toLowerCase();
  if (!name.endsWith('.pdf') && !name.endsWith('.docx') && !name.endsWith('.txt')) {
    alert('Please upload a PDF, DOCX, or TXT file.');
    return;
  }
  showUploadState('upload-loading');
  try {
    let text = '';
    if (name.endsWith('.pdf')) {
      text = await extractPdfText(file);
    } else if (name.endsWith('.docx')) {
      text = await extractDocxText(file);
    } else {
      text = await file.text();
    }
    if (!text || text.length < 10) throw new Error('No text found in file. Try a different file.');

    _extractedText     = text;
    _extractedFilename = file.name;

    const filenameEl  = $('#upload-filename');
    const charcountEl = $('#upload-charcount');
    const warningEl   = $('#upload-size-warning');
    if (filenameEl)  filenameEl.textContent  = file.name;
    if (charcountEl) charcountEl.textContent = `${text.length.toLocaleString()} characters extracted`;
    if (warningEl)   warningEl.style.display = text.length > CONFIG.MAX_CONTRACT_CHARS ? 'block' : 'none';

    // Preview in contract viewer
    initDocumentViewer(text.slice(0, 3000) + (text.length > 3000 ? '\n…[truncated for preview]' : ''));
    showUploadState('upload-ready');
  } catch(err) {
    console.error(err);
    alert('Error reading file: ' + err.message);
    showUploadState('upload-idle');
  }
}

function getSelectedFrameworks() {
  return $$('.framework-chip.active').map(c => c.dataset.fw).join(', ');
}

async function sendContractToAgents(text, filename) {
  const shortName  = filename.replace(/\.[^.]+$/, '');
  const truncated  = text.length > CONFIG.MAX_CONTRACT_CHARS ? text.slice(0, CONFIG.MAX_CONTRACT_CHARS) + '\n\n[Note: contract was truncated due to size]' : text;
  const frameworks = getSelectedFrameworks() || 'GDPR, CCPA/CPRA, HIPAA, SOC 2, SOX, AML/KYC';

  let message = `@rogiebacanto2002/planner-agent Please audit the following contract for compliance against ${frameworks}`;
  if (_referenceText) {
    message += ` and the provided reference rules.\n\nREFERENCE RULES:\n${_referenceText}`;
  } else {
    message += `.\n`;
  }
  message += `\nCONTRACT NAME: ${shortName}\n\nCONTRACT TEXT:\n${truncated}`;

  try {
    const res = await fetch(getBackendUrl(`send-message?room_id=${BAND.ROOM_ID}`), {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${BAND.API_KEY}` },
      body:    JSON.stringify({ content: message, mentions: ['@rogiebacanto2002/planner-agent'] }),
    });
    if (res.ok) {
      return res.json();
    }
    if (res.status === 404) {
      console.log("Static client/Vercel environment detected (Proxy returns 404). Triggering client-side simulation.");
      runClientSideSimulation(text, filename);
      return { status: "simulated" };
    }
    throw new Error(`Proxy error ${res.status}`);
  } catch (err) {
    console.warn("Send message failed, falling back to client-side simulation:", err);
    runClientSideSimulation(text, filename);
    return { status: "simulated" };
  }
}

async function runClientSideSimulation(text, filename) {
  state.isSimulating = true;
  const shortName = filename.replace(/\.[^.]+$/, '');

  let templateEvents = [];
  try {
    const res = await fetch(`events.json?t=${Date.now()}`);
    if (res.ok) {
      templateEvents = await res.json();
    }
  } catch (e) {
    console.error("Failed to load events template for simulation:", e);
  }

  if (!templateEvents || templateEvents.length === 0) {
    console.error("No simulation template events found.");
    state.isSimulating = false;
    return;
  }

  const simulatedEvents = templateEvents.map(ev => {
    const newEv = JSON.parse(JSON.stringify(ev));
    newEv.timestamp = new Date().toISOString();
    if (newEv.type === 'event' && newEv.message_type === 'compliance_plan_created') {
      newEv.metadata.contract = shortName;
      newEv.metadata.contract_text = text;
    }
    if (newEv.type === 'event' && newEv.message_type === 'compliance_review_completed') {
      newEv.metadata.contract = shortName;
    }
    return newEv;
  });

  (async () => {
    for (const ev of simulatedEvents) {
      if (!state.isSimulating) break;
      await processEvent(ev);

      let delay = 1500;
      if (ev.type === 'thinking') delay = 1200;
      else if (ev.type === 'message') delay = 2500;
      else if (ev.type === 'event') {
        if (ev.message_type === 'compliance_analysis_completed') delay = 500;
        else delay = 800;
      }
      await sleep(delay);
    }
  })();
}

function initUploadPanel() {
  const zone      = $('#upload-zone');
  const fileInput = $('#file-input');
  const btnAudit  = $('#btn-start-audit');
  const btnClear  = $('#btn-clear-upload');
  const btnOther  = $('#btn-audit-another');
  if (!zone) return;

  zone.addEventListener('dragover',  e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const f = e.dataTransfer?.files?.[0];
    if (f) handleFile(f);
  });
  zone.addEventListener('click', e => {
    if (['upload-icon','upload-title','upload-sub'].some(c => e.target.classList.contains(c)) || e.target === zone)
      fileInput?.click();
  });
  fileInput?.addEventListener('change', () => { const f = fileInput.files?.[0]; if (f) handleFile(f); });

  btnAudit?.addEventListener('click', async () => {
    if (!_extractedText) return;
    const text = _extractedText;
    const filename = _extractedFilename;
    const refText = _referenceText;
    const refFilename = _referenceFilename;
    showUploadState('upload-sending');
    try {
      await resetDashboard();
      _referenceText = refText;
      _referenceFilename = refFilename;
      await sendContractToAgents(text, filename);
      showUploadState('upload-sent');
    } catch(err) {
      console.error(err);
      alert('Failed to send: ' + err.message);
      showUploadState('upload-ready');
    }
  });

  btnClear?.addEventListener('click', () => {
    _extractedText = _extractedFilename = '';
    if (fileInput) fileInput.value = '';
    showUploadState('upload-idle');
  });

  btnOther?.addEventListener('click', () => {
    _extractedText = _extractedFilename = '';
    if (fileInput) fileInput.value = '';
    showUploadState('upload-idle');
  });

  // Framework chips toggle
  $$('.framework-chip').forEach(chip => {
    chip.addEventListener('click', () => chip.classList.toggle('active'));
  });

  // Reference file input
  const refFileInput = $('#ref-file-input');
  const btnClearRef  = $('#btn-clear-ref');
  const btnChooseRef = $('#btn-choose-ref');
  refFileInput?.addEventListener('change', () => {
    const f = refFileInput.files?.[0];
    if (f) handleReferenceFile(f);
  });
  btnClearRef?.addEventListener('click', () => {
    _referenceText = '';
    _referenceFilename = '';
    if (refFileInput) refFileInput.value = '';
    const refLabel = $('#ref-status-label');
    if (refLabel) refLabel.textContent = 'Audit contract against custom rules (PDF, DOCX, TXT)';
    if (btnChooseRef) btnChooseRef.style.display = 'inline-block';
    if (btnClearRef) btnClearRef.style.display = 'none';
  });
}

async function handleReferenceFile(file) {
  if (!file) return;
  const name = file.name.toLowerCase();
  if (!name.endsWith('.pdf') && !name.endsWith('.docx') && !name.endsWith('.txt')) {
    alert('Please upload a PDF, DOCX, or TXT file for reference guidelines.');
    return;
  }
  const refLabel = $('#ref-status-label');
  const btnChooseRef = $('#btn-choose-ref');
  const btnClearRef = $('#btn-clear-ref');
  if (refLabel) refLabel.textContent = 'Extracting reference rules...';
  try {
    let text = '';
    if (name.endsWith('.pdf')) {
      text = await extractPdfText(file);
    } else if (name.endsWith('.docx')) {
      text = await extractDocxText(file);
    } else {
      text = await file.text();
    }
    if (!text || text.length < 10) throw new Error('No text found in file.');

    _referenceText = text;
    _referenceFilename = file.name;

    if (refLabel) refLabel.textContent = `Attached: ${file.name} (${text.length.toLocaleString()} chars)`;
    if (btnChooseRef) btnChooseRef.style.display = 'none';
    if (btnClearRef) btnClearRef.style.display = 'inline-block';
  } catch (err) {
    console.error(err);
    alert('Error reading reference file: ' + err.message);
    _referenceText = '';
    _referenceFilename = '';
    if (refLabel) refLabel.textContent = 'Audit contract against custom rules (PDF, DOCX, TXT)';
    if (btnChooseRef) btnChooseRef.style.display = 'inline-block';
    if (btnClearRef) btnClearRef.style.display = 'none';
  }

// ─── INIT ─────────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  resetAgentNodes();
  loadAuditHistory();
  initUploadPanel();

  // Clear Audit History button
  $('#btn-clear-history')?.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the audit history?')) {
      state.auditHistory = [];
      try {
        localStorage.removeItem('lexaudit_history');
      } catch(e){}
      renderAuditHistory();
    }
  });

  // New Audit button
  $('#btn-new-audit')?.addEventListener('click', async () => {
    const btn = $('#btn-new-audit');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i data-lucide="loader"></i> Resetting...'; }
    await resetDashboard();
    // Add system message confirming reset
    const logContainer = $('#message-log');
    if (logContainer) {
      const entry = el('div', { className: 'log-entry system', html: '<div class="log-desc">Dashboard reset — ready for a new audit.</div>' });
      logContainer.appendChild(entry);
    }
    if (btn) { btn.disabled = false; btn.innerHTML = '<i data-lucide="refresh-cw"></i> New Audit'; }
    if (typeof lucide !== 'undefined') lucide.createIcons();
    // Scroll upload panel into view
    const uploadPanel = $('#upload-panel');
    if (uploadPanel) uploadPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // Export button
  $('#btn-export-report')?.addEventListener('click', () => {
    const modal = $('#export-modal');
    if (modal) modal.style.display = 'flex';
  });
  $('#btn-close-export')?.addEventListener('click', () => {
    const modal = $('#export-modal');
    if (modal) modal.style.display = 'none';
  });
  $('#btn-export-json')?.addEventListener('click', () => {
    if (!state.currentAudit) return;
    downloadBlob(JSON.stringify(state.currentAudit, null, 2), 'lexaudit_report.json', 'application/json');
    $('#export-modal').style.display = 'none';
  });
  $('#btn-export-txt')?.addEventListener('click', () => {
    downloadBlob(generateTextReport(), 'lexaudit_report.txt', 'text/plain');
    $('#export-modal').style.display = 'none';
  });

  // Findings filter
  $$('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => applyFindingsFilter(chip.dataset.filter));
  });

  // Close export modal when clicking backdrop
  $('#export-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'export-modal') {
      $('#export-modal').style.display = 'none';
    }
  });

  // Settings button
  $('#btn-settings')?.addEventListener('click', () => {
    const modal = $('#settings-modal');
    if (modal) {
      const roomInput = $('#settings-room-id');
      const keyInput = $('#settings-api-key');
      const backendInput = $('#settings-backend-url');
      if (roomInput) roomInput.value = BAND.ROOM_ID;
      if (keyInput) keyInput.value = BAND.API_KEY;
      if (backendInput) backendInput.value = localStorage.getItem('lexaudit_backend_url') || 'https://lexaudit-wfmf.onrender.com';
      modal.style.display = 'flex';
    }
  });
  $('#btn-close-settings')?.addEventListener('click', () => {
    const modal = $('#settings-modal');
    if (modal) modal.style.display = 'none';
  });
  $('#btn-save-settings')?.addEventListener('click', async () => {
    const roomId = $('#settings-room-id')?.value.trim();
    const apiKey = $('#settings-api-key')?.value.trim();
    const backendUrl = $('#settings-backend-url')?.value.trim();
    if (roomId) localStorage.setItem('lexaudit_room_id', roomId);
    if (apiKey) localStorage.setItem('lexaudit_api_key', apiKey);
    if (backendUrl !== undefined) {
      if (backendUrl) {
        localStorage.setItem('lexaudit_backend_url', backendUrl);
      } else {
        localStorage.removeItem('lexaudit_backend_url');
      }
    }
    
    const modal = $('#settings-modal');
    if (modal) modal.style.display = 'none';
    
    // Reset dashboard to sync pointer on the new room
    await resetDashboard();
  });
  $('#btn-reset-settings')?.addEventListener('click', async () => {
    localStorage.removeItem('lexaudit_room_id');
    localStorage.removeItem('lexaudit_api_key');
    localStorage.removeItem('lexaudit_backend_url');
    const modal = $('#settings-modal');
    if (modal) modal.style.display = 'none';
    await resetDashboard();
  });
  $('#settings-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'settings-modal') {
      $('#settings-modal').style.display = 'none';
    }
  });

  // Agent status check every 30s
  setInterval(checkAgentStatus, 30_000);

  // Start polling
  setInterval(pollEvents, CONFIG.POLL_INTERVAL_MS);
  pollEvents();

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});
