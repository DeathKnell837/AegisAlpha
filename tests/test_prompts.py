# tests/test_prompts.py
import pytest
from src.prompts import get_planner_prompt, get_executor_prompt, get_reviewer_prompt

def test_planner_prompt_handoff():
    prompt = get_planner_prompt()
    assert "@rogiebacanto2002/executor-agent" in prompt
    assert "band_send_event" in prompt

def test_executor_prompt_handoff():
    prompt = get_executor_prompt()
    assert "@rogiebacanto2002/reviewer-agent" in prompt
    assert "band_send_event" in prompt

def test_reviewer_prompt_handoff():
    prompt = get_reviewer_prompt()
    assert "@rogiebacanto2002/executor-agent" in prompt
    assert "<human-handle>" in prompt or "@" in prompt
    assert "band_send_event" in prompt

