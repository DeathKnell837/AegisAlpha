# tests/test_models.py
import os
import pytest
from unittest.mock import patch
from src.models import get_model_for_role

@patch.dict(os.environ, {"USE_MOCK_LLM": "false", "FEATHERLESS_API_KEY": "fake_key", "AIMLAPI_KEY": "fake_key", "USE_AIMLAPI": "false"})
def test_model_mappings_default():
    for role in ["planner", "executor", "reviewer"]:
        llm = get_model_for_role(role)
        assert llm.model_name is not None
        assert llm.openai_api_base == "https://api.featherless.ai/v1"
        assert llm.temperature == 0.1

@patch.dict(os.environ, {"USE_MOCK_LLM": "false", "FEATHERLESS_API_KEY": "fake_key", "AIMLAPI_KEY": "fake_key", "USE_AIMLAPI": "true"})
def test_model_mappings_aiml():
    for role in ["planner", "executor", "reviewer"]:
        llm = get_model_for_role(role)
        assert llm.model_name is not None
        if role == "reviewer":
            assert llm.openai_api_base == "https://api.aimlapi.com/v1"
        else:
            assert llm.openai_api_base == "https://api.featherless.ai/v1"
        assert llm.temperature == 0.1




