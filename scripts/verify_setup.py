# scripts/verify_setup.py
import os
import sys
import asyncio
from pathlib import Path
from langchain_openai import ChatOpenAI

# Add root folder to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import get_config

async def test_llm_connectivity():
    cfg = get_config()
    if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
        print("[LLM] Checking Mock LLM connectivity...")
        print("   [SUCCESS] Mock LLM is active and ready.")
        return True
    print("[LLM] Checking Featherless.ai LLM connectivity...")
    try:
        llm = ChatOpenAI(
            model="Qwen/Qwen2.5-7B-Instruct",
            base_url="https://api.featherless.ai/v1",
            api_key=cfg.featherless_api_key,
        )
        response = await llm.ainvoke("Hello! Reply with 'OK'.")
        print(f"   [SUCCESS] Featherless responded: {response.content.strip()}")
        return True
    except Exception as e:
        print(f"   [FAILED] Could not connect to Featherless: {e}", file=sys.stderr)
        return False

def check_config():
    print("[CONFIG] Checking configuration files...")
    try:
        cfg = get_config()
        print(f"   [SUCCESS] Configuration loaded.")
        print(f"   REST URL: {cfg.rest_url}")
        print(f"   WS URL: {cfg.ws_url}")
        
        # Print configured credentials
        for role in ["planner", "executor", "reviewer"]:
            agent_id, api_key, handle = cfg.get_agent_credentials(f"{role}_agent")
            print(f"   - {role.capitalize()} Agent ID: {agent_id[:8]}... | Handle: {handle}")
        return True
    except Exception as e:
        print(f"   [FAILED] Configuration check: {e}", file=sys.stderr)
        return False

async def main():
    print("=== BAND OF AGENTS PRE-FLIGHT VERIFICATION ===\n")
    config_ok = check_config()
    print()
    llm_ok = await test_llm_connectivity()
    print()
    
    if config_ok and llm_ok:
        print(">>> ALL CHECKS PASSED! You are ready to start the agent network.")
        print("Run 'python scripts/run_all.py' to launch.")
    else:
        print(">>> SOME CHECKS FAILED. Please verify your keys and agent configuration before running.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

