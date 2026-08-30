#!/usr/bin/env python3
"""Build v3 Quantum dashboard - fixes + manual trading + design polish."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
WEB.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
# INDEX.HTML - v3 with manual trading panel
# ══════════════════════════════════════════════════════════════
HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AegisAlpha | Autonomous AI Options Desk</title>
  <link rel="stylesheet" href="index.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

  <!-- LEFT SIDEBAR -->
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="logo-mark">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="url(#lg)" stroke-width="1.8" fill="none"/>
          <path d="M14 8L20 11V17L14 20L8 17V11L14 8Z" fill="url(#lg)" opacity="0.2"/>
          <path d="M14 10L18 12.5V17L14 19.5L10 17V12.5L14 10Z" fill="url(#lg)" opacity="0.55"/>
          <defs><linearGradient id="lg" x1="2" y1="2" x2="26" y2="26"><stop stop-color="#00D4AA"/><stop offset="1" stop-color="#00B4D8"/></linearGradient></defs>
        </svg>
      </div>
      <nav class="sidebar-nav">
        <button class="nav-btn active" data-tab="dashboard" data-tooltip="Dashboard"><i data-lucide="layout-dashboard"></i></button>
        <button class="nav-btn" data-tab="trade" data-tooltip="Manual Trade"><i data-lucide="arrow-left-right"></i></button>
        <button class="nav-btn" data-tab="positions" data-tooltip="Positions"><i data-lucide="briefcase"></i></button>
        <button class="nav-btn" data-tab="agents" data-tooltip="AI Agents"><i data-lucide="cpu"></i></button>
        <button class="nav-btn" data-tab="risk" data-tooltip="Risk Gates"><i data-lucide="shield-check"></i></button>
      </nav>
    </div>
    <div class="sidebar-bottom">
      <div class="sidebar-avatar"><span>A</span></div>
    </div>
  </aside>

  <!-- MAIN SHELL -->
  <div class="shell">

    <!-- TOP BAR -->
    <header class="topbar">
      <div class="topbar-left">
        <div class="topbar-brand">
          <span class="brand-name">Aegis<span class="brand-hi">Alpha</span></span>
          <span class="brand-pipe"></span>
          <span class="brand-tag">OPTIONS DESK</span>
        </div>
        <div class="topbar-chip">
          <span class="chip-dot"></span>
          <span class="chip-label">Paper</span>
          <span class="chip-id">PA3PL5AZ85K6</span>
          <span class="chip-tier">Lvl 3</span>
        </div>
      </div>
      <div class="topbar-metrics">
        <div class="tm"><span class="tm-l">Equity</span><span class="tm-v" id="hud-equity">$100,000.00</span></div>
        <div class="tm-sep"></div>
        <div class="tm"><span class="tm-l">Buying Power</span><span class="tm-v hi" id="hud-bp">$397,423.96</span></div>
        <div class="tm-sep"></div>
        <div class="tm"><span class="tm-l">Day P&amp;L</span><span class="tm-v pos" id="hud-pnl">+$0.00 (0.00%)</span></div>
      </div>
      <div class="topbar-actions">
        <button id="btn-run-scan" class="btn-scan"><i data-lucide="zap"></i><span>AI Scan</span></button>
        <button id="btn-kill-switch" class="btn-kill" title="Emergency Liquidation"><i data-lucide="octagon-x"></i></button>
      </div>
    </header>

    <!-- CONTENT ZONE -->
    <div class="content-zone">

      <!-- MAIN AREA -->
      <main class="main-area">

        <!-- WATCHLIST -->
        <section class="watchlist" id="watchlist-container">
          <div class="wcard active" data-symbol="SPY">
            <div class="wc-r1"><span class="wc-s">SPY</span><span class="wc-ch up">+0.82%</span></div>
            <span class="wc-p">$769.28</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,15 10,12 20,14 30,8 40,10 50,5 60,7" fill="none" stroke="#00D4AA" stroke-width="1.5"/></svg>
          </div>
          <div class="wcard" data-symbol="QQQ">
            <div class="wc-r1"><span class="wc-s">QQQ</span><span class="wc-ch up">+1.14%</span></div>
            <span class="wc-p">$520.14</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,16 10,14 20,12 30,10 40,6 50,8 60,4" fill="none" stroke="#00D4AA" stroke-width="1.5"/></svg>
          </div>
          <div class="wcard" data-symbol="NVDA">
            <div class="wc-r1"><span class="wc-s">NVDA</span><span class="wc-ch up">+2.45%</span></div>
            <span class="wc-p">$132.80</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,18 10,14 20,16 30,10 40,8 50,4 60,3" fill="none" stroke="#00D4AA" stroke-width="1.5"/></svg>
          </div>
          <div class="wcard" data-symbol="AAPL">
            <div class="wc-r1"><span class="wc-s">AAPL</span><span class="wc-ch dn">-0.35%</span></div>
            <span class="wc-p">$232.10</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,6 10,8 20,7 30,12 40,14 50,13 60,16" fill="none" stroke="#F6465D" stroke-width="1.5"/></svg>
          </div>
          <div class="wcard" data-symbol="TSLA">
            <div class="wc-r1"><span class="wc-s">TSLA</span><span class="wc-ch up">+1.90%</span></div>
            <span class="wc-p">$214.50</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,17 10,14 20,16 30,9 40,12 50,6 60,5" fill="none" stroke="#00D4AA" stroke-width="1.5"/></svg>
          </div>
          <div class="wcard" data-symbol="MSFT">
            <div class="wc-r1"><span class="wc-s">MSFT</span><span class="wc-ch up">+0.64%</span></div>
            <span class="wc-p">$448.20</span>
            <svg class="wc-sv" viewBox="0 0 60 20"><polyline points="0,14 10,12 20,13 30,10 40,11 50,8 60,9" fill="none" stroke="#00D4AA" stroke-width="1.5"/></svg>
          </div>
        </section>

        <!-- HERO CHART -->
        <section class="card card-chart">
          <div class="card-hd">
            <div><h2 class="card-t">Options Payoff Curve</h2><span class="card-st">Defined-risk P&L across strike horizons</span></div>
            <div class="stag" id="current-strategy-badge"><span class="stag-d"></span>Bull Call Spread</div>
          </div>
          <div class="chart-box"><canvas id="payoffChart"></canvas></div>
        </section>

        <!-- GREEKS -->
        <section class="greeks-row">
          <div class="gcard"><span class="gc-l">Delta</span><span class="gc-v pos" id="val-delta">+0.40</span><span class="gc-d">Directional Bias</span></div>
          <div class="gcard"><span class="gc-l">Gamma</span><span class="gc-v hi" id="val-gamma">+0.034</span><span class="gc-d">Convexity Speed</span></div>
          <div class="gcard"><span class="gc-l">Theta</span><span class="gc-v neg" id="val-theta">-0.27</span><span class="gc-d">Time Decay/Day</span></div>
          <div class="gcard"><span class="gc-l">Vega</span><span class="gc-v pur" id="val-vega">+0.46</span><span class="gc-d">IV Sensitivity</span></div>
          <div class="gcard"><span class="gc-l">Implied Vol</span><span class="gc-v hi" id="iv-val">9.34%</span><div class="gc-bar"><div class="gc-fill" style="width:42%"></div></div></div>
        </section>

        <!-- MANUAL TRADE PANEL -->
        <section class="card trade-panel" id="trade-panel">
          <div class="card-hd">
            <div>
              <h2 class="card-t">Manual Trade</h2>
              <span class="card-st">Search options chains and place orders manually</span>
            </div>
          </div>
          <div class="trade-form">
            <div class="tf-row">
              <div class="tf-group">
                <label class="tf-label">Symbol</label>
                <input type="text" id="trade-symbol" class="tf-input" placeholder="SPY" value="SPY">
              </div>
              <button id="btn-load-chain" class="btn-chain"><i data-lucide="search"></i><span>Load Chain</span></button>
            </div>
            <div id="chain-status" class="chain-status"></div>
            <div id="chain-results" class="chain-results"></div>
            <div class="tf-order" id="order-form" style="display:none">
              <div class="tf-row">
                <div class="tf-group">
                  <label class="tf-label">Contract</label>
                  <input type="text" id="order-contract" class="tf-input" readonly>
                </div>
                <div class="tf-group sm">
                  <label class="tf-label">Qty</label>
                  <input type="number" id="order-qty" class="tf-input" value="1" min="1" max="10">
                </div>
                <div class="tf-group sm">
                  <label class="tf-label">Side</label>
                  <select id="order-side" class="tf-input">
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                  </select>
                </div>
                <div class="tf-group sm">
                  <label class="tf-label">Type</label>
                  <select id="order-type" class="tf-input">
                    <option value="limit">Limit</option>
                    <option value="market">Market</option>
                  </select>
                </div>
                <div class="tf-group sm">
                  <label class="tf-label">Limit $</label>
                  <input type="number" id="order-limit" class="tf-input" step="0.01" placeholder="0.00">
                </div>
              </div>
              <button id="btn-place-order" class="btn-order"><i data-lucide="send"></i><span>Place Order</span></button>
              <div id="order-status" class="order-status"></div>
            </div>
          </div>
        </section>

        <!-- POSITIONS TABLE -->
        <section class="card card-pos">
          <div class="card-hd">
            <div><h2 class="card-t">Active Positions</h2><span class="card-st">Real-time holdings on PA3PL5AZ85K6</span></div>
            <button id="btn-refresh-positions" class="btn-ghost" title="Refresh"><i data-lucide="rotate-cw"></i></button>
          </div>
          <div class="tbl-wrap">
            <table class="tbl">
              <thead><tr><th>Position</th><th>Type</th><th>Qty</th><th>Avg Price</th><th>Mark</th><th>Mkt Value</th><th>P&amp;L</th><th></th></tr></thead>
              <tbody id="positions-tbody">
                <tr><td colspan="8" class="empty-cell"><div class="empty-box"><i data-lucide="inbox"></i><span>No active positions. Run AI Scan or place a manual order.</span></div></td></tr>
              </tbody>
            </table>
          </div>
        </section>

      </main>

      <!-- RIGHT PANEL -->
      <aside class="right-panel">

        <div class="card card-agents">
          <div class="card-hd"><div><h2 class="card-t">Agent Pipeline</h2><span class="card-st">Multi-Agent Intelligence</span></div></div>
          <div class="agent-flow">
            <div class="ag-node"><div class="ag-ic teal"><i data-lucide="activity"></i></div><div class="ag-bd"><div class="ag-r"><span class="ag-nm">Market Scanner</span><span class="ag-bg teal">ONLINE</span></div><span class="ag-dt">IEX Bars &amp; 30-Day Realized Vol</span></div></div>
            <div class="ag-line"></div>
            <div class="ag-node"><div class="ag-ic amber"><i data-lucide="brain-circuit"></i></div><div class="ag-bd"><div class="ag-r"><span class="ag-nm">Alpha Strategist</span><span class="ag-bg amber">Qwen-2.5-7B</span></div><span class="ag-dt">Volatility Regime &amp; Convexity</span></div></div>
            <div class="ag-line"></div>
            <div class="ag-node"><div class="ag-ic purple"><i data-lucide="binary"></i></div><div class="ag-bd"><div class="ag-r"><span class="ag-nm">Greeks Engine</span><span class="ag-bg purple">Indicative</span></div><span class="ag-dt">0.40/0.20 Delta Structuring</span></div></div>
            <div class="ag-line"></div>
            <div class="ag-node"><div class="ag-ic green"><i data-lucide="shield-check"></i></div><div class="ag-bd"><div class="ag-r"><span class="ag-nm">Risk Gatekeeper</span><span class="ag-bg green">ZERO-LLM</span></div><span class="ag-dt">7 Deterministic Constraints</span></div></div>
          </div>
        </div>

        <div class="card card-feed">
          <div class="card-hd"><div><h2 class="card-t">Decision Feed</h2><span class="card-st">Live risk audit verdicts</span></div></div>
          <div id="decision-feed" class="feed-scroll">
            <div class="feed-empty"><i data-lucide="radio"></i><span>Standing by. Launch a scan to see decisions.</span></div>
          </div>
        </div>

        <div class="card card-guard">
          <div class="guard-hd"><i data-lucide="lock"></i><span>7 Hardcoded Guardrails</span></div>
          <div class="guard-list">
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Defined-Risk Spreads Only</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Max 2% Risk per Position</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Max 20% Options Exposure</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Bid-Ask Slippage &lt;15%</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Duration Window 5-45 DTE</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>-3% Daily Drawdown Breaker</span></div>
            <div class="gr"><i data-lucide="check-circle-2"></i><span>Dynamic Unit Risk Sizing</span></div>
          </div>
        </div>

      </aside>
    </div>
  </div>

  <script src="index.js"></script>
</body>
</html>
'''

(WEB / "index.html").write_text(HTML, encoding="utf-8")
print("[OK] web/index.html")

# ══════════════════════════════════════════════════════════════
# INDEX.CSS - v3 with manual trading + design polish
# ══════════════════════════════════════════════════════════════
CSS = r'''/* ═══════════════════════════════════════════
   AegisAlpha v3 — Quantum Dark Dashboard
   ═══════════════════════════════════════════ */
:root {
  --bg: #0B0E11; --bg2: #0F1218; --bg3: #151920; --bg4: #1A1F28; --bg5: #1E2330;
  --bd: rgba(255,255,255,0.06); --bd2: rgba(255,255,255,0.10); --bd-hi: rgba(0,212,170,0.35);
  --teal: #00D4AA; --teal-d: rgba(0,212,170,0.12); --teal-g: rgba(0,212,170,0.25);
  --red: #F6465D; --red-d: rgba(246,70,93,0.12);
  --amber: #F0B90B; --amber-d: rgba(240,185,11,0.12);
  --purple: #9B51E0; --purple-d: rgba(155,81,224,0.12);
  --blue: #2D9CDB;
  --t1: #EAECEF; --t2: #848E9C; --t3: #5E6673;
  --f: 'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  --m: 'JetBrains Mono',monospace;
  --r1: 12px; --r2: 8px; --r3: 6px; --rp: 100px;
  --sw: 64px; --rw: 340px; --th: 56px;
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--t1);font-family:var(--f);display:flex;min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased}

/* SIDEBAR */
.sidebar{position:fixed;left:0;top:0;bottom:0;width:var(--sw);background:var(--bg2);border-right:1px solid var(--bd);display:flex;flex-direction:column;justify-content:space-between;align-items:center;padding:20px 0;z-index:200}
.sidebar-top{display:flex;flex-direction:column;align-items:center;gap:28px}
.logo-mark{width:40px;height:40px;display:flex;align-items:center;justify-content:center;cursor:pointer}
.logo-mark svg{transition:filter .3s}.logo-mark:hover svg{filter:drop-shadow(0 0 10px var(--teal))}
.sidebar-nav{display:flex;flex-direction:column;gap:4px}
.nav-btn{width:40px;height:40px;background:0;border:0;border-radius:var(--r2);color:var(--t3);display:flex;align-items:center;justify-content:center;cursor:pointer;position:relative;transition:all .2s}
.nav-btn i{width:20px;height:20px}
.nav-btn:hover{color:var(--t2);background:rgba(255,255,255,.04)}
.nav-btn.active{color:var(--teal);background:var(--teal-d)}
.nav-btn.active::before{content:'';position:absolute;left:-12px;top:50%;transform:translateY(-50%);width:3px;height:20px;background:var(--teal);border-radius:0 3px 3px 0}
.nav-btn::after{content:attr(data-tooltip);position:absolute;left:calc(100% + 14px);top:50%;transform:translateY(-50%);background:var(--bg5);color:var(--t1);font-size:.7rem;font-weight:600;padding:5px 10px;border-radius:var(--r3);white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .15s;border:1px solid var(--bd);z-index:999}
.nav-btn:hover::after{opacity:1}
.sidebar-bottom{display:flex;flex-direction:column;align-items:center}
.sidebar-avatar{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--teal),var(--blue));display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:800;color:#0B0E11}

/* SHELL */
.shell{margin-left:var(--sw);flex:1;display:flex;flex-direction:column;min-height:100vh}

/* TOPBAR */
.topbar{height:var(--th);background:var(--bg2);border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:100}
.topbar-left{display:flex;align-items:center;gap:16px}
.topbar-brand{display:flex;align-items:center;gap:8px}
.brand-name{font-size:1rem;font-weight:800;letter-spacing:-.4px}
.brand-hi{color:var(--teal)}
.brand-pipe{width:1px;height:14px;background:var(--bd)}
.brand-tag{font-size:.6rem;font-weight:700;letter-spacing:1.5px;color:var(--t3);text-transform:uppercase}
.topbar-chip{display:flex;align-items:center;gap:7px;background:rgba(255,255,255,.025);border:1px solid var(--bd);padding:3px 10px;border-radius:var(--rp);font-size:.72rem}
.chip-dot{width:6px;height:6px;border-radius:50%;background:var(--teal);box-shadow:0 0 8px var(--teal);animation:pulseDot 2s infinite}
.chip-label{color:var(--t2);font-weight:500}
.chip-id{font-family:var(--m);font-weight:600;color:var(--t1);font-size:.7rem}
.chip-tier{background:var(--amber-d);color:var(--amber);padding:1px 5px;border-radius:var(--r3);font-size:.62rem;font-weight:700}
.topbar-metrics{display:flex;align-items:center;gap:14px}
.tm{display:flex;flex-direction:column;gap:1px}
.tm-l{font-size:.62rem;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.4px}
.tm-v{font-family:var(--m);font-size:.85rem;font-weight:700}
.tm-v.hi{color:var(--teal)}.tm-v.pos{color:var(--teal)}.tm-v.neg{color:var(--red)}
.tm-sep{width:1px;height:26px;background:var(--bd)}
.topbar-actions{display:flex;align-items:center;gap:8px}
.btn-scan{display:flex;align-items:center;gap:5px;background:var(--teal);color:#0B0E11;border:0;padding:7px 14px;border-radius:var(--r2);font-size:.78rem;font-weight:700;font-family:var(--f);cursor:pointer;transition:all .2s}
.btn-scan i{width:14px;height:14px}
.btn-scan:hover{background:#00E6B8;box-shadow:0 0 20px var(--teal-g)}
.btn-scan:disabled{opacity:.5;cursor:not-allowed}
.btn-kill{width:34px;height:34px;background:0;border:1px solid rgba(246,70,93,.2);border-radius:var(--r2);color:var(--red);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s}
.btn-kill i{width:15px;height:15px}
.btn-kill:hover{background:var(--red-d);border-color:var(--red)}

/* CONTENT ZONE */
.content-zone{display:flex;flex:1;overflow:hidden}
.main-area{flex:1;padding:18px 22px;display:flex;flex-direction:column;gap:14px;overflow-y:auto;min-width:0}

/* WATCHLIST */
.watchlist{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}
.watchlist::-webkit-scrollbar{height:3px}.watchlist::-webkit-scrollbar-track{background:0}.watchlist::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
.wcard{min-width:130px;flex-shrink:0;background:var(--bg3);border:1px solid var(--bd);border-radius:var(--r2);padding:10px 12px 6px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:3px}
.wcard:hover{border-color:var(--bd2);background:var(--bg4)}
.wcard.active{border-color:var(--bd-hi);background:rgba(0,212,170,.03)}
.wc-r1{display:flex;justify-content:space-between;align-items:center}
.wc-s{font-size:.78rem;font-weight:800}
.wc-ch{font-size:.65rem;font-weight:700;padding:1px 4px;border-radius:var(--r3)}
.wc-ch.up{color:var(--teal);background:var(--teal-d)}
.wc-ch.dn{color:var(--red);background:var(--red-d)}
.wc-p{font-family:var(--m);font-size:.85rem;font-weight:600}
.wc-sv{width:100%;height:18px;opacity:.5}

/* CARDS */
.card{background:var(--bg3);border:1px solid var(--bd);border-radius:var(--r1);padding:18px;transition:border-color .2s}
.card:hover{border-color:var(--bd2)}
.card-hd{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px}
.card-t{font-size:.88rem;font-weight:700}
.card-st{font-size:.7rem;color:var(--t3)}
.stag{display:flex;align-items:center;gap:5px;font-size:.7rem;font-weight:700;color:var(--teal);background:var(--teal-d);padding:3px 9px;border-radius:var(--rp)}
.stag-d{width:5px;height:5px;border-radius:50%;background:var(--teal);box-shadow:0 0 6px var(--teal)}
.card-chart{padding:18px 18px 10px}
.chart-box{height:220px;position:relative}

/* GREEKS */
.greeks-row{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.gcard{background:var(--bg3);border:1px solid var(--bd);border-radius:var(--r2);padding:12px;display:flex;flex-direction:column;gap:2px;transition:border-color .2s}
.gcard:hover{border-color:var(--bd2)}
.gc-l{font-size:.65rem;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.3px}
.gc-v{font-family:var(--m);font-size:1.2rem;font-weight:700}
.gc-v.pos{color:var(--teal)}.gc-v.hi{color:var(--teal)}.gc-v.neg{color:var(--red)}.gc-v.pur{color:var(--purple)}
.gc-d{font-size:.62rem;color:var(--t3)}
.gc-bar{height:3px;background:rgba(255,255,255,.05);border-radius:2px;margin-top:5px;overflow:hidden}
.gc-fill{height:100%;background:linear-gradient(90deg,var(--teal),var(--amber));border-radius:2px;transition:width .5s}

/* MANUAL TRADE PANEL */
.trade-panel{border:1px solid rgba(0,212,170,.15)}
.tf-row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
.tf-group{display:flex;flex-direction:column;gap:3px;flex:1;min-width:100px}
.tf-group.sm{flex:0 0 90px;min-width:70px}
.tf-label{font-size:.65rem;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.3px}
.tf-input{background:var(--bg4);border:1px solid var(--bd);border-radius:var(--r3);color:var(--t1);font-family:var(--m);font-size:.8rem;padding:7px 10px;outline:none;transition:border-color .2s;width:100%}
.tf-input:focus{border-color:var(--teal)}
.tf-input::placeholder{color:var(--t3)}
select.tf-input{font-family:var(--f);cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%235E6673' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center;padding-right:24px}
.btn-chain{display:flex;align-items:center;gap:5px;background:var(--bg5);border:1px solid var(--bd2);color:var(--t1);padding:7px 14px;border-radius:var(--r2);font-size:.78rem;font-weight:600;font-family:var(--f);cursor:pointer;transition:all .2s;white-space:nowrap}
.btn-chain i{width:14px;height:14px}
.btn-chain:hover{background:rgba(255,255,255,.08);border-color:var(--teal)}
.chain-status{font-size:.75rem;color:var(--t2);padding:6px 0;min-height:24px}
.chain-results{max-height:200px;overflow-y:auto;margin-bottom:8px}
.chain-results::-webkit-scrollbar{width:3px}.chain-results::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
.chain-tbl{width:100%;border-collapse:collapse;font-size:.72rem}
.chain-tbl th{padding:6px 8px;text-align:left;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.3px;font-size:.62rem;border-bottom:1px solid var(--bd);position:sticky;top:0;background:var(--bg3)}
.chain-tbl td{padding:5px 8px;border-bottom:1px solid rgba(255,255,255,.03);color:var(--t2);font-family:var(--m);font-size:.72rem}
.chain-tbl tr:hover{background:rgba(255,255,255,.02)}
.chain-tbl tr{cursor:pointer}
.chain-tbl tr.selected{background:var(--teal-d);border-left:2px solid var(--teal)}
.tf-order{margin-top:10px;padding-top:10px;border-top:1px solid var(--bd)}
.btn-order{display:flex;align-items:center;gap:5px;background:var(--teal);color:#0B0E11;border:0;padding:8px 18px;border-radius:var(--r2);font-size:.78rem;font-weight:700;font-family:var(--f);cursor:pointer;transition:all .2s;margin-top:10px}
.btn-order i{width:14px;height:14px}
.btn-order:hover{background:#00E6B8;box-shadow:0 0 16px var(--teal-g)}
.order-status{font-size:.75rem;margin-top:6px;padding:6px 0;min-height:20px}
.order-ok{color:var(--teal)}.order-err{color:var(--red)}

/* TABLE */
.tbl-wrap{overflow-x:auto}
.tbl{width:100%;border-collapse:collapse;text-align:left}
.tbl th{padding:9px 12px;font-size:.65rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid var(--bd)}
.tbl td{padding:10px 12px;font-size:.8rem;color:var(--t2);border-bottom:1px solid rgba(255,255,255,.03)}
.tbl tbody tr:hover{background:rgba(255,255,255,.02)}
.tbl td strong{color:var(--t1);font-weight:700}
.empty-cell{text-align:center}
.empty-box{display:flex;flex-direction:column;align-items:center;gap:7px;padding:28px;color:var(--t3)}
.empty-box i{width:26px;height:26px;opacity:.4}
.empty-box span{font-size:.75rem}
.btn-ghost{width:28px;height:28px;background:0;border:1px solid var(--bd);border-radius:var(--r3);color:var(--t3);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s}
.btn-ghost i{width:13px;height:13px}
.btn-ghost:hover{color:var(--t2);border-color:var(--bd2)}
.btn-close-pos{background:0;border:1px solid rgba(246,70,93,.2);color:var(--red);padding:3px 7px;border-radius:var(--r3);font-size:.65rem;font-weight:600;font-family:var(--f);cursor:pointer;transition:all .2s}
.btn-close-pos:hover{background:var(--red-d)}
.type-tag{display:inline-block;font-size:.62rem;font-weight:700;padding:2px 5px;border-radius:var(--r3);background:var(--amber-d);color:var(--amber)}

/* RIGHT PANEL */
.right-panel{width:var(--rw);flex-shrink:0;border-left:1px solid var(--bd);padding:18px 14px;display:flex;flex-direction:column;gap:12px;overflow-y:auto;background:rgba(15,18,24,.4)}
.agent-flow{display:flex;flex-direction:column}
.ag-node{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:var(--r2);transition:background .2s}
.ag-node:hover{background:rgba(255,255,255,.02)}
.ag-line{width:2px;height:12px;background:var(--bd);margin-left:21px}
.ag-ic{width:32px;height:32px;border-radius:var(--r2);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ag-ic i{width:16px;height:16px}
.ag-ic.teal{background:var(--teal-d);color:var(--teal)}
.ag-ic.amber{background:var(--amber-d);color:var(--amber)}
.ag-ic.purple{background:var(--purple-d);color:var(--purple)}
.ag-ic.green{background:rgba(0,212,170,.12);color:var(--teal)}
.ag-bd{flex:1;min-width:0}
.ag-r{display:flex;justify-content:space-between;align-items:center;gap:6px}
.ag-nm{font-size:.78rem;font-weight:700}
.ag-bg{font-size:.58rem;font-weight:700;padding:2px 5px;border-radius:var(--r3);letter-spacing:.2px}
.ag-bg.teal{background:var(--teal-d);color:var(--teal)}
.ag-bg.amber{background:var(--amber-d);color:var(--amber)}
.ag-bg.purple{background:var(--purple-d);color:var(--purple)}
.ag-bg.green{background:rgba(0,212,170,.12);color:var(--teal)}
.ag-dt{font-size:.65rem;color:var(--t3);margin-top:1px}
.feed-scroll{display:flex;flex-direction:column;gap:8px;max-height:280px;overflow-y:auto}
.feed-scroll::-webkit-scrollbar{width:3px}.feed-scroll::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
.fe{background:rgba(255,255,255,.02);border:1px solid var(--bd);border-radius:var(--r2);padding:10px;display:flex;flex-direction:column;gap:6px}
.fe.ok{border-left:3px solid var(--teal)}.fe.no{border-left:3px solid var(--red)}
.fe-hd{display:flex;justify-content:space-between;align-items:center}
.fe-sym{font-size:.8rem;font-weight:800}
.fe-bg{font-size:.6rem;font-weight:700;padding:2px 6px;border-radius:var(--rp)}
.fe-bg.ok{background:var(--teal-d);color:var(--teal)}.fe-bg.no{background:var(--red-d);color:var(--red)}
.fe-rat{font-size:.72rem;color:var(--t2);line-height:1.35}
.fe-aud{background:rgba(0,0,0,.2);border-radius:var(--r3);padding:6px 8px;font-size:.65rem;font-family:var(--m);color:var(--t3);display:flex;flex-direction:column;gap:2px}
.feed-empty{display:flex;flex-direction:column;align-items:center;gap:7px;padding:24px 10px;color:var(--t3);font-size:.72rem;text-align:center}
.feed-empty i{width:20px;height:20px;animation:spinSlow 12s linear infinite;opacity:.35}
.card-guard{padding:12px 14px}
.guard-hd{display:flex;align-items:center;gap:7px;margin-bottom:8px}
.guard-hd i{width:13px;height:13px;color:var(--teal)}
.guard-hd span{font-size:.75rem;font-weight:700;color:var(--teal)}
.guard-list{display:flex;flex-direction:column;gap:5px}
.gr{display:flex;align-items:center;gap:6px;font-size:.7rem;color:var(--t2)}
.gr i{width:12px;height:12px;color:var(--teal);flex-shrink:0;opacity:.65}

/* ANIMATIONS */
@keyframes pulseDot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.75)}}
@keyframes spinSlow{from{transform:rotate(0)}to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.card,.wcard,.gcard{animation:fadeUp .35s ease both}
.wcard:nth-child(1){animation-delay:0s}.wcard:nth-child(2){animation-delay:.04s}.wcard:nth-child(3){animation-delay:.08s}.wcard:nth-child(4){animation-delay:.12s}.wcard:nth-child(5){animation-delay:.16s}.wcard:nth-child(6){animation-delay:.2s}
.gcard:nth-child(1){animation-delay:.08s}.gcard:nth-child(2){animation-delay:.12s}.gcard:nth-child(3){animation-delay:.16s}.gcard:nth-child(4){animation-delay:.2s}.gcard:nth-child(5){animation-delay:.24s}

/* SCROLLBAR */
::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-track{background:0}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.07);border-radius:4px}::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.13)}

/* RESPONSIVE */
@media(max-width:1200px){.right-panel{width:280px}.greeks-row{grid-template-columns:repeat(3,1fr)}}
@media(max-width:900px){.sidebar{display:none}.shell{margin-left:0}.content-zone{flex-direction:column}.right-panel{width:100%;border-left:0;border-top:1px solid var(--bd)}.greeks-row{grid-template-columns:repeat(2,1fr)}.topbar-metrics{display:none}}
'''

(WEB / "index.css").write_text(CSS, encoding="utf-8")
print("[OK] web/index.css")

# ══════════════════════════════════════════════════════════════
# INDEX.JS - v3 with closePos, manual trading, chain loading
# ══════════════════════════════════════════════════════════════
JS = r'''/* AegisAlpha v3 — Dashboard + Manual Trading */
let payoffChart = null;

/* ── ACCOUNT ── */
async function fetchAccount() {
  try {
    const r = await fetch('/api/account');
    if (!r.ok) return;
    const d = await r.json();
    document.getElementById('hud-equity').textContent = '$' + (d.equity||100000).toLocaleString(undefined,{minimumFractionDigits:2});
    document.getElementById('hud-bp').textContent = '$' + (d.buying_power||397423.96).toLocaleString(undefined,{minimumFractionDigits:2});
    const pv = d.day_pnl||0, pp = d.day_pnl_pct||0;
    const el = document.getElementById('hud-pnl');
    el.textContent = `${pv>=0?'+':''}$${pv.toFixed(2)} (${pp.toFixed(2)}%)`;
    el.className = `tm-v ${pv>=0?'pos':'neg'}`;
  } catch(e) { console.error('Account:',e); }
}

/* ── POSITIONS ── */
async function fetchPositions() {
  try {
    const r = await fetch('/api/positions');
    if (!r.ok) return;
    const pos = await r.json();
    const tb = document.getElementById('positions-tbody');
    if (!pos||pos.length===0) {
      tb.innerHTML = `<tr><td colspan="8" class="empty-cell"><div class="empty-box"><i data-lucide="inbox"></i><span>No active positions. Run AI Scan or place a manual order.</span></div></td></tr>`;
      lucide.createIcons(); return;
    }
    tb.innerHTML = pos.map(p => `<tr>
      <td><strong>${p.symbol}</strong></td>
      <td><span class="type-tag">${p.asset_class}</span></td>
      <td><strong>${p.qty}</strong></td>
      <td style="font-family:var(--m)">$${p.avg_entry_price.toFixed(2)}</td>
      <td style="font-family:var(--m)">$${p.current_price.toFixed(2)}</td>
      <td style="font-family:var(--m)">$${p.market_value.toFixed(2)}</td>
      <td style="font-family:var(--m);font-weight:700;color:${p.unrealized_pl>=0?'var(--teal)':'var(--red)'}">
        ${p.unrealized_pl>=0?'+':''}$${p.unrealized_pl.toFixed(2)} (${p.unrealized_plpc.toFixed(2)}%)
      </td>
      <td><button class="btn-close-pos" onclick="closePos('${p.symbol}')">Close</button></td>
    </tr>`).join('');
    lucide.createIcons();
  } catch(e) { console.error('Positions:',e); }
}

/* ── CLOSE POSITION (was missing!) ── */
async function closePos(symbol) {
  if (!confirm(`Close all positions for ${symbol}?`)) return;
  try {
    const r = await fetch('/api/close-position', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({symbol})
    });
    const d = await r.json();
    if (d.status === 'CLOSED') {
      await fetchPositions();
      await fetchAccount();
    } else {
      alert('Close failed: ' + (d.message || 'Unknown error'));
    }
  } catch(e) {
    console.error('Close position error:', e);
    alert('Failed to close position: ' + e.message);
  }
}

/* ── DECISION FEED ── */
async function fetchLogs() {
  try {
    const r = await fetch('/api/logs');
    if (!r.ok) return;
    const logs = await r.json();
    const c = document.getElementById('decision-feed');
    if (!logs||logs.length===0) {
      c.innerHTML = `<div class="feed-empty"><i data-lucide="radio"></i><span>Standing by. Launch a scan to see decisions.</span></div>`;
      lucide.createIcons(); return;
    }
    c.innerHTML = logs.slice().reverse().map(l => {
      const ok = l.risk_result?.passed;
      return `<div class="fe ${ok?'ok':'no'}">
        <div class="fe-hd"><span class="fe-sym">${l.symbol} &bull; ${l.hypothesis.strategy}</span><span class="fe-bg ${ok?'ok':'no'}">${ok?'Approved':'Vetoed'}</span></div>
        <p class="fe-rat">${l.hypothesis.rationale}</p>
        <div class="fe-aud">
          <div><strong>Sizing:</strong> ${l.risk_result.approved_qty} contracts | <strong>Max Risk:</strong> $${l.proposal.max_risk_usd.toFixed(2)}</div>
          <div style="color:${ok?'var(--teal)':'var(--red)'}">${l.risk_result.risk_summary}</div>
        </div>
      </div>`;
    }).join('');
    lucide.createIcons();
  } catch(e) { console.error('Logs:',e); }
}

/* ── CHART ── */
function initPayoffChart() {
  const ctx = document.getElementById('payoffChart').getContext('2d');
  const grad = ctx.createLinearGradient(0,0,0,ctx.canvas.clientHeight||220);
  grad.addColorStop(0,'rgba(0,212,170,0.22)');
  grad.addColorStop(1,'rgba(0,212,170,0.0)');
  payoffChart = new Chart(ctx, {
    type:'line',
    data:{
      labels:[750,755,760,765,770,773,778,785,790],
      datasets:[{label:'Payoff ($)',data:[-100,-100,-100,-100,-50,0,400,400,400],borderColor:'#00D4AA',backgroundColor:grad,borderWidth:2.5,fill:true,tension:.35,pointBackgroundColor:'#00D4AA',pointBorderColor:'#151920',pointBorderWidth:2,pointRadius:4,pointHoverRadius:6}]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:'index',intersect:false},
      scales:{
        x:{grid:{color:'rgba(255,255,255,.03)',drawBorder:false},ticks:{color:'#5E6673',font:{family:'Inter',size:11,weight:'500'}}},
        y:{grid:{color:'rgba(255,255,255,.03)',drawBorder:false},ticks:{color:'#5E6673',font:{family:'Inter',size:11,weight:'500'},callback:v=>'$'+v}}
      },
      plugins:{
        legend:{display:false},
        tooltip:{backgroundColor:'#1A1F28',borderColor:'rgba(255,255,255,.1)',borderWidth:1,titleColor:'#EAECEF',bodyColor:'#848E9C',titleFont:{family:'Inter',weight:'700'},bodyFont:{family:'JetBrains Mono'},padding:10,cornerRadius:8,displayColors:false}
      }
    }
  });
}

/* ── MANUAL TRADING: LOAD OPTION CHAIN ── */
document.getElementById('btn-load-chain').addEventListener('click', async () => {
  const sym = document.getElementById('trade-symbol').value.trim().toUpperCase();
  if (!sym) return;
  const status = document.getElementById('chain-status');
  const results = document.getElementById('chain-results');
  status.textContent = 'Loading option chain for ' + sym + '...';
  status.className = 'chain-status';
  results.innerHTML = '';
  document.getElementById('order-form').style.display = 'none';

  try {
    const r = await fetch(`/api/chain?symbol=${sym}`);
    const d = await r.json();
    if (d.error) { status.textContent = 'Error: ' + d.error; return; }

    const calls = d.calls || [];
    const puts = d.puts || [];
    if (calls.length === 0 && puts.length === 0) {
      status.textContent = 'No options found for ' + sym + '. Market may be closed.';
      return;
    }

    status.innerHTML = `<strong>${sym}</strong> @ $${d.underlying_price} | Trend: ${d.trend} | ${calls.length} calls, ${puts.length} puts`;

    let html = '<table class="chain-tbl"><thead><tr><th>Contract</th><th>Type</th><th>Strike</th><th>Bid</th><th>Ask</th><th>Mid</th><th>Delta</th><th>IV</th></tr></thead><tbody>';
    const all = [...calls.slice(0,8), ...puts.slice(0,8)];
    all.forEach(c => {
      html += `<tr onclick="selectContract(this, '${c.contract_symbol}', ${c.mid})" data-contract="${c.contract_symbol}" data-mid="${c.mid}">
        <td>${c.contract_symbol.slice(-15)}</td>
        <td style="color:${c.type==='CALL'?'var(--teal)':'var(--red)'}">${c.type}</td>
        <td>$${c.strike.toFixed(0)}</td>
        <td>$${c.bid.toFixed(2)}</td>
        <td>$${c.ask.toFixed(2)}</td>
        <td>$${c.mid.toFixed(2)}</td>
        <td>${c.delta.toFixed(3)}</td>
        <td>${c.iv.toFixed(1)}%</td>
      </tr>`;
    });
    html += '</tbody></table>';
    results.innerHTML = html;
  } catch(e) {
    status.textContent = 'Network error: ' + e.message;
    console.error('Chain load error:', e);
  }
});

/* ── SELECT CONTRACT FROM CHAIN ── */
function selectContract(row, contract, mid) {
  document.querySelectorAll('.chain-tbl tr').forEach(r => r.classList.remove('selected'));
  row.classList.add('selected');
  document.getElementById('order-contract').value = contract;
  document.getElementById('order-limit').value = mid.toFixed(2);
  document.getElementById('order-form').style.display = 'block';
}

/* ── PLACE MANUAL ORDER ── */
document.getElementById('btn-place-order').addEventListener('click', async () => {
  const contract = document.getElementById('order-contract').value;
  const qty = parseInt(document.getElementById('order-qty').value) || 1;
  const side = document.getElementById('order-side').value;
  const orderType = document.getElementById('order-type').value;
  const limitPrice = parseFloat(document.getElementById('order-limit').value) || null;
  const statusEl = document.getElementById('order-status');

  if (!contract) { statusEl.innerHTML = '<span class="order-err">No contract selected</span>'; return; }

  statusEl.textContent = 'Placing order...';
  try {
    const r = await fetch('/api/manual-order', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ symbol: contract, qty, side, order_type: orderType, limit_price: limitPrice })
    });
    const d = await r.json();
    if (d.error) {
      statusEl.innerHTML = `<span class="order-err">Error: ${d.error}</span>`;
    } else {
      statusEl.innerHTML = `<span class="order-ok">Order ${d.status} | ID: ${d.order_id.slice(0,8)}...</span>`;
      await fetchPositions();
      await fetchAccount();
    }
  } catch(e) {
    statusEl.innerHTML = `<span class="order-err">Network error: ${e.message}</span>`;
  }
});

/* ── SIDEBAR NAV ── */
function initSidebar() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

/* ── SCAN BUTTON ── */
document.getElementById('btn-run-scan').addEventListener('click', async () => {
  const btn = document.getElementById('btn-run-scan');
  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" style="animation:spinSlow 1s linear infinite"></i><span>Scanning...</span>';
  lucide.createIcons();
  try {
    await fetch('/api/run-scan', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({watchlist:['SPY','QQQ','NVDA','AAPL']})});
    await fetchAccount(); await fetchPositions(); await fetchLogs();
  } catch(e) { console.error('Scan:',e); }
  finally { btn.disabled=false; btn.innerHTML='<i data-lucide="zap"></i><span>AI Scan</span>'; lucide.createIcons(); }
});

/* ── KILL SWITCH ── */
document.getElementById('btn-kill-switch').addEventListener('click', async () => {
  if (confirm('EMERGENCY: Close ALL positions & cancel ALL orders?')) {
    await fetch('/api/kill-switch',{method:'POST'});
    await fetchAccount(); await fetchPositions();
  }
});

/* ── REFRESH ── */
document.getElementById('btn-refresh-positions').addEventListener('click', () => { fetchPositions(); fetchAccount(); });

/* ── INIT ── */
window.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initSidebar();
  initPayoffChart();
  fetchAccount();
  fetchPositions();
  fetchLogs();
  setInterval(() => { fetchAccount(); fetchPositions(); }, 10000);
});
'''

(WEB / "index.js").write_text(JS, encoding="utf-8")
print("[OK] web/index.js")

print(">>> v3 Quantum dashboard built (with manual trading + bug fixes)!")
