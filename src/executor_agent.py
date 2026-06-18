# src/executor_agent.py
import asyncio
from src.agent_factory import build_agent

async def main():
    agent = build_agent("executor")
    print("[executor-agent] Connecting and listening for mentions...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
