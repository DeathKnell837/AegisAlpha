# tests/test_bootstrap.py -> test_risk_engine
import pytest
from src.risk_engine import DeterministicRiskEngine, TradeProposal

def test_risk_engine_daily_drawdown_breaker():
    """Verify that daily loss exceeding 3% halts trading."""
    engine = DeterministicRiskEngine()
    proposal = TradeProposal(
        symbol="SPY",
        strategy="BULL_CALL_SPREAD",
        long_contract={"spread_pct": 0.02},
        short_contract={"spread_pct": 0.02},
        contracts_qty=1,
        max_risk_usd=300.0,
        max_reward_usd=500.0
    )
    # Account with -3.5% daily drawdown
    account = {"equity": 100000.0, "buying_power": 400000.0, "day_pnl_pct": -3.5}
    res = engine.evaluate_trade(proposal, account, [])
    assert not res.passed
    assert "Daily drawdown circuit breaker" in res.violations[0]

def test_risk_engine_bid_ask_spread_gate():
    """Verify that illiquid options with wide bid-ask spread (>15%) are vetoed."""
    engine = DeterministicRiskEngine()
    proposal = TradeProposal(
        symbol="NVDA",
        strategy="BULL_CALL_SPREAD",
        long_contract={"spread_pct": 0.22},  # 22% spread > 15% limit
        short_contract={"spread_pct": 0.03},
        contracts_qty=1,
        max_risk_usd=400.0,
        max_reward_usd=600.0
    )
    account = {"equity": 100000.0, "buying_power": 400000.0, "day_pnl_pct": 0.0}
    res = engine.evaluate_trade(proposal, account, [])
    assert not res.passed
    assert any("bid-ask spread too wide" in v for v in res.violations)

def test_risk_engine_portfolio_allocation_cap():
    """Verify that options exposure exceeding 20% of equity is vetoed."""
    engine = DeterministicRiskEngine()
    proposal = TradeProposal(
        symbol="TSLA",
        strategy="BULL_CALL_SPREAD",
        long_contract={"spread_pct": 0.03},
        short_contract={"spread_pct": 0.03},
        contracts_qty=5,
        max_risk_usd=5000.0,
        max_reward_usd=8000.0
    )
    # Already holding $18,000 in options on $100k account (20k max allowed)
    open_positions = [{"symbol": "SPY260908C00773000", "market_value": 18000.0}]
    account = {"equity": 100000.0, "buying_power": 400000.0, "day_pnl_pct": 0.0}
    res = engine.evaluate_trade(proposal, account, open_positions)
    assert not res.passed
    assert any("Portfolio options exposure would exceed" in v for v in res.violations)

def test_risk_engine_approved_defined_risk_trade():
    """Verify that a compliant defined-risk spread is approved with correct sizing."""
    engine = DeterministicRiskEngine()
    proposal = TradeProposal(
        symbol="SPY",
        strategy="BULL_CALL_SPREAD",
        long_contract={"spread_pct": 0.02},
        short_contract={"spread_pct": 0.02},
        contracts_qty=2,
        max_risk_usd=600.0,
        max_reward_usd=1000.0
    )
    account = {"equity": 100000.0, "buying_power": 400000.0, "day_pnl_pct": 0.2}
    res = engine.evaluate_trade(proposal, account, [])
    assert res.passed
    assert res.approved_qty == 2
    assert res.adjusted_max_risk_usd == 600.0
    assert "Risk Gate Approved" in res.risk_summary
