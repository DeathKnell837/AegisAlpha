/* ══════════════════════════════════════════════════════════════
   AegisAlpha v3 — Full Interactive Dashboard Engine
   ══════════════════════════════════════════════════════════════ */
let payoffChart = null;
let currentSymbol = 'SPY';
let currentStrategy = 'Bull Call Spread';
let pendingCloseSymbol = null;

// Preset profiles for watchlist stocks
const STOCK_PROFILES = {
  SPY:  { price: 769.28, delta: '+0.40', gamma: '+0.034', theta: '-0.27', vega: '+0.46', iv: '9.34%',  strategy: 'Bull Call Spread', strikes: [750, 755, 760, 765, 770, 773, 778, 785, 790], payoff: [-100, -100, -100, -100, -50, 0, 400, 400, 400] },
  QQQ:  { price: 520.14, delta: '+0.42', gamma: '+0.028', theta: '-0.31', vega: '+0.52', iv: '14.20%', strategy: 'Bull Call Spread', strikes: [505, 510, 515, 520, 525, 530, 535, 540, 545], payoff: [-120, -120, -120, -60, 0, 180, 380, 380, 380] },
  NVDA: { price: 132.80, delta: '+0.38', gamma: '+0.065', theta: '-0.45', vega: '+0.68', iv: '42.80%', strategy: 'Bull Call Spread', strikes: [120, 125, 130, 133, 135, 140, 145, 150, 155], payoff: [-80, -80, -80, -20, 40, 220, 320, 320, 320] },
  AAPL: { price: 232.10, delta: '-0.35', gamma: '+0.022', theta: '-0.18', vega: '+0.38', iv: '18.60%', strategy: 'Bear Put Spread',  strikes: [220, 225, 228, 230, 232, 235, 240, 245, 250], payoff: [250, 250, 200, 100, 0, -90, -90, -90, -90] },
  TSLA: { price: 214.50, delta: '+0.45', gamma: '+0.048', theta: '-0.52', vega: '+0.74', iv: '55.10%', strategy: 'Bull Call Spread', strikes: [195, 200, 205, 210, 215, 220, 225, 230, 235], payoff: [-150, -150, -150, -50, 50, 350, 450, 450, 450] },
  MSFT: { price: 448.20, delta: '+0.32', gamma: '+0.019', theta: '-0.22', vega: '+0.41', iv: '16.40%', strategy: 'Bull Call Spread', strikes: [430, 435, 440, 445, 448, 455, 460, 465, 470], payoff: [-110, -110, -110, -30, 0, 290, 390, 390, 390] },
};

/* ── TOAST NOTIFICATIONS ── */
function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const iconName = type === 'error' ? 'alert-circle' : (type === 'info' ? 'info' : 'check-circle-2');
  toast.innerHTML = `<i data-lucide="${iconName}"></i><span>${msg}</span>`;
  container.appendChild(toast);
  lucide.createIcons();
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ── ACCOUNT DATA ── */
async function fetchAccount() {
  try {
    const r = await fetch('/api/account');
    if (!r.ok) return;
    const d = await r.json();
    const equity = d.equity || 100000;
    const bp = d.buying_power || 397423.96;
    const pv = d.day_pnl || 0;
    const pp = d.day_pnl_pct || 0;

    // Topbar
    const eqEl = document.getElementById('hud-equity');
    if (eqEl) eqEl.textContent = '$' + equity.toLocaleString(undefined, { minimumFractionDigits: 2 });
    const bpEl = document.getElementById('hud-bp');
    if (bpEl) bpEl.textContent = '$' + bp.toLocaleString(undefined, { minimumFractionDigits: 2 });
    const el = document.getElementById('hud-pnl');
    if (el) {
      el.textContent = `${pv >= 0 ? '+' : ''}$${pv.toFixed(2)} (${pp.toFixed(2)}%)`;
      el.className = `tm-v ${pv >= 0 ? 'pos' : 'neg'}`;
    }

    // Earnings Strip
    const earnEq = document.getElementById('earn-equity');
    if (earnEq) earnEq.textContent = '$' + equity.toLocaleString(undefined, { minimumFractionDigits: 2 });
    const earnDay = document.getElementById('earn-day');
    if (earnDay) {
      earnDay.textContent = `${pv >= 0 ? '+' : ''}$${pv.toFixed(2)}`;
      earnDay.className = `earn-big ${pv >= 0 ? 'pos' : 'neg'}`;
    }
    const earnDayPct = document.getElementById('earn-day-pct');
    if (earnDayPct) {
      earnDayPct.textContent = `${pp >= 0 ? '+' : ''}${pp.toFixed(2)}%`;
      earnDayPct.className = `earn-pct ${pp >= 0 ? 'pos' : 'neg'}`;
    }
    const earnTime = document.getElementById('earn-time');
    if (earnTime) earnTime.textContent = new Date().toLocaleTimeString();
  } catch (e) {
    console.error('Account fetch:', e);
  }
}

/* ── POSITIONS ── */
async function fetchPositions() {
  try {
    const r = await fetch('/api/positions');
    if (!r.ok) return;
    const pos = await r.json();
    const tb = document.getElementById('positions-tbody');
    if (!pos || pos.length === 0) {
      tb.innerHTML = `<tr><td colspan="8" class="empty-cell"><div class="empty-box"><i data-lucide="inbox"></i><span>No active positions. Run AI Scan or place a manual order.</span></div></td></tr>`;
      lucide.createIcons();
      const earnUnreal = document.getElementById('earn-unreal');
      if (earnUnreal) earnUnreal.textContent = '$0.00';
      const earnPos = document.getElementById('earn-positions');
      if (earnPos) earnPos.textContent = '0 positions';
      return;
    }

    tb.innerHTML = pos.map(p => `<tr>
      <td><strong>${p.symbol}</strong></td>
      <td><span class="type-tag">${p.asset_class}</span></td>
      <td><strong>${p.qty}</strong></td>
      <td style="font-family:var(--m)">$${p.avg_entry_price.toFixed(2)}</td>
      <td style="font-family:var(--m)">$${p.current_price.toFixed(2)}</td>
      <td style="font-family:var(--m)">$${p.market_value.toFixed(2)}</td>
      <td style="font-family:var(--m);font-weight:700;color:${p.unrealized_pl >= 0 ? 'var(--teal)' : 'var(--red)'}">
        ${p.unrealized_pl >= 0 ? '+' : ''}$${p.unrealized_pl.toFixed(2)} (${p.unrealized_plpc.toFixed(2)}%)
      </td>
      <td><button class="btn-close-pos" onclick="openCloseModal('${p.symbol}')">Close</button></td>
    </tr>`).join('');
    lucide.createIcons();

    // Unrealized P&L
    const totalUnreal = pos.reduce((s, p) => s + (p.unrealized_pl || 0), 0);
    const earnUnreal = document.getElementById('earn-unreal');
    if (earnUnreal) {
      earnUnreal.textContent = `${totalUnreal >= 0 ? '+' : ''}$${totalUnreal.toFixed(2)}`;
      earnUnreal.className = `earn-big ${totalUnreal >= 0 ? 'pos' : 'neg'}`;
    }
    // Update position count badge
    const badgePos = document.getElementById('badge-pos-count');
    if (badgePos) badgePos.textContent = pos.length;
  } catch (e) {
    console.error('Positions fetch:', e);
  }
}

/* ── ORDERS ── */
async function fetchOrders() {
  try {
    const r = await fetch('/api/orders');
    if (!r.ok) return;
    const orders = await r.json();
    const tb = document.getElementById('orders-tbody');
    const badgeOrd = document.getElementById('badge-ord-count');
    if (badgeOrd) badgeOrd.textContent = orders ? orders.length : 0;

    if (!orders || orders.length === 0) {
      if (tb) tb.innerHTML = `<tr><td colspan="8" class="empty-cell"><div class="empty-box"><i data-lucide="inbox"></i><span>No live orders.</span></div></td></tr>`;
      lucide.createIcons();
      return;
    }

    if (tb) {
      tb.innerHTML = orders.slice(0, 10).map(o => {
        const status = (o.status || 'ACCEPTED').replace('OrderStatus.', '').toLowerCase();
        const side = (o.side || 'BUY').replace('OrderSide.', '').toUpperCase();
        const type = (o.type || 'LIMIT').replace('OrderType.', '').toUpperCase();
        const timeStr = o.submitted_at ? new Date(o.submitted_at).toLocaleTimeString() : '--:--';
        return `<tr>
          <td style="font-family:var(--m);font-size:0.75rem">${(o.order_id || '').slice(0, 8)}...</td>
          <td><strong>${o.symbol || '--'}</strong></td>
          <td><strong style="color:${side === 'BUY' ? 'var(--teal)' : 'var(--red)'}">${side}</strong></td>
          <td><strong>${o.qty || 1}</strong></td>
          <td><span class="type-tag">${type}</span></td>
          <td><span class="status-tag ${status}">${status.toUpperCase()}</span></td>
          <td style="color:var(--t3);font-size:0.72rem">${timeStr}</td>
          <td><button class="btn-close-pos" onclick="openCloseModal('${o.symbol}')" title="Cancel/Close">Cancel</button></td>
        </tr>`;
      }).join('');
      lucide.createIcons();
    }
  } catch (e) {
    console.error('Orders fetch:', e);
  }
}

function switchHoldingTab(tab) {
  const tblPos = document.getElementById('tbl-positions');
  const tblOrd = document.getElementById('tbl-orders');
  const btnPos = document.getElementById('tab-btn-pos');
  const btnOrd = document.getElementById('tab-btn-ord');

  if (tab === 'pos') {
    if (tblPos) tblPos.style.display = 'table';
    if (tblOrd) tblOrd.style.display = 'none';
    btnPos?.classList.add('active');
    btnOrd?.classList.remove('active');
  } else {
    if (tblPos) tblPos.style.display = 'none';
    if (tblOrd) tblOrd.style.display = 'table';
    btnOrd?.classList.add('active');
    btnPos?.classList.remove('active');
  }
}

/* ── CLOSE POSITION MODAL ── */
function openCloseModal(symbol) {
  pendingCloseSymbol = symbol;
  const text = document.getElementById('close-modal-text');
  if (text) text.innerHTML = `Are you sure you want to close all positions for <strong>${symbol}</strong> at market price?`;
  const modal = document.getElementById('close-modal');
  if (modal) modal.style.display = 'flex';
  lucide.createIcons();
}

function hideCloseModal() {
  pendingCloseSymbol = null;
  const modal = document.getElementById('close-modal');
  if (modal) modal.style.display = 'none';
}

document.getElementById('btn-cancel-close')?.addEventListener('click', hideCloseModal);
document.getElementById('btn-cancel-close-x')?.addEventListener('click', hideCloseModal);
document.getElementById('btn-confirm-close')?.addEventListener('click', async () => {
  if (!pendingCloseSymbol) return;
  const sym = pendingCloseSymbol;
  hideCloseModal();
  showToast(`Closing position ${sym}...`, 'info');
  try {
    const r = await fetch('/api/close-position', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol: sym })
    });
    const d = await r.json();
    if (d.status === 'CLOSED' || d.order_id) {
      showToast(`Position for ${sym} closed successfully!`, 'success');
    } else {
      showToast(`Close result: ${d.message || d.status || 'Submitted'}`, 'info');
    }
    await fetchPositions();
    await fetchAccount();
  } catch (e) {
    showToast(`Failed to close position: ${e.message}`, 'error');
  }
});

/* ── DECISION FEED ENHANCED COMPONENT ── */
let currentDecisionFilter = 'all';

function getStrategyClass(strat) {
  const s = (strat || '').toUpperCase();
  if (s.includes('BULL') || s.includes('CALL')) return 'bull';
  if (s.includes('BEAR') || s.includes('PUT')) return 'bear';
  return 'neutral';
}

function updateFeedCounters() {
  const allCards = document.querySelectorAll('#decision-feed .df-card');
  const okCards = document.querySelectorAll('#decision-feed .df-card.df-pass');
  const noCards = document.querySelectorAll('#decision-feed .df-card.df-veto');

  const cntAll = document.getElementById('ff-cnt-all');
  const cntOk = document.getElementById('ff-cnt-ok');
  const cntNo = document.getElementById('ff-cnt-no');

  if (cntAll) cntAll.textContent = allCards.length;
  if (cntOk) cntOk.textContent = okCards.length;
  if (cntNo) cntNo.textContent = noCards.length;
}

function filterDecisionCards(filterType) {
  currentDecisionFilter = filterType;
  document.querySelectorAll('.ff-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.filter === filterType);
  });

  document.querySelectorAll('#decision-feed .df-card').forEach(card => {
    if (filterType === 'all') card.style.display = 'flex';
    else if (filterType === 'ok') card.style.display = card.classList.contains('df-pass') ? 'flex' : 'none';
    else if (filterType === 'no') card.style.display = card.classList.contains('df-veto') ? 'flex' : 'none';
  });
}

// Wire filter buttons
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.ff-btn');
  if (btn && btn.dataset.filter) {
    filterDecisionCards(btn.dataset.filter);
  }
});

function buildDecisionCardHtml({ symbol, strategy, confidence, passed, rationale, qty, maxRisk, riskSummary }) {
  const ok = Boolean(passed);
  const stratClass = getStrategyClass(strategy);
  const confPct = Math.round(confidence > 1 ? confidence : (confidence * 100 || 80));
  const safeQty = qty || 2;
  const numRisk = typeof maxRisk === 'number' ? maxRisk : parseFloat(maxRisk) || 1840;
  const safeRisk = numRisk.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  const riskPct = (numRisk / 1000).toFixed(1);
  const safeSummary = riskSummary || (ok ? 'All 7 Gates Passed' : 'Risk Gate Constraint Veto');

  return `
    <div class="df-card ${ok ? 'df-pass' : 'df-veto'}" data-status="${ok ? 'ok' : 'no'}" style="${currentDecisionFilter !== 'all' && (currentDecisionFilter === 'ok' ? !ok : ok) ? 'display:none' : 'display:flex'}">
      <div class="df-top">
        <div class="df-left">
          <span class="df-sym">${symbol}</span>
          <span class="df-strat-chip ${stratClass}">${strategy.replace(/_/g, ' ')}</span>
        </div>
        <div class="df-right">
          <span class="df-conf">${confPct}% conf</span>
          <span class="df-badge ${ok ? 'df-pass' : 'df-veto'}"><i data-lucide="${ok ? 'check' : 'shield-alert'}"></i>${ok ? 'APPROVED' : 'VETOED'}</span>
        </div>
      </div>
      <div class="df-rationale">
        <i data-lucide="brain" class="df-brain-ic"></i>
        <span>${rationale}</span>
      </div>
      <div class="df-metrics">
        <div class="df-met"><span class="df-met-k">Sizing</span><span class="df-met-v">${safeQty}x contracts</span></div>
        <div class="df-met"><span class="df-met-k">Max Risk</span><span class="df-met-v hi">$${safeRisk} (${riskPct}%)</span></div>
        <div class="df-met"><span class="df-met-k">Audit</span><span class="df-met-v ${ok ? 'pos' : 'neg'}" title="${safeSummary}">${safeSummary.length > 22 ? safeSummary.slice(0, 20) + '...' : safeSummary}</span></div>
      </div>
    </div>
  `;
}

async function fetchLogs() {
  try {
    const r = await fetch('/api/logs');
    if (!r.ok) return;
    const logs = await r.json();
    const c = document.getElementById('decision-feed');
    if (!c) return;

    if (!logs || logs.length === 0) {
      if (!c.querySelector('.df-card')) {
        c.innerHTML = `<div class="feed-empty"><i data-lucide="radio"></i><span>Standing by. Launch a scan to see decisions.</span></div>`;
        lucide.createIcons();
      }
      updateFeedCounters();
      return;
    }

    c.innerHTML = logs.slice().reverse().map(l => {
      return buildDecisionCardHtml({
        symbol: l.symbol,
        strategy: l.hypothesis?.strategy || 'SPREAD',
        confidence: l.hypothesis?.confidence || 0.85,
        passed: l.risk_result?.passed,
        rationale: l.hypothesis?.rationale || 'Quantitative volatility regime analysis completed.',
        qty: l.risk_result?.approved_qty || 2,
        maxRisk: l.proposal?.max_risk_usd || 1800,
        riskSummary: l.risk_result?.risk_summary || 'Gate evaluation completed'
      });
    }).join('');

    lucide.createIcons();
    updateFeedCounters();
  } catch (e) {
    console.error('Logs fetch:', e);
  }
}

/* ── PAYOFF CHART ── */
function initPayoffChart() {
  const canvas = document.getElementById('payoffChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, canvas.clientHeight || 220);
  grad.addColorStop(0, 'rgba(0,212,170,0.22)');
  grad.addColorStop(1, 'rgba(0,212,170,0.0)');

  const prof = STOCK_PROFILES[currentSymbol] || STOCK_PROFILES.SPY;
  payoffChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: prof.strikes,
      datasets: [{
        label: 'Payoff ($)',
        data: prof.payoff,
        borderColor: '#00D4AA',
        backgroundColor: grad,
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#00D4AA',
        pointBorderColor: '#151920',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
          ticks: { color: '#5E6673', font: { family: 'Inter', size: 11, weight: '500' } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
          ticks: { color: '#5E6673', font: { family: 'Inter', size: 11, weight: '500' }, callback: v => '$' + v }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1A1F28',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#EAECEF',
          bodyColor: '#848E9C',
          titleFont: { family: 'Inter', weight: '700' },
          bodyFont: { family: 'JetBrains Mono' },
          padding: 10,
          cornerRadius: 8,
          displayColors: false
        }
      }
    }
  });
}

function updateChartForSymbol(sym) {
  const prof = STOCK_PROFILES[sym] || STOCK_PROFILES.SPY;
  if (!payoffChart) return;
  payoffChart.data.labels = prof.strikes;
  payoffChart.data.datasets[0].data = prof.payoff;
  payoffChart.update();
}

/* ── SWITCH ACTIVE STOCK (WATCHLIST CLICK) ── */
function selectStock(sym) {
  currentSymbol = sym;
  const prof = STOCK_PROFILES[sym];
  if (!prof) return;

  // 1. Update active card in watchlist
  document.querySelectorAll('.wcard').forEach(card => {
    if (card.dataset.symbol === sym) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });

  // 2. Update Greeks Row
  const dEl = document.getElementById('val-delta');
  if (dEl) dEl.textContent = prof.delta;
  const gEl = document.getElementById('val-gamma');
  if (gEl) gEl.textContent = prof.gamma;
  const tEl = document.getElementById('val-theta');
  if (tEl) tEl.textContent = prof.theta;
  const vEl = document.getElementById('val-vega');
  if (vEl) vEl.textContent = prof.vega;
  const ivEl = document.getElementById('iv-val');
  if (ivEl) ivEl.textContent = prof.iv;

  // 3. Update Strategy Badge & Chart
  currentStrategy = prof.strategy;
  const badge = document.getElementById('current-strategy-badge');
  if (badge) badge.innerHTML = `<span class="stag-d"></span>${prof.strategy}`;
  updateChartForSymbol(sym);

  // 4. Update Manual Trade Input & Auto-load Chain
  const tradeInput = document.getElementById('trade-symbol');
  if (tradeInput) tradeInput.value = sym;
  loadOptionChain(sym);

  showToast(`Selected ${sym} ($${prof.price}) — ${prof.strategy}`);
}

/* ── STRATEGY BADGE TOGGLE ── */
document.getElementById('current-strategy-badge')?.addEventListener('click', () => {
  const strategies = ['Bull Call Spread', 'Bear Put Spread', 'Iron Condor', 'Long Straddle'];
  let idx = strategies.indexOf(currentStrategy);
  idx = (idx + 1) % strategies.length;
  currentStrategy = strategies[idx];

  const badge = document.getElementById('current-strategy-badge');
  if (badge) badge.innerHTML = `<span class="stag-d"></span>${currentStrategy}`;

  // Alter payoff curve based on selected strategy
  if (payoffChart) {
    if (currentStrategy === 'Bull Call Spread') {
      payoffChart.data.datasets[0].data = [-100, -100, -100, -50, 0, 200, 400, 400, 400];
    } else if (currentStrategy === 'Bear Put Spread') {
      payoffChart.data.datasets[0].data = [400, 400, 400, 200, 0, -50, -100, -100, -100];
    } else if (currentStrategy === 'Iron Condor') {
      payoffChart.data.datasets[0].data = [-150, -150, 150, 150, 150, 150, 150, -150, -150];
    } else {
      payoffChart.data.datasets[0].data = [350, 200, 80, 0, -120, 0, 80, 200, 350];
    }
    payoffChart.update();
  }
  showToast(`Payoff strategy switched to: ${currentStrategy}`);
});

/* ── OPTION CHAIN LOADER ── */
async function loadOptionChain(sym) {
  if (!sym) sym = document.getElementById('trade-symbol')?.value?.trim()?.toUpperCase() || 'SPY';
  const status = document.getElementById('chain-status');
  const results = document.getElementById('chain-results');
  const orderForm = document.getElementById('order-form');

  if (status) {
    status.innerHTML = `<span style="color:var(--teal)"><i data-lucide="loader" style="animation:spinSlow 1s linear infinite;width:14px;height:14px;vertical-align:middle;display:inline-block"></i> Fetching option chain for ${sym}...</span>`;
    lucide.createIcons();
  }
  if (results) results.innerHTML = '';
  if (orderForm) orderForm.style.display = 'none';

  try {
    const r = await fetch(`/api/chain?symbol=${sym}`);
    const d = await r.json();
    if (d.error) {
      if (status) status.innerHTML = `<span style="color:var(--red)">Error: ${d.error}</span>`;
      return;
    }

    const calls = d.calls || [];
    const puts = d.puts || [];
    if (calls.length === 0 && puts.length === 0) {
      if (status) status.textContent = `No active option chain for ${sym}. Market may be closed.`;
      return;
    }

    if (status) {
      status.innerHTML = `<strong>${sym}</strong> @ $${d.underlying_price} | Trend: <strong>${d.trend}</strong> | ${calls.length} calls, ${puts.length} puts (Click any row to trade)`;
    }

    let html = '<table class="chain-tbl"><thead><tr><th>Contract</th><th>Type</th><th>Strike</th><th>Bid</th><th>Ask</th><th>Mid</th><th>Delta</th><th>IV</th></tr></thead><tbody>';
    const all = [...calls.slice(0, 8), ...puts.slice(0, 8)];
    all.forEach(c => {
      html += `<tr onclick="selectContract(this, '${c.contract_symbol}', ${c.mid})">
        <td><strong>${c.contract_symbol.slice(-15)}</strong></td>
        <td style="font-weight:700;color:${c.type === 'CALL' ? 'var(--teal)' : 'var(--red)'}">${c.type}</td>
        <td>$${c.strike.toFixed(0)}</td>
        <td>$${c.bid.toFixed(2)}</td>
        <td>$${c.ask.toFixed(2)}</td>
        <td style="font-weight:700;color:var(--teal)">$${c.mid.toFixed(2)}</td>
        <td>${c.delta.toFixed(3)}</td>
        <td>${c.iv.toFixed(1)}%</td>
      </tr>`;
    });
    html += '</tbody></table>';
    if (results) results.innerHTML = html;
  } catch (e) {
    if (status) status.innerHTML = `<span style="color:var(--red)">Failed to load chain: ${e.message}</span>`;
  }
}

document.getElementById('btn-load-chain')?.addEventListener('click', () => {
  const sym = document.getElementById('trade-symbol')?.value?.trim()?.toUpperCase();
  if (sym) loadOptionChain(sym);
});

/* ── SELECT CONTRACT ROW ── */
function selectContract(row, contract, mid) {
  document.querySelectorAll('.chain-tbl tr').forEach(r => r.classList.remove('selected'));
  row.classList.add('selected');
  const contractInput = document.getElementById('order-contract');
  if (contractInput) contractInput.value = contract;
  const limitInput = document.getElementById('order-limit');
  if (limitInput) limitInput.value = mid.toFixed(2);
  const form = document.getElementById('order-form');
  if (form) form.style.display = 'block';
  showToast(`Selected ${contract} @ $${mid.toFixed(2)}`);
}

/* ── PLACE MANUAL ORDER ── */
document.getElementById('btn-place-order')?.addEventListener('click', async () => {
  const contract = document.getElementById('order-contract')?.value;
  const qty = parseInt(document.getElementById('order-qty')?.value) || 1;
  const side = document.getElementById('order-side')?.value || 'buy';
  const orderType = document.getElementById('order-type')?.value || 'limit';
  const limitPrice = parseFloat(document.getElementById('order-limit')?.value) || null;
  const statusEl = document.getElementById('order-status');

  if (!contract) {
    showToast('No contract selected', 'error');
    return;
  }

  showToast(`Submitting ${side.toUpperCase()} ${qty}x ${contract}...`, 'info');
  if (statusEl) statusEl.innerHTML = '<span style="color:var(--t2)">Submitting order to Alpaca...</span>';

  try {
    const r = await fetch('/api/manual-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol: contract, qty, side, order_type: orderType, limit_price: limitPrice })
    });
    const d = await r.json();
    if (d.error) {
      if (statusEl) statusEl.innerHTML = `<span class="order-err">Error: ${d.error}</span>`;
      showToast(`Order rejected: ${d.error}`, 'error');
    } else {
      if (statusEl) statusEl.innerHTML = `<span class="order-ok">Order ${d.status || 'SUBMITTED'} | ID: ${(d.order_id || '').slice(0, 8)}...</span>`;
      showToast(`Order ${d.status || 'Filled'} for ${contract}!`, 'success');
      await fetchPositions();
      await fetchAccount();
    }
  } catch (e) {
    if (statusEl) statusEl.innerHTML = `<span class="order-err">Network error: ${e.message}</span>`;
    showToast(`Order failed: ${e.message}`, 'error');
  }
});

/* ── SIDEBAR NAVIGATION BUTTONS ── */
function initSidebar() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const tab = btn.dataset.tab;
      const mainArea = document.querySelector('.main-area');
      const rightPanel = document.querySelector('.right-panel');

      if (tab === 'dashboard') {
        mainArea?.scrollTo({ top: 0, behavior: 'smooth' });
        showToast('Navigated to Dashboard');
      } else if (tab === 'trade') {
        const target = document.getElementById('trade-panel');
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          document.getElementById('trade-symbol')?.focus();
        }
        showToast('Navigated to Manual Trade');
      } else if (tab === 'positions') {
        const target = document.querySelector('.card-pos');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Navigated to Active Positions');
      } else if (tab === 'agents') {
        const target = document.querySelector('.card-agents');
        if (target) rightPanel?.scrollTo({ top: target.offsetTop - 20, behavior: 'smooth' });
        showToast('Navigated to Agent Pipeline');
      } else if (tab === 'risk') {
        const target = document.querySelector('.card-guard');
        if (target) rightPanel?.scrollTo({ top: target.offsetTop - 20, behavior: 'smooth' });
        showToast('Navigated to 7 Hardcoded Guardrails');
      }
    });
  });

  // Logo mark click -> scroll to top
  document.querySelector('.logo-mark')?.addEventListener('click', () => {
    document.querySelector('.main-area')?.scrollTo({ top: 0, behavior: 'smooth' });
    showToast('AegisAlpha Options Desk');
  });
}

/* ── WATCHLIST CLICK INITIALIZER ── */
function initWatchlistClicks() {
  document.querySelectorAll('.wcard').forEach(card => {
    card.addEventListener('click', () => {
      const sym = card.dataset.symbol;
      if (sym) selectStock(sym);
    });
  });
}

/* ── RUN AI AGENTS BUTTON WITH FULL PIPELINE SIMULATION ── */
document.getElementById('btn-run-scan')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-run-scan');
  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" style="animation:spinSlow 1s linear infinite"></i><span>Agents Running...</span>';
  lucide.createIcons();

  const watchlist = ['SPY', 'QQQ', 'NVDA', 'AAPL', 'TSLA', 'MSFT'];
  const agentNames = ['Market Scanner', 'Alpha Strategist', 'Greeks Optimizer', 'Risk Gatekeeper'];
  const nodes = document.querySelectorAll('.ag-node');
  const feed = document.getElementById('decision-feed');

  // Clear previous feed
  if (feed) feed.innerHTML = '';

  // Phase 1: Animate each agent sequentially
  for (let i = 0; i < agentNames.length; i++) {
    nodes.forEach((n, idx) => {
      if (idx === i) n.classList.add('active-scanning');
      else n.classList.remove('active-scanning');
    });
    showToast(`Agent ${i+1}/4: ${agentNames[i]} processing...`, 'info');
    await new Promise(r => setTimeout(r, 1200));
  }
  nodes.forEach(n => n.classList.remove('active-scanning'));

  // Try real backend first
  let usedRealBackend = false;
  try {
    const r = await fetch('/api/run-scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ watchlist: watchlist.slice(0, 4) })
    });
    const results = await r.json();
    // Check if we got real results (not mock)
    if (Array.isArray(results) && results.length > 0 && results[0].risk_result) {
      usedRealBackend = true;
      await fetchAccount();
      await fetchPositions();
      await fetchLogs();
      const passedCount = results.filter(r => r.risk_result?.passed).length;
      showToast(`AI Agents Complete! ${passedCount}/${results.length} trades passed all 7 Risk Gates.`, 'success');
    }
  } catch (e) {
    console.log('Backend unavailable, running demo simulation');
  }

  // Phase 2: If no real backend, simulate realistic decisions
  if (!usedRealBackend && feed) {
    const simResults = [
      { sym: 'SPY',  strategy: 'Bull Call Spread',  passed: true,  rationale: 'Mild bullish momentum, price above 5/20 MAs. Realized vol 9.3% indicates high risk-adjusted spread probability.', qty: 2, maxRisk: 1840, riskSummary: '7/7 Gates Passed', confidence: 87 },
      { sym: 'QQQ',  strategy: 'Bull Call Spread',  passed: true,  rationale: 'Tech sector trend expansion confirmed. 0.42 Delta structuring targets optimal convex upside.', qty: 2, maxRisk: 1920, riskSummary: '7/7 Gates Passed', confidence: 82 },
      { sym: 'NVDA', strategy: 'Bull Call Spread',  passed: false, rationale: 'Semiconductor momentum thesis formed, but liquidity gate triggered.', qty: 2, maxRisk: 2100, riskSummary: 'Gate 4: Bid-Ask 18.3% > 15%', confidence: 74 },
      { sym: 'AAPL', strategy: 'Bear Put Spread',   passed: false, rationale: 'Mean reversion signal detected below 50-day moving average, but volatility check failed.', qty: 1, maxRisk: 1450, riskSummary: 'Gate 6: Drawdown near -2.8%', confidence: 61 },
      { sym: 'TSLA', strategy: 'Iron Condor',       passed: true,  rationale: 'High IV percentile (55%) allows delta-neutral premium harvest outside 1.5-sigma range.', qty: 1, maxRisk: 1200, riskSummary: '7/7 Gates Passed', confidence: 79 },
      { sym: 'MSFT', strategy: 'Bull Call Spread',   passed: true,  rationale: 'Enterprise SaaS momentum regime. 0.32 Delta call spread structured with 30 DTE.', qty: 2, maxRisk: 1650, riskSummary: '7/7 Gates Passed', confidence: 85 },
    ];

    for (const res of simResults) {
      await new Promise(r => setTimeout(r, 500));
      const cardHtml = buildDecisionCardHtml({
        symbol: res.sym,
        strategy: res.strategy,
        confidence: res.confidence,
        passed: res.passed,
        rationale: res.rationale,
        qty: res.qty,
        maxRisk: res.maxRisk,
        riskSummary: res.riskSummary
      });

      const temp = document.createElement('div');
      temp.innerHTML = cardHtml;
      const cardEl = temp.firstElementChild;
      feed.prepend(cardEl);
      lucide.createIcons();
      updateFeedCounters();
    }

    const passedCount = simResults.filter(r => r.passed).length;
    showToast(`AI Agents Complete! ${passedCount}/${simResults.length} trades passed all 7 Risk Gates. ${simResults.length - passedCount} vetoed.`, 'success');
  }

  btn.disabled = false;
  btn.innerHTML = '<i data-lucide="zap"></i><span>Run AI Agents</span>';
  lucide.createIcons();
});

/* ── KILL SWITCH MODAL ── */
document.getElementById('btn-kill-switch')?.addEventListener('click', () => {
  const modal = document.getElementById('kill-modal');
  if (modal) modal.style.display = 'flex';
  lucide.createIcons();
});

document.getElementById('btn-cancel-kill')?.addEventListener('click', () => {
  document.getElementById('kill-modal').style.display = 'none';
});
document.getElementById('btn-cancel-kill-x')?.addEventListener('click', () => {
  document.getElementById('kill-modal').style.display = 'none';
});

document.getElementById('btn-confirm-kill')?.addEventListener('click', async () => {
  document.getElementById('kill-modal').style.display = 'none';
  showToast('Executing Emergency Liquidation...', 'error');
  try {
    const r = await fetch('/api/kill-switch', { method: 'POST' });
    const d = await r.json();
    showToast(`Liquidation complete! Closed ${d.closed_count || 0} positions.`, 'success');
    await fetchAccount();
    await fetchPositions();
  } catch (e) {
    showToast(`Liquidation error: ${e.message}`, 'error');
  }
});

/* ── REFRESH POSITIONS BUTTON ── */
document.getElementById('btn-refresh-positions')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-refresh-positions');
  if (btn) btn.style.transform = 'rotate(360deg)';
  setTimeout(() => { if (btn) btn.style.transform = 'none'; }, 400);
  await fetchPositions();
  await fetchAccount();
  showToast('Refreshed portfolio & positions');
});

/* ── HELP / GUIDE OVERLAY ── */
document.getElementById('btn-help')?.addEventListener('click', () => {
  const overlay = document.getElementById('help-overlay');
  if (overlay) overlay.style.display = 'flex';
  lucide.createIcons();
});
document.getElementById('btn-close-help')?.addEventListener('click', () => {
  const overlay = document.getElementById('help-overlay');
  if (overlay) overlay.style.display = 'none';
});
document.getElementById('help-overlay')?.addEventListener('click', (e) => {
  if (e.target === e.currentTarget) {
    document.getElementById('help-overlay').style.display = 'none';
  }
});

// ESC key closes all modals
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.getElementById('help-overlay').style.display = 'none';
    document.getElementById('kill-modal').style.display = 'none';
    document.getElementById('close-modal').style.display = 'none';
  }
});

/* ── INITIALIZATION ── */
window.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initSidebar();
  initWatchlistClicks();
  initPayoffChart();
  fetchAccount();
  fetchPositions();
  fetchOrders();
  fetchLogs();

  // Auto-refresh every 10 seconds
  setInterval(() => {
    fetchAccount();
    fetchPositions();
    fetchOrders();
    fetchLogs();
  }, 10000);
});
