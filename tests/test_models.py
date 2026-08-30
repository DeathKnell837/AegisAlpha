# tests/test_models.py
import pytest
from src.featherless_llm import OptionHypothesis, FeatherlessLLMEngine

def test_option_hypothesis_model():
    """Verify that OptionHypothesis correctly validates fields."""
    hyp = OptionHypothesis(
        symbol="SPY",
        regime="BULLISH",
        strategy="BULL_CALL_SPREAD",
        confidence=0.88,
        rationale="Strong upward momentum above 20d MA with expanding volume.",
        suggested_dte_target=14
    )
    assert hyp.symbol == "SPY"
    assert hyp.regime == "BULLISH"
    assert hyp.confidence == 0.88
    assert hyp.suggested_dte_target == 14

def test_featherless_llm_initialization():
    """Verify FeatherlessLLMEngine initializes with correct base url and model."""
    engine = FeatherlessLLMEngine()
    assert engine.api_key != ""
    assert "Qwen" in engine.model or "Mistral" in engine.model




