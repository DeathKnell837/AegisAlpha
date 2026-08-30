# tests/test_config.py
import pytest
from src.config import get_config

def test_load_config():
    """Verify that AegisOptions configuration parses properly and has required fields."""
    cfg = get_config()
    assert cfg.alpaca_api_key != ""
    assert cfg.alpaca_secret_key != ""
    assert cfg.alpaca_account_id == "PA3PL5AZ85K6"
    assert cfg.featherless_api_key != ""
    assert cfg.risk.max_risk_per_trade_pct == 0.02
    assert cfg.risk.max_portfolio_options_pct == 0.20
    assert cfg.risk.max_daily_drawdown_pct == 0.03
