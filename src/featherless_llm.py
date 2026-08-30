# src/featherless_llm.py
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.config import get_config


class OptionHypothesis(BaseModel):
    symbol: str
    regime: str = Field(description="BULLISH, BEARISH, or NEUTRAL_VOLATILITY")
    strategy: str = Field(description="BULL_CALL_SPREAD, BEAR_PUT_SPREAD, or IRON_CONDOR")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    rationale: str = Field(description="Detailed macro, momentum, and volatility rationale")
    suggested_dte_target: int = Field(default=14, description="Optimal Days to Expiration")


class FeatherlessLLMEngine:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.featherless_api_key
        self.model = self.config.default_model

    def generate_options_hypothesis(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        chain_summary: Dict[str, Any]
    ) -> OptionHypothesis:
        """Calls Featherless AI to generate an options trading strategy hypothesis."""
        prompt = f"""You are the Lead Quantitative Options Strategist at an autonomous hedge fund.
Analyze the following asset and live option chain parameters to formulate an options trading hypothesis.

Underlying Asset: {symbol}
Current Price: ${market_data.get('price', 0.0)}
Trend Classification: {market_data.get('trend', 'UNKNOWN')}
5-Day MA: ${market_data.get('ma_5', 0.0)} | 20-Day MA: ${market_data.get('ma_20', 0.0)}
Annualized Realized Volatility: {market_data.get('realized_volatility_annual_pct', 0.0)}%
30-Day Range: ${market_data.get('low_30d', 0.0)} - ${market_data.get('high_30d', 0.0)}

Available Call Strikes: {[c['strike'] for c in chain_summary.get('calls', [])[:4]]}
Available Put Strikes: {[p['strike'] for p in chain_summary.get('puts', [])[:4]]}

REQUIREMENTS:
1. Choose ONE defined-risk strategy: BULL_CALL_SPREAD (if bullish), BEAR_PUT_SPREAD (if bearish), or IRON_CONDOR (if neutral/range-bound).
2. Return your decision ONLY as a valid, raw JSON object (NO markdown backticks, NO explanation outside JSON) with this exact schema:
{{
  "symbol": "{symbol}",
  "regime": "BULLISH",
  "strategy": "BULL_CALL_SPREAD",
  "confidence": 0.85,
  "rationale": "Concise rationale explaining trend and risk-reward profile.",
  "suggested_dte_target": 14
}}"""

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert quantitative options strategist. Output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 500,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.config.featherless_base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                content = data["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                parsed = json.loads(content)
                return OptionHypothesis(**parsed)
        except Exception as e:
            trend = market_data.get("trend", "RANGE_BOUND")
            if "BULLISH" in trend:
                strat, regime = "BULL_CALL_SPREAD", "BULLISH"
            elif "BEARISH" in trend:
                strat, regime = "BEAR_PUT_SPREAD", "BEARISH"
            else:
                strat, regime = "IRON_CONDOR", "NEUTRAL_VOLATILITY"

            return OptionHypothesis(
                symbol=symbol,
                regime=regime,
                strategy=strat,
                confidence=0.80,
                rationale=f"Technical trend: {trend}. Realized Volatility: {market_data.get('realized_volatility_annual_pct', 20)}%. Rule-based deterministic fallback.",
                suggested_dte_target=14
            )
