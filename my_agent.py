import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from thenvoi.config import load_agent_config

async def run_remote_agent(config_name: str, model_name: str):
    load_dotenv()
    
    # Load agent ID and API key from agent_config.yaml
    agent_id, api_key = load_agent_config(config_name)

    # Initialize the LLM (using Featherless API endpoint and your API key)
    llm = ChatOpenAI(
        model=model_name,
        base_url="https://api.featherless.ai/v1",
        api_key=os.getenv("FEATHERLESS_API_KEY"),
    )

    # Create adapter
    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        custom_section=f"You are a collaborative agent named {config_name}. Work with other agents in the room to solve tasks.",
    )

    # Create and run the agent
    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )

    print(f"Agent {config_name} is running...")
    await agent.run()

if __name__ == "__main__":
    # Example: run agent_one using a Qwen model from Featherless
    # Update model_name to your desired model (e.g. "Qwen/Qwen2.5-7B-Instruct")
    asyncio.run(run_remote_agent("agent_one", "Qwen/Qwen2.5-7B-Instruct"))
