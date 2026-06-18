# tests/test_models.py
import pytest
from src.models import get_model_for_role

def test_model_mappings():
    for role in ["planner", "executor", "reviewer"]:
        llm = get_model_for_role(role)
        assert llm.model_name is not None
        if role == "reviewer":
            assert llm.openai_api_base == "https://api.featherless.ai/v1"
            assert llm.temperature == 0.1
        else:
            assert llm.openai_api_base == "https://api.featherless.ai/v1"
            assert llm.temperature == 0.1


