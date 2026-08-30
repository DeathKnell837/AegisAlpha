# src/risk_engine.py
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from src.config import get_config


class TradeProposal(BaseModel):
    symbol: str
    strategy: str
    long_contract: Optional[Dict[str, Any]] = None
    short_contract: Optional[Dict[str, Any]] = None
    contracts_qty: int = 1
    net_debit_or_credit: float = 0.0
    max_risk_usd: float = 0.0
    max_reward_usd: float = 0.0
    rationale: str = ""


class RiskGateResult(BaseModel):
    passed: bool
    approved_qty: int
    adjusted_max_risk_usd: float
    violations: List[str] = Field(default_factory=list)
    gate_checks: Dict[str, bool] = Field(default_factory=dict)
    risk_summary: str = ""


class DeterministicRiskEngine:
    """
    Zero-hallucination deterministic guardrails.
    Evaluates proposed options trades against strict mathematical risk parameters.
    """
    def __init__(self):
        self.config = get_config()
        self.risk_cfg = self.config.risk

    def evaluate_trade(
        self,
        proposal: TradeProposal,
        account: Dict[str, Any],
        open_positions: List[Dict[str, Any]]
    ) -> RiskGateResult:
        violations = []
        gate_checks = {}

        equity = account.get("equity", 100000.0)
        buying_power = account.get("buying_power", 400000.0)
        day_pnl_pct = account.get("day_pnl_pct", 0.0)

        # 1. Daily Drawdown Circuit Breaker Gate
        if day_pnl_pct <= -(self.risk_cfg.max_daily_drawdown_pct * 100):
            violations.append(f"Daily drawdown circuit breaker triggered ({day_pnl_pct:.2f}% <= -{self.risk_cfg.max_daily_drawdown_pct * 100}%)")
            gate_checks["daily_drawdown_gate"] = False
        else:
            gate_checks["daily_drawdown_gate"] = True

        # 2. Defined-Risk Spread Requirement Gate
        is_defined_risk = proposal.strategy in ["BULL_CALL_SPREAD", "BEAR_PUT_SPREAD", "IRON_CONDOR"] or (
            proposal.long_contract is not None and proposal.short_contract is None
        )
        if not is_defined_risk:
            violations.append(f"Uncapped risk strategy rejected: {proposal.strategy}. Must be defined-risk.")
            gate_checks["defined_risk_gate"] = False
        else:
            gate_checks["defined_risk_gate"] = True

        # 3. Liquidity / Bid-Ask Spread Gate
        spread_ok = True
        if proposal.long_contract:
            spread_pct = proposal.long_contract.get("spread_pct", 0.0)
            if spread_pct > self.risk_cfg.max_slippage_bid_ask_pct:
                violations.append(f"Long leg bid-ask spread too wide ({spread_pct*100:.1f}% > {self.risk_cfg.max_slippage_bid_ask_pct*100}%)")
                spread_ok = False
        if proposal.short_contract:
            spread_pct = proposal.short_contract.get("spread_pct", 0.0)
            if spread_pct > self.risk_cfg.max_slippage_bid_ask_pct:
                violations.append(f"Short leg bid-ask spread too wide ({spread_pct*100:.1f}% > {self.risk_cfg.max_slippage_bid_ask_pct*100}%)")
                spread_ok = False
        gate_checks["liquidity_spread_gate"] = spread_ok

        # 4. Total Portfolio Options Allocation Gate
        total_options_exposure = sum(
            abs(p.get("market_value", 0.0)) for p in open_positions if "C00" in p.get("symbol", "") or "P00" in p.get("symbol", "")
        )
        max_allowed_options_exposure = equity * self.risk_cfg.max_portfolio_options_pct
        if total_options_exposure + proposal.max_risk_usd > max_allowed_options_exposure:
            violations.append(f"Portfolio options exposure would exceed {self.risk_cfg.max_portfolio_options_pct*100}% limit ($ {total_options_exposure + proposal.max_risk_usd:.2f} > $ {max_allowed_options_exposure:.2f})")
            gate_checks["portfolio_allocation_gate"] = False
        else:
            gate_checks["portfolio_allocation_gate"] = True

        # 5. Position Sizing & Max Risk per Trade Gate
        max_risk_per_trade_usd = min(equity * self.risk_cfg.max_risk_per_trade_pct, self.risk_cfg.max_position_size_usd)
        unit_risk = (proposal.max_risk_usd / proposal.contracts_qty) if proposal.contracts_qty > 0 else proposal.max_risk_usd

        if unit_risk <= 0:
            unit_risk = 100.0  # safety floor

        max_contracts_allowed = max(1, int(max_risk_per_trade_usd // unit_risk))
        approved_qty = min(proposal.contracts_qty, max_contracts_allowed)
        adjusted_max_risk = unit_risk * approved_qty

        if adjusted_max_risk > max_risk_per_trade_usd * 1.05:
            violations.append(f"Trade risk $ {adjusted_max_risk:.2f} exceeds max allowable single-trade risk of $ {max_risk_per_trade_usd:.2f}")
            gate_checks["position_sizing_gate"] = False
        else:
            gate_checks["position_sizing_gate"] = True

        # Overall verdict
        passed = len(violations) == 0

        summary = (
            f"Risk Gate Approved: {approved_qty} contracts, max risk $ {adjusted_max_risk:.2f} ({adjusted_max_risk/equity*100:.2f}% equity)."
            if passed
            else f"Risk Gate VETOED: {'; '.join(violations)}"
        )

        return RiskGateResult(
            passed=passed,
            approved_qty=approved_qty,
            adjusted_max_risk_usd=adjusted_max_risk,
            violations=violations,
            gate_checks=gate_checks,
            risk_summary=summary
        )
