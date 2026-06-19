# scripts/combined_server.py
import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os
import sys
import threading
import asyncio
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import agent runner components
from src.agent_factory import build_agent
from src.visual_logger import clear_events
from scripts.server import CustomHandler

# Run agents concurrently in an asyncio loop
async def start_agents():
    print("Starting all 3 agents (Planner, Executor, Reviewer) concurrently in the background...")
    await clear_events()
    
    # Run all agents in parallel
    await asyncio.gather(
        run_agent("planner"),
        run_agent("executor"),
        run_agent("reviewer")
    )

async def run_agent(role: str):
    while True:
        try:
            agent = build_agent(role)
            print(f"[{role}-agent] Initialized successfully. Starting listener loop...")
            await agent.run()
        except Exception as e:
            print(f"[{role}-agent] ERROR: {e}. Retrying in 10 seconds...", file=sys.stderr)
            await asyncio.sleep(10)

def run_async_loop():
    # Set up asyncio event loop for the agents
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_agents())
    except Exception as e:
        print(f"Agents loop failed: {e}", file=sys.stderr)

def main():
    # Get port from environment (Render sets PORT env)
    PORT = int(os.environ.get("PORT", 3000))
    
    # Start agents in a background thread
    agent_thread = threading.Thread(target=run_async_loop, daemon=True)
    agent_thread.start()
    
    # Start HTTP server in the main thread
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Combined server started on port {PORT} (HTTP server + Agents background thread)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping combined server. Goodbye!")

if __name__ == "__main__":
    main()
