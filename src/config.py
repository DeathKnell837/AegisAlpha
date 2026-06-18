# src/config.py
import os
import re
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
CONFIG_PATH = ROOT_DIR / "agent_config.yaml"

# Load .env
if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))

def _expand_env(value):
    if isinstance(value, str):
        # Match both ${VAR} and $VAR
        return re.sub(r"\$\{(\w+)\}|\$(\w+)", lambda m: os.getenv(m.group(1) or m.group(2), ""), value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value

class Config:
    def __init__(self):
        # Platform settings
        self.rest_url = os.getenv("THENVOI_REST_URL", "https://app.band.ai/")
        self.ws_url = os.getenv("THENVOI_WS_URL", "wss://app.band.ai/api/v1/socket/websocket")
        
        # LLM Keys
        self.featherless_api_key = os.getenv("FEATHERLESS_API_KEY")
        self.aimlapi_key = os.getenv("AIMLAPI_KEY")
        
        if not self.featherless_api_key:
            raise ValueError("FEATHERLESS_API_KEY is missing from the environment!")
        if not self.aimlapi_key:
            raise ValueError("AIMLAPI_KEY is missing from the environment! (required for Reviewer agent)")
            
        # Agent Configurations
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"agent_config.yaml not found at {CONFIG_PATH}")
            
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw_yaml = yaml.safe_load(f) or {}
            self.agent_yaml = _expand_env(raw_yaml)

    def get_agent_credentials(self, role_key: str):
        """Returns (agent_id, api_key, handle) for a given agent role key."""
        config = self.agent_yaml.get(role_key)
        if not config:
            raise KeyError(f"Role key '{role_key}' not found in agent_config.yaml")
        
        agent_id = config.get("agent_id")
        api_key = config.get("api_key")
        handle = config.get("handle")
        
        if not agent_id or not api_key or not handle:
            raise ValueError(f"Incomplete credentials for '{role_key}' in agent_config.yaml")
            
        return agent_id, api_key, handle

# Singleton config instance
try:
    config = Config()
except Exception as e:
    # We catch errors during compile so tests can mock environments if needed
    config = None
    _config_error = e

def get_config():
    if config is None:
        raise _config_error
    return config

