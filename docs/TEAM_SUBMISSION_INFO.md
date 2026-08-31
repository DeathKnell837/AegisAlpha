# 🦅 Team "Returnee" — Hackathon Submission Details

Use these ready-to-copy fields to fill out your Lablab.ai team profile and project submission form:

---

## 1. Team Profile Information

- **Team Name**: `Returnee`
- **Team Tagline**: `Veteran solo builder returning with autonomous multi-agent quantitative intelligence.`
- **Team Type**: Solo Competitor
- **Team Avatar URL**: [https://raw.githubusercontent.com/DeathKnell837/band-of-agents-hackathon/master/team_avatar.jpg](https://raw.githubusercontent.com/DeathKnell837/band-of-agents-hackathon/master/team_avatar.jpg)
- **Team Banner URL**: [https://raw.githubusercontent.com/DeathKnell837/band-of-agents-hackathon/master/team_banner.jpg](https://raw.githubusercontent.com/DeathKnell837/band-of-agents-hackathon/master/team_banner.jpg)

### Team Bio / Description:
```text
Returnee is a solo competitive hackathon team focused on pushing the frontier of autonomous AI agents and quantitative finance. Returning as a seasoned builder to the Alpaca AI Trading Agents Hackathon, Returnee combines production-grade financial engineering with open-source frontier LLMs (Qwen-2.5-72B via Featherless AI) and Alpaca's institutional FastMCP tool architecture to solve the safety and execution challenges of autonomous options trading.
```

### Team Member Role:
- **Name / Handle**: `@DeathKnell837`
- **Role**: `Solo Full-Stack AI Engineer & Quantitative Developer`
- **Skills**: `Python, LLM Agents, Alpaca API, FastMCP, Options Greeks, Quantitative Risk Management, Web UI/UX`

---

## 2. Project Submission Information

- **Project Title**: `AegisAlpha: Autonomous AI Options Desk`
- **Short Pitch (1-liner)**: `Autonomous multi-agent options trading desk powered by Alpaca FastMCP, Qwen-2.5-72B on Featherless AI, and 7 zero-LLM deterministic mathematical risk guardrails.`

### Track / Category:
- `AI Trading Agents / Multi-Agent Systems / FastMCP Tool Integration`

### Problem Statement:
```text
Most AI trading experiments either place naive directional equity bets or hallucinate high-risk unhedged options positions. Retail traders lack access to institutional multi-agent workflows that can scan volatility surfaces, optimize strike Greeks, and enforce un-bypassable mathematical risk constraints.
```

### Solution:
```text
AegisOptions solves this by separating strategy generation from risk enforcement across a 4-agent architecture:
1. Market Scanner: Ingests live IEX bars and historical volatility surfaces.
2. Alpha Strategist: Uses Qwen-2.5-72B via Featherless AI to evaluate volatility regimes and propose defined-risk spreads (Bull Call Spreads, Bear Put Spreads, Iron Condors).
3. Greeks Engine: Structures optimal asymmetric convexity (~0.40 / 0.20 Delta legs).
4. Deterministic Risk Gatekeeper: 7 hardcoded mathematical rules (zero LLM authority) that enforce strict 2% per-trade risk limits, 20% portfolio caps, bid-ask slippage filters, and daily drawdown circuit breakers before autonomous execution on Alpaca.
```

---

## 3. Official Links

- **GitHub Repository**: [https://github.com/DeathKnell837/AegisAlpha](https://github.com/DeathKnell837/AegisAlpha)
- **Live Production App**: [https://aegis-alpha-desk.vercel.app](https://aegis-alpha-desk.vercel.app)
- **Interactive Slide Deck**: [https://aegis-alpha-desk.vercel.app/slides.html](https://aegis-alpha-desk.vercel.app/slides.html)
- **1-Page Architecture Doc**: [https://github.com/DeathKnell837/AegisAlpha/blob/master/docs/ONE_PAGE_WRITEUP.md](https://github.com/DeathKnell837/AegisAlpha/blob/master/docs/ONE_PAGE_WRITEUP.md)
