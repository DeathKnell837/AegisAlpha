# tests/test_prompts.py -> test_alpaca_models.py
import pytest
from src.alpaca_service import AlpacaService

def test_alpaca_service_initialization():
    """Verify that AlpacaService initializes and loads credentials."""
    service = AlpacaService()
    assert service.trading_client is not None
    assert service.stock_data_client is not None
    assert service.option_data_client is not None

