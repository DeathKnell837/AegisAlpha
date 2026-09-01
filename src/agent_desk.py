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
