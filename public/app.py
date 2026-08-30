# web/app.py
import os
import sys
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import get_config
from src.alpaca_service import AlpacaService
from src.agent_desk import AegisOptionsDesk

st.set_page_config(
    page_title="AegisOptions | Autonomous AI Options Alpha Desk",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .badge-approved {
        background-color: #065f46;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-vetoed {
        background-color: #881337;
        color: #f43f5e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

if "desk" not in st.session_state:
    st.session_state.desk = AegisOptionsDesk()

desk: AegisOptionsDesk = st.session_state.desk

# Sidebar
st.sidebar.image("https://files.readme.io/2a85a89-black-alpaca-logo.svg", width=180)
st.sidebar.title("⚡ AegisOptions Desk")
st.sidebar.caption("Autonomous Options Alpha Engine on Alpaca & Featherless AI")

st.sidebar.divider()
st.sidebar.subheader("🎯 Autonomous Control")
watchlist = st.sidebar.multiselect(
    "Target Watchlist",
    options=["SPY", "QQQ", "NVDA", "AAPL", "TSLA", "MSFT", "AMD"],
    default=["SPY", "QQQ", "NVDA", "AAPL"]
)

run_scan = st.sidebar.button("🚀 Scan & Execute Options Cycle", use_container_width=True, type="primary")

if st.sidebar.button("🛑 Emergency Kill Switch (Close All)", use_container_width=True):
    with st.spinner("Closing all positions & open orders..."):
        res = desk.alpaca.close_all_positions()
        st.sidebar.success(f"Closed {len(res)} positions/orders!")

st.sidebar.divider()
st.sidebar.subheader("🛡️ Deterministic Guardrails")
st.sidebar.markdown("""
- **Max Risk per Trade**: 2.0% equity
- **Options Allocation Cap**: 20.0%
- **Max Bid-Ask Spread**: 15.0%
- **Target DTE**: 5 to 45 Days
- **Circuit Breaker**: -3.0% Day Loss
""")

account = desk.alpaca.get_account()
positions = desk.alpaca.get_positions()

st.title("⚡ AegisOptions: Autonomous AI Options Desk")
st.caption(f"Alpaca Account: **{account['account_number']}** | Status: **{account['status']}** | Inference Engine: **Featherless AI (Qwen-2.5-7B)**")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Portfolio Equity", f"${account['equity']:,.2f}", f"{account['day_pnl_pct']:+.2f}%")
with col2:
    st.metric("Cash Balance", f"${account['cash']:,.2f}")
with col3:
    st.metric("Buying Power", f"${account['buying_power']:,.2f}")
with col4:
    st.metric("Day P&L", f"${account['day_pnl']:+,.2f}")
with col5:
    st.metric("Options Level", f"Level {account['options_trading_level']}", "Approved")

st.divider()

if run_scan:
    with st.status("Executing Autonomous Alpha Cycle...", expanded=True) as status:
        st.write("🔍 Scanning watchlist for momentum & volatility regimes...")
        for sym in watchlist:
            st.write(f"Evaluating **{sym}** options chains and Greeks...")
            log = desk.scan_and_evaluate_symbol(sym)
            if log:
                st.write(f"• **{sym}**: {log.hypothesis.strategy} -> Risk Gate: {'✅ Approved' if log.risk_result.passed else '❌ Vetoed'}")
        status.update(label="Autonomous Cycle Complete!", state="complete", expanded=False)
        st.rerun()

tab1, tab2, tab3 = st.tabs(["📊 Active Positions & Greek Matrix", "🧠 AI Reasoning & Risk Gate Telemetry", "📈 Portfolio Analytics"])

with tab1:
    st.subheader("Live Open Positions")
    if positions:
        df_pos = pd.DataFrame(positions)
        st.dataframe(
            df_pos[["symbol", "qty", "side", "avg_entry_price", "current_price", "market_value", "unrealized_pl", "unrealized_plpc"]],
            use_container_width=True,
            column_config={
                "avg_entry_price": st.column_config.NumberColumn("Entry Price", format="$%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                "market_value": st.column_config.NumberColumn("Market Value", format="$%.2f"),
                "unrealized_pl": st.column_config.NumberColumn("Unrealized P&L", format="$%.2f"),
                "unrealized_plpc": st.column_config.NumberColumn("Return %", format="%.2f%%"),
            }
        )
    else:
        st.info("No open options positions currently. Click 'Scan & Execute Options Cycle' to initiate autonomous trades.")

with tab2:
    st.subheader("Autonomous Decision Stream & Deterministic Risk Audits")
    if desk.trade_logs:
        for log in reversed(desk.trade_logs[-10:]):
            with st.expander(f"⚡ {log.symbol} | {log.hypothesis.strategy} | {log.timestamp[:19]}", expanded=True):
                c_a, c_b = st.columns([1, 1])
                with c_a:
                    st.markdown("#### 🧠 Featherless AI Hypothesis")
                    st.write(f"**Regime**: `{log.hypothesis.regime}` | **Confidence**: `{log.hypothesis.confidence * 100:.0f}%`")
                    st.info(f"**Rationale**: {log.hypothesis.rationale}")
                    st.write(f"**Proposed Trade**: `{log.proposal.strategy}` (Qty: {log.proposal.contracts_qty})")
                    st.write(f"**Max Dollar Risk**: `${log.proposal.max_risk_usd:.2f}` | **Max Reward**: `${log.proposal.max_reward_usd:.2f}`")
                
                with c_b:
                    st.markdown("#### 🛡️ Deterministic Risk Gate Audit")
                    badge = "badge-approved" if log.risk_result.passed else "badge-vetoed"
                    verdict_text = "APPROVED FOR EXECUTION" if log.risk_result.passed else "VETOED BY RISK GATE"
                    st.markdown(f"<span class='{badge}'>{verdict_text}</span>", unsafe_allow_html=True)
                    st.write("")
                    st.write(f"**Approved Sizing**: `{log.risk_result.approved_qty} contracts` (Capped Risk: `${log.risk_result.adjusted_max_risk_usd:.2f}`)")
                    st.write(f"**Risk Summary**: {log.risk_result.risk_summary}")
                    if log.risk_result.violations:
                        st.error(f"Violations: {', '.join(log.risk_result.violations)}")
                    if log.executed:
                        st.success(f"✅ Live Alpaca Order Dispatched! Order IDs: {', '.join(log.order_ids)}")
    else:
        st.info("No trade logs recorded in this session yet. Launch a scan from the sidebar to inspect AI thoughts.")

with tab3:
    st.subheader("Capital & Risk Telemetry")
    gauge_col1, gauge_col2 = st.columns(2)
    with gauge_col1:
        options_val = sum(abs(p["market_value"]) for p in positions if "C00" in p["symbol"] or "P00" in p["symbol"])
        alloc_pct = (options_val / account["equity"] * 100) if account["equity"] > 0 else 0
        
        fig_alloc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=alloc_pct,
            title={'text': "Portfolio Options Allocation (%)"},
            gauge={
                'axis': {'range': [0, 30]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 15], 'color': "#10b981"},
                    {'range': [15, 20], 'color': "#f59e0b"},
                    {'range': [20, 30], 'color': "#ef4444"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 20}
            }
        ))
        fig_alloc.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_alloc, use_container_width=True)

    with gauge_col2:
        drawdown_val = abs(min(0.0, account["day_pnl_pct"]))
        fig_dd = go.Figure(go.Indicator(
            mode="gauge+number",
            value=drawdown_val,
            title={'text': "Daily Drawdown (% of Circuit Breaker)"},
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': "#f59e0b"},
                'steps': [
                    {'range': [0, 1.5], 'color': "#10b981"},
                    {'range': [1.5, 3.0], 'color': "#f59e0b"},
                    {'range': [3.0, 5.0], 'color': "#ef4444"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 3.0}
            }
        ))
        fig_dd.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_dd, use_container_width=True)
