# 🎥 AegisOptions — Hackathon Video Presentation Script (2-3 Mins)

### [0:00 - 0:30] Introduction & Problem Statement
* **Visual**: Show AegisOptions Streamlit Dashboard with Alpaca Account `$100,000.00` balance.
* **Voiceover**: 
  > "Welcome! This is AegisOptions — an autonomous AI options alpha desk built for the Alpaca AI Trading Agents Hackathon. 
  > Trading options with AI requires more than just generating trade ideas. It demands rigorous mathematical risk guardrails, real-time Greek analysis, and defined-risk execution. 
  > AegisOptions combines the speed of Featherless AI with Alpaca's Trading API and FastMCP Server to deliver a self-governing, multi-agent options fund."

### [0:30 - 1:15] Architecture & AI Reasoning
* **Visual**: Switch to Tab 2 ('AI Reasoning & Risk Gate Telemetry'), click 'Scan & Execute Options Cycle'.
* **Voiceover**: 
  > "Here is our autonomous cycle in action. First, the Market Scanner ingests real-time IEX bars and historical volatility across our watchlist. 
  > Next, our Alpha Strategist — powered by Featherless AI's Qwen-2.5-7B — formulates high-conviction directional and volatility hypotheses. 
  > Our Quantitative Greek Engine then queries Alpaca's live option chain to select optimal 0.40/0.20 Delta strikes for asymmetric risk-reward."

### [1:15 - 1:50] Deterministic Risk Guardrails in Action
* **Visual**: Highlight the 'Deterministic Risk Gate Audit' cards showing approved vs. vetoed trades.
* **Voiceover**: 
  > "Crucially, the LLM has zero direct execution power. Every trade must clear our 7 Deterministic Risk Gates:
  > • Capping max risk to 2% of portfolio equity
  > • Restricting options exposure to 20% total allocation
  > • Enforcing strict bid-ask liquidity spreads
  > • And a hard daily drawdown circuit breaker.
  > If an option has excessive slippage or uncapped risk, the engine vetoes it on the spot."

### [1:50 - 2:30] Live Execution & Portfolio Telemetry
* **Visual**: Switch to Tab 1 ('Active Positions & Greek Matrix') showing open Alpaca positions, then Tab 3 ('Capital & Risk Telemetry').
* **Voiceover**: 
  > "Once approved, orders execute directly against Alpaca's paper trading API. We can monitor live positions, unrealized P&L, and portfolio Greek exposure in real time. 
  > Everything is open-source, modular, and equipped with a FastMCP server for seamless integration with AI assistants. 
  > Thank you to Alpaca and Lablab.ai for this incredible challenge!"
