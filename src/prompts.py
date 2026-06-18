# src/prompts.py
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(filename: str) -> str:
    """Reads a prompt text file and returns its content as a string."""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found at {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_planner_prompt() -> str:
    return load_prompt("planner_prompt.txt")

def get_executor_prompt() -> str:
    return load_prompt("executor_prompt.txt")

def get_reviewer_prompt() -> str:
    return load_prompt("reviewer_prompt.txt")
