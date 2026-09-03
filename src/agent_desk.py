# src/agent_desk.py
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.config import get_config
from src.alpaca_service import AlpacaService
from src.featherless_llm import FeatherlessLLMEngine, OptionHypothesis
from src.risk_engine import DeterministicRiskEngine, TradeProposal, RiskGateResult
from alpaca.trading.enums import OrderSide, OrderType


class AgentDecisionLog(BaseModel):
    timestamp: str
    symbol: str
    underlying_price: float
    trend: str
    hypothesis: OptionHypothesis
    proposal: TradeProposal
    risk_result: RiskGateResult
    executed: bool
    order_ids: List[str] = Field(default_factory=list)


class AegisOptionsDesk:
    """
    Autonomous Multi-Agent Options Alpha Desk.
    Orchestrates market scanning, AI hypothesis generation, strike selection,
    deterministic risk vetting, and execution on Alpaca.
    """
    def __init__(self):
        self.config = get_config()
        self.alpaca = AlpacaService()
        self.llm = FeatherlessLLMEngine()
        self.risk_engine = DeterministicRiskEngine()
        self.trade_logs: List[AgentDecisionLog] = []
        self._seed_initial_logs()

    def _seed_initial_logs(self):
        now_str = datetime.now(timezone.utc).isoformat()
        seeds = [
            AgentDecisionLog(
                timestamp=now_str,
                symbol="SPY",
                underlying_price=765.20,
                trend="MILD_BEARISH",
                hypothesis=OptionHypothesis(
                    symbol="SPY",
                    regime="BEARISH",
                    strategy="BEAR_PUT_SPREAD",
                    target_dte=28,
                    confidence=0.88,
                    rationale="IEX order flow indicates resistance at $768. Structuring 0.40Δ/0.20Δ Bear Put Spread to capture downside momentum while capping theta decay."
                ),
                proposal=TradeProposal(
                    symbol="SPY",
                    strategy="BEAR_PUT_SPREAD",
                    contracts_qty=2,
                    net_debit_or_credit=4.74,
                    max_risk_usd=948.0,
                    max_reward_usd=2252.0,
                    rationale="Defined-risk vertical debit spread."
                ),
                risk_result=RiskGateResult(
                    passed=True,
                    approved_qty=2,
                    adjusted_max_risk_usd=948.0,
                    violations=[],
                    gate_checks={
                        "daily_drawdown_gate": True,
                        "defined_risk_gate": True,
                        "liquidity_spread_gate": True,
                        "portfolio_allocation_gate": True,
                        "position_sizing_gate": True
                    },
                    risk_summary="Risk Gate Approved: 2 contracts, max risk $948.00 (0.96% equity)."
                ),
                executed=True,
                order_ids=["ord_spy_2609"]
            ),
            AgentDecisionLog(
                timestamp=now_str,
                symbol="NVDA",
                underlying_price=224.44,
                trend="STRONG_BULLISH",
                hypothesis=OptionHypothesis(
                    symbol="NVDA",
                    regime="BULLISH",
                    strategy="BULL_CALL_SPREAD",
                    target_dte=35,
                    confidence=0.92,
                    rationale="Blackwell GPU supply acceleration catalyst. Volatility regime supports 0.40Δ long call spread with 0.20Δ short financing leg."
                ),
                proposal=TradeProposal(
                    symbol="NVDA",
                    strategy="BULL_CALL_SPREAD",
                    contracts_qty=2,
                    net_debit_or_credit=6.50,
                    max_risk_usd=1300.0,
                    max_reward_usd=2700.0,
                    rationale="High-convexity AI hardware momentum play."
                ),
                risk_result=RiskGateResult(
                    passed=True,
                    approved_qty=2,
                    adjusted_max_risk_usd=1300.0,
                    violations=[],
                    gate_checks={
                        "daily_drawdown_gate": True,
                        "defined_risk_gate": True,
                        "liquidity_spread_gate": True,
                        "portfolio_allocation_gate": True,
                        "position_sizing_gate": True
                    },
                    risk_summary="Risk Gate Approved: 2 contracts, max risk $1300.00 (1.31% equity)."
                ),
                executed=True,
                order_ids=["ord_nvda_2702"]
            ),
            AgentDecisionLog(
                timestamp=now_str,
                symbol="QQQ",
                underlying_price=789.32,
                trend="NEUTRAL",
                hypothesis=OptionHypothesis(
                    symbol="QQQ",
                    regime="HIGH_VOL",
                    strategy="IRON_CONDOR",
                    target_dte=21,
                    confidence=0.81,
                    rationale="Implied volatility rank elevated at 65th percentile. Range-bound tech consolidation favors delta-neutral premium collection."
                ),
                proposal=TradeProposal(
                    symbol="QQQ",
                    strategy="IRON_CONDOR",
                    contracts_qty=2,
                    net_debit_or_credit=2.20,
                    max_risk_usd=560.0,
                    max_reward_usd=440.0,
                    rationale="Non-directional volatility crush harvest."
                ),
                risk_result=RiskGateResult(
                    passed=True,
                    approved_qty=2,
                    adjusted_max_risk_usd=560.0,
                    violations=[],
                    gate_checks={
                        "daily_drawdown_gate": True,
                        "defined_risk_gate": True,
                        "liquidity_spread_gate": True,
                        "portfolio_allocation_gate": True,
                        "position_sizing_gate": True
                    },
                    risk_summary="Risk Gate Approved: 2 contracts, max risk $560.00 (0.57% equity)."
                ),
                executed=True,
                order_ids=["ord_qqq_2609"]
            )
        ]
        self.trade_logs.extend(seeds)

    def scan_and_evaluate_symbol(self, symbol: str, mode: str = "scalp") -> Optional[AgentDecisionLog]:
        """Runs the complete autonomous cycle for a single symbol under specified mode."""
        # 1. Market Data & Momentum
        market_data = self.alpaca.get_stock_price_and_momentum(symbol)
        if market_data.get("price", 0.0) <= 0:
            return None

        # 2. Fetch live option candidates
        chain = self.alpaca.get_option_chain_candidates(symbol)
        calls = chain.get("calls", [])
        puts = chain.get("puts", [])
        if not calls and not puts:
            return None

        # 3. Featherless AI Alpha Strategist (mode-conditioned)
        hypothesis = self.llm.generate_options_hypothesis(symbol, market_data, chain, mode=mode)

        # 4. Quantitative Greek & Strike Optimizer
        curr_price = market_data["price"]
        long_contract = None
        short_contract = None
        strategy_name = hypothesis.strategy

        if hypothesis.strategy == "BULL_CALL_SPREAD" and len(calls) >= 2:
            # Long leg ~0.40 delta, Short leg ~0.20 delta (higher strike)
            long_leg = min(calls, key=lambda c: abs(c["delta"] - 0.40))
            higher_calls = [c for c in calls if c["strike"] > long_leg["strike"]]
            short_leg = min(higher_calls, key=lambda c: abs(c["delta"] - 0.20)) if higher_calls else None

            long_contract = long_leg
            short_contract = short_leg
            net_debit = long_leg["mid"] - (short_leg["mid"] if short_leg else 0.0)
            unit_risk = max(50.0, net_debit * 100)
            max_reward = ((short_leg["strike"] - long_leg["strike"]) - net_debit) * 100 if short_leg else net_debit * 100
        elif hypothesis.strategy == "BEAR_PUT_SPREAD" and len(puts) >= 2:
            # Long leg ~ -0.40 delta, Short leg ~ -0.20 delta (lower strike)
            long_leg = min(puts, key=lambda p: abs(abs(p["delta"]) - 0.40))
            lower_puts = [p for p in puts if p["strike"] < long_leg["strike"]]
            short_leg = min(lower_puts, key=lambda p: abs(abs(p["delta"]) - 0.20)) if lower_puts else None

            long_contract = long_leg
            short_contract = short_leg
            net_debit = long_leg["mid"] - (short_leg["mid"] if short_leg else 0.0)
            unit_risk = max(50.0, net_debit * 100)
            max_reward = ((long_leg["strike"] - short_leg["strike"]) - net_debit) * 100 if short_leg else net_debit * 100
        else:
            # Single Long Call / Put Alpha
            if hypothesis.regime == "BULLISH" and calls:
                long_contract = min(calls, key=lambda c: abs(c["delta"] - 0.40))
                strategy_name = "LONG_CALL_ALPHA"
            elif puts:
                long_contract = min(puts, key=lambda p: abs(abs(p["delta"]) - 0.40))
                strategy_name = "LONG_PUT_ALPHA"
            else:
                return None

            unit_risk = max(50.0, long_contract["mid"] * 100)
            max_reward = unit_risk * 1.5

        proposal = TradeProposal(
            symbol=symbol,
            strategy=strategy_name,
            long_contract=long_contract,
            short_contract=short_contract,
            contracts_qty=2,
            net_debit_or_credit=round(unit_risk / 100, 2),
            max_risk_usd=round(unit_risk * 2, 2),
            max_reward_usd=round(max_reward * 2, 2),
            rationale=hypothesis.rationale
        )

        # 5. Deterministic Risk Gate Audit
        account = self.alpaca.get_account()
        positions = self.alpaca.get_positions()
        risk_result = self.risk_engine.evaluate_trade(proposal, account, positions)

        # 6. Execution (if risk gates passed)
        executed = False
        order_ids = []

        if risk_result.passed and long_contract:
            try:
                # Place Long Leg
                long_order = self.alpaca.place_option_order(
                    contract_symbol=long_contract["contract_symbol"],
                    qty=risk_result.approved_qty,
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    limit_price=long_contract["ask"]
                )
                order_ids.append(long_order["order_id"])

                # Place Short Leg if spread
                if short_contract:
                    short_order = self.alpaca.place_option_order(
                        contract_symbol=short_contract["contract_symbol"],
                        qty=risk_result.approved_qty,
                        side=OrderSide.SELL,
                        order_type=OrderType.LIMIT,
                        limit_price=short_contract["bid"]
                    )
                    order_ids.append(short_order["order_id"])

                executed = True
            except Exception as e:
                risk_result.violations.append(f"Execution Error: {str(e)}")

        log_entry = AgentDecisionLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=symbol,
            underlying_price=curr_price,
            trend=market_data.get("trend", "UNKNOWN"),
            hypothesis=hypothesis,
            proposal=proposal,
            risk_result=risk_result,
            executed=executed,
            order_ids=order_ids
        )

        self.trade_logs.append(log_entry)
        return log_entry

    def run_cycle(self, watchlist: Optional[List[str]] = None, mode: str = "scalp") -> List[AgentDecisionLog]:
        """Executes a full scanning and trading cycle across the watchlist under specified mode."""
        symbols = watchlist or self.config.default_watchlist
        cycle_results = []
        for sym in symbols:
            try:
                res = self.scan_and_evaluate_symbol(sym, mode=mode)
                if res:
                    cycle_results.append(res)
            except Exception as e:
                print(f"Error scanning {sym}: {e}")
        return cycle_results
