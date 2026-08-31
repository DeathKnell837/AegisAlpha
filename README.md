# ⚡ AegisAlpha: Autonomous Multi-Agent Options Desk

<div align="center">
  <img src="team_banner.jpg" alt="Returnee Team Banner" width="100%" style="border-radius:12px;margin-bottom:16px;" />
</div>

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live%20Dashboard-00D4AA.svg)](https://aegis-alpha-desk.vercel.app)
[![Alpaca Trading API](https://img.shields.io/badge/Alpaca-Trading%20API-yellow.svg)](https://alpaca.markets)
[![FastMCP Server](https://img.shields.io/badge/MCP-FastMCP%202.0-blue.svg)](https://github.com/alpacahq/alpaca-mcp-server)
[![Featherless AI](https://img.shields.io/badge/Inference-Qwen%2072B%20Featherless-purple.svg)](https://featherless.ai)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.14-green.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AegisAlpha** is an autonomous quantitative options trading system engineered for the **LabLab.ai × Alpaca AI Trading Agents Hackathon** by solo builder team **Returnee**. It combines serverless open-source model inference via **Featherless AI** (`Qwen/Qwen2.5-72B-Instruct`), real-time option chains and Greeks from **Alpaca's Trading API**, a standalone **FastMCP Server**, and a strict **Deterministic Risk Engine (Zero-LLM Authority)**.

🌐 **Live Production App**: [https://aegis-alpha-desk.vercel.app](https://aegis-alpha-desk.vercel.app)  
📊 **Interactive Pitch Slides**: [https://aegis-alpha-desk.vercel.app/slides.html](https://aegis-alpha-desk.vercel.app/slides.html)

---

## 🏆 Hackathon Highlights

* 🏦 **Dedicated Account**: Live Level-3 Options paper trading on fresh \$100,000 account (`PA3PL5AZ85K6`).
* 📊 **Multi-Leg Defined-Risk Options**: Executes Bull Call Spreads, Bear Put Spreads, and Iron Condors with asymmetric risk/reward.
* 🛡️ **Zero-LLM Authority Risk Engine**: 7 hard mathematical guardrails veto unsafe trades, manage position sizing, enforce DTE bounds, and trigger drawdown circuit breakers.
* 🔌 **FastMCP Integration**: Exposes 5 autonomous agent tools for Cursor, Claude Desktop, and Antigravity.
* 🖥️ **Live Observability Dashboard**: Full Streamlit web UI with live Greek matrices, P&L telemetry, and AI thought streams.

---

## 🏗️ Multi-Agent Architecture

```mermaid
flowchart TD
    subgraph S1["1. Market & Options Ingestion"]
        A["Alpaca IEX Data Client"] --> M["Market Momentum & Volatility Scanner"]
        B["Alpaca Options Data Client"] --> OC["Option Chains & Greeks (Delta, Gamma, Vega, IV)"]
    end

    subgraph S2["2. Autonomous AI Desk (Featherless AI)"]
        M --> Alpha["Alpha Strategist (Qwen-2.5-72B)\nRegime & Spread Hypotheses"]
        OC --> Quant["Quantitative Greeks Optimizer\n0.40 / 0.20 Delta Strike Selection"]
        Alpha --> Quant
    end

    subgraph S3["3. Deterministic Risk Engine (Zero-LLM Authority)"]
        Quant --> Gate{"7 Hardcoded Safety Gates\n(Defined Risk, Max 2% Equity Risk, Drawdown Breaker)"}
        Gate -- REJECT / DOWNSIZE --> Log["Audit Telemetry (Trade Vetoed / Resized)"]
    end

    subgraph S4["4. Alpaca Execution Layer"]
        Gate -- APPROVED --> FastMCP["Alpaca Trading Client / FastMCP Server"]
        FastMCP --> Broker["Alpaca Paper Account PA3PL5AZ85K6"]
    end

    subgraph S5["5. Observability & Web UI"]
        Broker --> Dash["Quantum Dark Web Dashboard\n(Live Orders, Payoff Curves, P&L)"]
        Log --> Dash
    end
```

---

## 🛡️ The 7 Deterministic Risk Guardrails

| Gate | Name | Rule / Boundary |
| :--- | :--- | :--- |
| **Gate 1** | **Defined-Risk Requirement** | Naked/uncapped options strictly vetoed. Only vertical spreads and iron condors allowed. |
| **Gate 2** | **Max Risk per Trade** | Max dollar loss per position capped at **2.0% of portfolio equity** (\$2,000 max on \$100k account). |
| **Gate 3** | **Portfolio Options Cap** | Total capital committed to active options positions cannot exceed **20.0% of equity** (\$20,000). |
| **Gate 4** | **Liquidity & Slippage** | Contracts with bid-ask spread wider than **15.0% of mid-price** are rejected. |
| **Gate 5** | **DTE Range Guardrail** | Trades restricted to **5 to 45 Days to Expiration (DTE)** to prevent 0-DTE gamma pin traps. |
| **Gate 6** | **Daily Drawdown Breaker** | New trades immediately frozen if daily portfolio drawdown reaches **-3.0%**. |
| **Gate 7** | **Dynamic Position Sizing** | Contracts automatically downsized to adhere to exact unit risk boundaries. |

---

## 🚀 Quickstart & Setup

### 1. Clone & Setup Environment
```bash
git clone https://github.com/DeathKnell837/AegisAlpha.git
cd band-of-agents-hackathon
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file with your credentials:
```env
ALPACA_API_KEY=PK4R5RYFZ6XNIOMRAJKSPHYJAT
ALPACA_SECRET_KEY=9HAw6A8h2z3oyWHBnfRDXh1T57QwcNCfN6mZTqSaeTJW
ALPACA_API_BASE_URL=https://paper-api.alpaca.markets
ALPACA_ACCOUNT_ID=PA3PL5AZ85K6

FEATHERLESS_API_KEY=rc_e00d1ccd3560e26a8a4c148600c0aa542fd3e0860815efcb0508f37ab414e3bd
```

### 3. Run Unit Tests
```bash
pytest -v
```

### 4. Launch the Observability Dashboard
```bash
streamlit run web/app.py
```

### 5. Run Standalone FastMCP Server
```bash
python src/mcp_server.py
```

---

## 📦 Project Structure

```
├── .env.example               # Environment template
├── pytest.ini                 # Test configuration
├── requirements.txt           # Project dependencies
├── docs/
│   ├── ONE_PAGE_WRITEUP.md    # Official 1-page submission write-up
│   ├── DEMO_VIDEO_SCRIPT.md   # Presentation & video walkthrough script
│   └── SOCIAL_POSTS.md        # 5 Build-in-Public social media posts
├── src/
│   ├── config.py              # App & Risk configuration
│   ├── alpaca_service.py      # Alpaca market data, option chains & orders
│   ├── featherless_llm.py     # Featherless AI quantitative alpha engine
│   ├── risk_engine.py         # 7 Deterministic Risk Guardrails
│   ├── agent_desk.py          # Autonomous multi-agent coordinator
│   └── mcp_server.py          # FastMCP server tools
├── tests/                     # 8/8 passing unit tests
│   ├── test_bootstrap.py      # Deterministic risk engine tests
│   ├── test_config.py         # Config validation tests
│   ├── test_models.py         # LLM Pydantic model tests
│   └── test_prompts.py        # Alpaca client structure tests
└── web/
    └── app.py                 # Streamlit Live Observability Dashboard
```

---

## 📜 License
MIT License. Open-source for the Alpaca & LabLab.ai community.
        Reviewer -->|Adversarial Verdict, Exposure & Challenges| BandRoom
    end
MIT License. Open-source for the Alpaca & LabLab.ai community.
