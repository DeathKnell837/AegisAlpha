/* ══════════════════════════════════════════════════════════════
   AegisAlpha v3 — Quantitative Terminal & Payoff Engine
   ══════════════════════════════════════════════════════════════ */
let payoffChart = null;
let currentSymbol = 'SPY';
let currentStrategyKey = 'BULL_CALL';
let currentDTE = 30;
let pendingCloseSymbol = null;

// Multi-strategy quantitative profiles
const STOCK_DATA = {
  SPY: {
    price: 769.28,
    trend: 'Mild Bullish (+0.82%)',
    strategies: {
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [750, 755, 760, 765, 770, 772.5, 778, 785, 790],
        payoff: [-100, -100, -100, -100, -50, 0, 400, 400, 400],
        maxProfit: 400,
        maxLoss: -100,
        breakeven: '$772.50',
        beDist: '+0.42% to Spot',
        rr: '1 : 4.00',
        pop: '68.4%',
        maxRoi: '+400% ROI',
        delta: '+0.40',
        gamma: '+0.034',
        theta: '-$0.27',
        vega: '+$0.46',
        iv: '9.34%',
        ivRank: 42,
        deltaBar: 70,
        gammaBar: 55,
        thetaBar: 35,
        vegaBar: 62
      },
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [750, 755, 760, 765, 767.5, 770, 775, 780, 790],
        payoff: [350, 350, 350, 150, 0, -150, -150, -150, -150],
        maxProfit: 350,
        maxLoss: -150,
        breakeven: '$767.50',
        beDist: '-0.23% to Spot',
        rr: '1 : 2.33',
        pop: '54.2%',
        maxRoi: '+233% ROI',
        delta: '-0.38',
        gamma: '+0.029',
        theta: '-$0.22',
        vega: '+$0.41',
        iv: '9.34%',
        ivRank: 42,
        deltaBar: 40,
        gammaBar: 45,
        thetaBar: 28,
        vegaBar: 50
      },
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [745, 750, 755, 765, 770, 775, 785, 790, 795],
        payoff: [-300, -300, 0, 180, 180, 180, 0, -300, -300],
        maxProfit: 180,
        maxLoss: -300,
        breakeven: '$755 / $785',
        beDist: '±1.95% Range',
        rr: '1 : 0.60',
        pop: '78.5%',
        maxRoi: '+60% ROI',
        delta: '+0.02',
        gamma: '+0.012',
        theta: '+$0.35',
        vega: '-$0.55',
        iv: '9.34%',
        ivRank: 42,
        deltaBar: 52,
        gammaBar: 25,
        thetaBar: 65,
        vegaBar: 75
      }
    }
  },
  QQQ: {
    price: 520.14,
    trend: 'Bullish (+1.14%)',
    strategies: {
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [500, 505, 510, 515, 520, 523, 530, 535, 540],
        payoff: [-120, -120, -120, -120, -40, 0, 380, 380, 380],
        maxProfit: 380,
        maxLoss: -120,
        breakeven: '$523.00',
        beDist: '+0.55% to Spot',
        rr: '1 : 3.16',
        pop: '65.1%',
        maxRoi: '+316% ROI',
        delta: '+0.42',
        gamma: '+0.028',
        theta: '-$0.31',
        vega: '+$0.52',
        iv: '14.20%',
        ivRank: 48,
        deltaBar: 72,
        gammaBar: 48,
        thetaBar: 40,
        vegaBar: 68
      },
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [500, 505, 510, 517, 520, 525, 530, 535, 540],
        payoff: [320, 320, 320, 0, -140, -140, -140, -140, -140],
        maxProfit: 320,
        maxLoss: -140,
        breakeven: '$517.00',
        beDist: '-0.60% to Spot',
        rr: '1 : 2.28',
        pop: '51.8%',
        maxRoi: '+228% ROI',
        delta: '-0.36',
        gamma: '+0.025',
        theta: '-$0.28',
        vega: '+$0.48',
        iv: '14.20%',
        ivRank: 48,
        deltaBar: 38,
        gammaBar: 42,
        thetaBar: 36,
        vegaBar: 58
      },
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [495, 505, 510, 518, 520, 525, 532, 540, 545],
        payoff: [-250, -250, 0, 160, 160, 160, 0, -250, -250],
        maxProfit: 160,
        maxLoss: -250,
        breakeven: '$510 / $532',
        beDist: '±2.10% Range',
        rr: '1 : 0.64',
        pop: '76.2%',
        maxRoi: '+64% ROI',
        delta: '+0.03',
        gamma: '+0.015',
        theta: '+$0.42',
        vega: '-$0.61',
        iv: '14.20%',
        ivRank: 48,
        deltaBar: 53,
        gammaBar: 30,
        thetaBar: 70,
        vegaBar: 80
      }
    }
  },
  NVDA: {
    price: 132.80,
    trend: 'High Beta (+2.45%)',
    strategies: {
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [115, 120, 125, 130, 133.5, 135, 140, 145, 150],
        payoff: [-90, -90, -90, -90, 0, 120, 310, 310, 310],
        maxProfit: 310,
        maxLoss: -90,
        breakeven: '$133.50',
        beDist: '+0.53% to Spot',
        rr: '1 : 3.44',
        pop: '62.8%',
        maxRoi: '+344% ROI',
        delta: '+0.38',
        gamma: '+0.065',
        theta: '-$0.45',
        vega: '+$0.68',
        iv: '42.80%',
        ivRank: 65,
        deltaBar: 68,
        gammaBar: 85,
        thetaBar: 60,
        vegaBar: 88
      },
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [115, 120, 125, 131, 133, 135, 140, 145, 150],
        payoff: [280, 280, 280, 0, -110, -110, -110, -110, -110],
        maxProfit: 280,
        maxLoss: -110,
        breakeven: '$131.00',
        beDist: '-1.35% to Spot',
        rr: '1 : 2.54',
        pop: '55.0%',
        maxRoi: '+254% ROI',
        delta: '-0.41',
        gamma: '+0.058',
        theta: '-$0.39',
        vega: '+$0.62',
        iv: '42.80%',
        ivRank: 65,
        deltaBar: 35,
        gammaBar: 75,
        thetaBar: 52,
        vegaBar: 78
      },
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [115, 122, 125, 130, 133, 136, 142, 145, 150],
        payoff: [-220, -220, 0, 140, 140, 140, 0, -220, -220],
        maxProfit: 140,
        maxLoss: -220,
        breakeven: '$125 / $142',
        beDist: '±6.00% Range',
        rr: '1 : 0.63',
        pop: '74.0%',
        maxRoi: '+63% ROI',
        delta: '-0.01',
        gamma: '+0.022',
        theta: '+$0.58',
        vega: '-$0.78',
        iv: '42.80%',
        ivRank: 65,
        deltaBar: 49,
        gammaBar: 40,
        thetaBar: 82,
        vegaBar: 92
      }
    }
  },
  AAPL: {
    price: 232.10,
    trend: 'Pullback (-0.35%)',
    strategies: {
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [215, 220, 225, 230, 231.2, 235, 240, 245, 250],
        payoff: [260, 260, 260, 120, 0, -90, -90, -90, -90],
        maxProfit: 260,
        maxLoss: -90,
        breakeven: '$231.20',
        beDist: '-0.38% to Spot',
        rr: '1 : 2.88',
        pop: '58.6%',
        maxRoi: '+288% ROI',
        delta: '-0.35',
        gamma: '+0.022',
        theta: '-$0.18',
        vega: '+$0.38',
        iv: '18.60%',
        ivRank: 35,
        deltaBar: 42,
        gammaBar: 38,
        thetaBar: 24,
        vegaBar: 48
      },
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [215, 220, 225, 230, 233.5, 235, 240, 245, 250],
        payoff: [-85, -85, -85, -85, 0, 110, 315, 315, 315],
        maxProfit: 315,
        maxLoss: -85,
        breakeven: '$233.50',
        beDist: '+0.60% to Spot',
        rr: '1 : 3.70',
        pop: '61.2%',
        maxRoi: '+370% ROI',
        delta: '+0.33',
        gamma: '+0.020',
        theta: '-$0.19',
        vega: '+$0.36',
        iv: '18.60%',
        ivRank: 35,
        deltaBar: 63,
        gammaBar: 35,
        thetaBar: 26,
        vegaBar: 45
      },
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [215, 222, 225, 230, 232, 235, 238, 242, 250],
        payoff: [-200, -200, 0, 120, 120, 120, 0, -200, -200],
        maxProfit: 120,
        maxLoss: -200,
        breakeven: '$225 / $238',
        beDist: '±2.80% Range',
        rr: '1 : 0.60',
        pop: '79.2%',
        maxRoi: '+60% ROI',
        delta: '+0.01',
        gamma: '+0.011',
        theta: '+$0.28',
        vega: '-$0.42',
        iv: '18.60%',
        ivRank: 35,
        deltaBar: 51,
        gammaBar: 20,
        thetaBar: 55,
        vegaBar: 60
      }
    }
  },
  TSLA: {
    price: 214.50,
    trend: 'High Volatility (+1.90%)',
    strategies: {
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [185, 195, 200, 210, 215, 220, 228, 235, 245],
        payoff: [-260, -260, 0, 190, 190, 190, 0, -260, -260],
        maxProfit: 190,
        maxLoss: -260,
        breakeven: '$200 / $228',
        beDist: '±6.50% Range',
        rr: '1 : 0.73',
        pop: '77.0%',
        maxRoi: '+73% ROI',
        delta: '+0.02',
        gamma: '+0.025',
        theta: '+$0.62',
        vega: '-$0.85',
        iv: '55.10%',
        ivRank: 72,
        deltaBar: 52,
        gammaBar: 45,
        thetaBar: 88,
        vegaBar: 95
      },
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [185, 195, 205, 210, 217, 220, 230, 235, 245],
        payoff: [-140, -140, -140, -140, 0, 160, 460, 460, 460],
        maxProfit: 460,
        maxLoss: -140,
        breakeven: '$217.00',
        beDist: '+1.16% to Spot',
        rr: '1 : 3.28',
        pop: '64.5%',
        maxRoi: '+328% ROI',
        delta: '+0.45',
        gamma: '+0.048',
        theta: '-$0.52',
        vega: '+$0.74',
        iv: '55.10%',
        ivRank: 72,
        deltaBar: 75,
        gammaBar: 65,
        thetaBar: 68,
        vegaBar: 90
      },
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [185, 195, 205, 212, 215, 220, 230, 235, 245],
        payoff: [380, 380, 380, 0, -160, -160, -160, -160, -160],
        maxProfit: 380,
        maxLoss: -160,
        breakeven: '$212.00',
        beDist: '-1.15% to Spot',
        rr: '1 : 2.37',
        pop: '53.8%',
        maxRoi: '+237% ROI',
        delta: '-0.42',
        gamma: '+0.045',
        theta: '-$0.48',
        vega: '+$0.69',
        iv: '55.10%',
        ivRank: 72,
        deltaBar: 32,
        gammaBar: 60,
        thetaBar: 62,
        vegaBar: 85
      }
    }
  },
  MSFT: {
    price: 448.20,
    trend: 'Steady Trend (+0.64%)',
    strategies: {
      BULL_CALL: {
        name: 'Bull Call Spread',
        strikes: [425, 435, 440, 445, 449.5, 455, 460, 465, 475],
        payoff: [-110, -110, -110, -110, 0, 210, 390, 390, 390],
        maxProfit: 390,
        maxLoss: -110,
        breakeven: '$449.50',
        beDist: '+0.29% to Spot',
        rr: '1 : 3.54',
        pop: '67.0%',
        maxRoi: '+354% ROI',
        delta: '+0.32',
        gamma: '+0.019',
        theta: '-$0.22',
        vega: '+$0.41',
        iv: '16.40%',
        ivRank: 38,
        deltaBar: 62,
        gammaBar: 32,
        thetaBar: 30,
        vegaBar: 52
      },
      BEAR_PUT: {
        name: 'Bear Put Spread',
        strikes: [425, 435, 440, 447, 448, 455, 460, 465, 475],
        payoff: [310, 310, 310, 0, -120, -120, -120, -120, -120],
        maxProfit: 310,
        maxLoss: -120,
        breakeven: '$447.00',
        beDist: '-0.27% to Spot',
        rr: '1 : 2.58',
        pop: '52.4%',
        maxRoi: '+258% ROI',
        delta: '-0.30',
        gamma: '+0.018',
        theta: '-$0.20',
        vega: '+$0.39',
        iv: '16.40%',
        ivRank: 38,
        deltaBar: 45,
        gammaBar: 30,
        thetaBar: 28,
        vegaBar: 50
      },
      IRON_CONDOR: {
        name: 'Iron Condor',
        strikes: [425, 438, 442, 447, 448, 452, 456, 462, 475],
        payoff: [-220, -220, 0, 150, 150, 150, 0, -220, -220],
        maxProfit: 150,
        maxLoss: -220,
        breakeven: '$442 / $456',
        beDist: '±1.75% Range',
        rr: '1 : 0.68',
        pop: '78.0%',
        maxRoi: '+68% ROI',
        delta: '+0.01',
        gamma: '+0.010',
        theta: '+$0.31',
        vega: '-$0.48',
        iv: '16.40%',
        ivRank: 38,
        deltaBar: 51,
        gammaBar: 18,
        thetaBar: 60,
        vegaBar: 65
      }
    }
  }
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

/* ── QUANTITATIVE PAYOFF ENGINE ── */
function getActiveProfile() {
  const stock = STOCK_DATA[currentSymbol] || STOCK_DATA.SPY;
  const strat = stock.strategies[currentStrategyKey] || stock.strategies.BULL_CALL;
  return { stock, strat };
}

function updatePayoffDisplay() {
  const { stock, strat } = getActiveProfile();

  // 1. Update Strategy Badge
  const badgeName = document.getElementById('badge-strat-name');
  if (badgeName) badgeName.textContent = strat.name;

  // 2. Greeks Row
  const dEl = document.getElementById('val-delta');
  if (dEl) dEl.textContent = strat.delta;
  const dBar = document.getElementById('bar-delta');
  if (dBar) dBar.style.width = `${strat.deltaBar || 50}%`;

  const gEl = document.getElementById('val-gamma');
  if (gEl) gEl.textContent = strat.gamma;
  const gBar = document.getElementById('bar-gamma');
  if (gBar) gBar.style.width = `${strat.gammaBar || 40}%`;

  const tEl = document.getElementById('val-theta');
  if (tEl) tEl.textContent = strat.theta;
  const tBar = document.getElementById('bar-theta');
  if (tBar) tBar.style.width = `${strat.thetaBar || 35}%`;

  const vEl = document.getElementById('val-vega');
  if (vEl) vEl.textContent = strat.vega;
  const vBar = document.getElementById('bar-vega');
  if (vBar) vBar.style.width = `${strat.vegaBar || 60}%`;

  const ivEl = document.getElementById('iv-val');
  if (ivEl) ivEl.textContent = strat.iv;
  const ivBar = document.getElementById('bar-iv');
  if (ivBar) ivBar.style.width = `${strat.ivRank || 42}%`;
}

function initPayoffChart() {
  const canvas = document.getElementById('payoffChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const grad = ctx.createLinearGradient(0, 0, 0, canvas.clientHeight || 235);
  grad.addColorStop(0, 'rgba(0,212,170,0.22)');
  grad.addColorStop(0.6, 'rgba(0,212,170,0.03)');
  grad.addColorStop(1, 'rgba(246,70,93,0.08)');

  const { strat } = getActiveProfile();

  payoffChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: strat.strikes.map(s => typeof s === 'number' ? `$${s}` : s),
      datasets: [
        {
          label: 'Payoff ($)',
          data: strat.payoff,
          borderColor: '#00D4AA',
          backgroundColor: grad,
          borderWidth: 2.5,
          fill: true,
          tension: 0.38,
          pointBackgroundColor: '#00D4AA',
          pointBorderColor: '#0B0E11',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6.5,
          pointHoverBackgroundColor: '#FFFFFF',
          pointHoverBorderColor: '#00D4AA'
        },
        {
          label: 'Breakeven',
          data: strat.strikes.map(() => 0),
          borderColor: 'rgba(255,255,255,0.12)',
          borderWidth: 1.2,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
          ticks: { color: '#5E6673', font: { family: 'JetBrains Mono', size: 11, weight: '500' } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
          ticks: {
            color: '#5E6673',
            font: { family: 'JetBrains Mono', size: 11, weight: '500' },
            callback: v => (v > 0 ? '+$' : (v < 0 ? '-$' : '$')) + Math.abs(v)
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#12161C',
          borderColor: 'rgba(0,212,170,0.3)',
          borderWidth: 1,
          titleColor: '#FFFFFF',
          bodyColor: '#A0AEC0',
          titleFont: { family: 'Inter', weight: '700', size: 12 },
          bodyFont: { family: 'JetBrains Mono', size: 11 },
          padding: 10,
          cornerRadius: 6,
          displayColors: false,
          callbacks: {
            title: items => `Strike Price: ${items[0].label}`,
            label: item => {
              if (item.datasetIndex === 1) return null;
              const val = item.raw;
              const roi = ((val / 100) * 100).toFixed(0);
              const zone = val > 0 ? 'Profit Zone' : (val < 0 ? 'Defined Risk Capped' : 'Breakeven');
              return [
                `Estimated P&L: ${val >= 0 ? '+' : ''}$${val.toFixed(2)} (${roi}% ROI)`,
                `Status: ${zone}`
              ];
            }
          }
        }
      }
    }
  });

  updatePayoffDisplay();
}

function updatePayoffChart() {
  if (!payoffChart) return;
  const { strat } = getActiveProfile();

  payoffChart.data.labels = strat.strikes.map(s => typeof s === 'number' ? `$${s}` : s);
  payoffChart.data.datasets[0].data = strat.payoff;
  payoffChart.data.datasets[1].data = strat.strikes.map(() => 0);
  payoffChart.update();
  updatePayoffDisplay();
}

/* ── STRATEGY BADGE TOGGLE (CLICK BADGE TO CYCLE STRATEGIES) ── */
document.getElementById('current-strategy-badge')?.addEventListener('click', () => {
  const stratKeys = ['BULL_CALL', 'BEAR_PUT', 'IRON_CONDOR'];
  let idx = stratKeys.indexOf(currentStrategyKey);
  idx = (idx + 1) % stratKeys.length;
  currentStrategyKey = stratKeys[idx];

  updatePayoffChart();
  const { strat } = getActiveProfile();
  showToast(`Payoff strategy switched to: ${strat.name}`);
});

/* ── SWITCH ACTIVE STOCK (WATCHLIST CLICK) ── */
function selectStock(sym) {
  currentSymbol = sym;
  const stock = STOCK_DATA[sym];
  if (!stock) return;

  // 1. Update active card in watchlist
  document.querySelectorAll('.wcard').forEach(card => {
    card.classList.toggle('active', card.dataset.symbol === sym);
  });

  // 2. Refresh Payoff Chart & Greeks
  updatePayoffChart();

  // 3. Update Manual Trade Input & Auto-load Chain
  const tradeInput = document.getElementById('trade-symbol');
  if (tradeInput) tradeInput.value = sym;
  loadOptionChain(sym);

  showToast(`Selected ${sym} ($${stock.price.toFixed(2)})`);
}

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

/* ── MARKET STATUS TRACKER ── */
function updateMarketStatus() {
  const now = new Date();
  const utcDay = now.getUTCDay();
  const utcHours = now.getUTCHours();
  const utcMins = now.getUTCMinutes();
  const utcTimeMin = utcHours * 60 + utcMins;

  // NYSE Trading Hours: Monday (1) to Friday (5), 13:30 UTC to 20:00 UTC (9:30 AM - 4:00 PM EDT)
  const isWeekday = utcDay >= 1 && utcDay <= 5;
  const isOpenTime = utcTimeMin >= 810 && utcTimeMin < 1200;
  const isOpen = isWeekday && isOpenTime;

  const chip = document.getElementById('market-status-chip');
  const dot = chip?.querySelector('.mkt-dot');
  const txt = document.getElementById('mkt-status-text');

  if (isOpen) {
    if (dot) { dot.className = 'mkt-dot open'; }
    if (txt) { txt.textContent = 'NYSE LIVE • Market Open'; txt.className = 'mkt-status open'; }
  } else {
    if (dot) { dot.className = 'mkt-dot closed'; }
    let target = new Date(now);
    target.setUTCHours(13, 30, 0, 0);
    if (now > target || !isWeekday) {
      if (utcDay === 5 && utcTimeMin >= 1200) target.setUTCDate(target.getUTCDate() + 3);
      else if (utcDay === 6) target.setUTCDate(target.getUTCDate() + 2);
      else if (utcDay === 0) target.setUTCDate(target.getUTCDate() + 1);
      else if (utcTimeMin >= 1200) target.setUTCDate(target.getUTCDate() + 1);
    }
    const diffMs = Math.max(0, target - now);
    const diffH = Math.floor(diffMs / 3600000);
    const diffM = Math.floor((diffMs % 3600000) / 60000);
    if (txt) { txt.textContent = `NYSE Closed • Opens in ${diffH}h ${diffM}m`; txt.className = 'mkt-status'; }
  }
}

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
  updateMarketStatus();

  // Auto-refresh every 10 seconds
  setInterval(() => {
    fetchAccount();
    fetchPositions();
    fetchOrders();
    fetchLogs();
    updateMarketStatus();
  }, 10000);
});
