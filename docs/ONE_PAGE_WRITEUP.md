# AegisOptions: Autonomous Multi-Agent Options Trading Desk
**LabLab.ai × Alpaca AI Trading Agents Hackathon — Challenge Submission**

---

### 1. Executive Summary & Strategy Rationale
**AegisOptions** is an autonomous quantitative options trading system built on **Alpaca's Trading API & FastMCP Server**, powered by serverless open-source model inference via **Featherless AI** (`Qwen/Qwen2.5-7B-Instruct`). 

While conventional retail algorithms rely on simple directional equity orders or unhedged options bets, AegisOptions systematically harvests volatility risk premia and directional momentum using **defined-risk multi-leg options spreads** (Bull Call Spreads, Bear Put Spreads, and Iron Condors) with strict mathematical risk bounds.

---

### 2. Autonomous Multi-Agent AI Architecture
AegisOptions operates as a 4-agent dialectic desk:
1. **Market Scanner & Intelligence Agent**: Ingests real-time IEX bars, 30-day realized volatility, and 5/20-day moving average momentum for watchlist assets (`SPY`, `QQQ`, `NVDA`, `AAPL`, `TSLA`, `MSFT`, `AMD`).
2. **Featherless AI Alpha Strategist**: Formulates macro/volatility hypotheses and selects optimal options structures. Returns structured JSON with confidence scoring and trade rationale.
3. **Quantitative Greeks & Strike Selector**: Filters live Alpaca Option Chains (via `INDICATIVE` feed) to isolate contracts matching optimal Delta/Gamma/Vega ratios (~0.40 Delta long leg, ~0.20 Delta short leg) to maximize asymmetric convexity.
4. **Execution Engine**: Interacts with Alpaca's paper trading platform via `alpaca-py` and standalone **FastMCP Server**, enabling autonomous execution and agent tool integration.

```
[Alpaca Market Data & Option Chains]
               │
               ▼
[Featherless AI Alpha Strategist] ──► [Quantitative Greeks Selector]
                                                   │
                                                   ▼
                                    [Deterministic Risk Guardrail Engine]
                                                   │ (Pass/Fail)
                                                   ▼
                                    [Alpaca Execution / FastMCP] ──► [$100k Paper Account PA3PL5AZ85K6]
```

---

### 3. Deterministic Risk Gates (Zero-LLM Authority)
To eliminate catastrophic hallucinations, **no AI model has execution authority**. All proposals must pass 7 hardcoded deterministic gates:
* 🛡️ **Gate 1 — Defined-Risk Requirement**: Naked calls/puts are strictly vetoed. Only defined-risk vertical spreads and iron condors with strictly capped maximum loss are permitted.
* 🛡️ **Gate 2 — Max Risk per Trade (2.0%)**: Maximum dollar loss per position cannot exceed 2.0% of portfolio equity ($2,000 max on $100k account).
* 🛡️ **Gate 3 — Portfolio Options Exposure Cap (20.0%)**: Total capital committed to active options contracts cannot exceed 20.0% of portfolio equity ($20,000).
* 🛡️ **Gate 4 — Liquidity & Bid-Ask Spread Filter**: Any option contract with a bid-ask spread wider than 15.0% of mid-price is automatically vetoed to prevent slippage decay.
* 🛡️ **Gate 5 — Duration & DTE Boundary**: Trades are restricted to 5–45 Days to Expiration (DTE) to avoid 0-DTE extreme gamma pin risk while optimizing theta decay.
* 🛡️ **Gate 6 — Daily Drawdown Circuit Breaker**: If portfolio daily P&L falls below -3.0%, all new trade entries are immediately frozen.
* 🛡️ **Gate 7 — Dynamic Position Sizing**: Contracts are mathematically sized based on unit risk to prevent over-allocation.

---

### 4. Alpaca Infrastructure & Observability
* **Alpaca Trading API**: Level-3 paper trading account (`PA3PL5AZ85K6`, $100,000 starting balance).
* **FastMCP Server (`src/mcp_server.py`)**: Exposes portfolio telemetry, active positions, alpha scanner, and emergency kill-switch tools.
* **Observability Dashboard (`web/app.py`)**: Real-time Streamlit UI rendering live Greeks, open positions, P&L telemetry, and full audit logs of AI reasoning vs. risk gate decisions.
