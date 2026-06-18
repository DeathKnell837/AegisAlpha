# scripts/run_all.py
import asyncio
import sys
from pathlib import Path

# Add root folder to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agent_factory import build_agent
from src.visual_logger import clear_events

async def run_agent(role: str):
    try:
        agent = build_agent(role)
        print(f"[{role}-agent] Initialized successfully. Starting listener loop...")
        await agent.run()
    except Exception as e:
        print(f"[{role}-agent] ERROR: {e}", file=sys.stderr)

async def main():
    print("Starting all 3 agents (Planner, Executor, Reviewer) concurrently...")
    print("Press Ctrl+C to stop the agent network.\n")
    
    # Clear visual event logs
    await clear_events()
    
    # Run all agents in parallel
    await asyncio.gather(
        run_agent("planner"),
        run_agent("executor"),
        run_agent("reviewer")
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping agent network. Goodbye!")

