# tests/test_config.py
import pytest
from src.config import get_config

def test_load_config():
    """Verify that configuration parses properly and has required fields."""
    cfg = get_config()
    assert cfg.rest_url is not None
    assert cfg.ws_url is not None
    assert cfg.featherless_api_key is not None

def test_agent_credentials():
    """Verify credentials exist for all 3 agents."""
    cfg = get_config()
    for role in ["planner", "executor", "reviewer"]:
        agent_id, api_key, handle = cfg.get_agent_credentials(f"{role}_agent")
        assert agent_id is not None
        assert api_key is not None
        assert handle is not None
        assert handle.startswith("@")
