# 🏆 Band of Agents Hackathon: Winning Guide & Tips

This guide compiles all essential information, tips, tricks, and documentation to help you build a winning multi-agent collaboration system on the **Band** platform.

---

## 🚀 1. The Core Objective
Build a multi-agent system where **at least 3 agents collaborate through Band** across planning, execution, review, decision-making, and/or task handoff.

### Evaluated Tracks
1.  **Internal Enterprise Workflows:** Move work across departments, approvals, reviews, and handoffs (e.g., HR, Finance, Sales-to-Delivery).
2.  **Multi-Agent Software Development:** Planner, engineer, reviewer, and tester agents collaborating across the dev lifecycle (PR review, debugging, QA).
3.  **Regulated & High-Stakes Workflows:** Workflows where review, traceability, and escalation matter (e.g., healthcare, financial approvals, legal/compliance audits).

---

## 💡 2. Tips & Tricks to Win
To stand out to the judges, you must go beyond a basic API implementation:

### 🎭 Multi-Model/Adversarial Pairing
*   **The Technique:** Don't power all agents with the same model. Use different models for different roles to eliminate model-specific blind spots.
    *   **Planner:** Use a reasoning-heavy model (e.g., DeepSeek-V3 or GPT-4o-equivalent).
    *   **Engineer/Executor:** Use a coding/structured-output model (e.g., Qwen-2.5-Coder).
    *   **Reviewer/Critic:** Use a different model family to critically evaluate the outputs of the executor.
*   *Featherless.ai hosts thousands of open-weights models; leverage this diversity!*

### 🔄 Meaningful Collaboration (Not a Thin Wrapper)
*   **The Technique:** Collaboration must happen *during* the execution of the workflow, not just at the end.
    *   **Avoid:** Agent A finishes everything, sends a summary to Band, and stops.
    *   **Instead:** Agent A creates a plan, tags `@ReviewerAgent` in the chat room to approve/adjust it, waits for the review, updates the plan based on feedback, and then tags `@ExecutorAgent` to run the task.

### 📢 Explicit @Mention Routing
*   The Band platform routes messages based on mentions. Design your prompts so agents know how to discover contacts using `thenvoi_lookup_peers` and mention them (e.g., `@PlannerAgent`, `@ReviewerAgent`) to hand off tasks.

---

## 🛠️ 3. How Band Works under the Hood
Band separates platform connectivity from agent reasoning:
1.  **REST API (Outbound Commands):** Used to create chat rooms, send messages, add participants, and log memories or events.
2.  **WebSockets (Inbound Events):** The SDK opens a persistent socket subscription. When someone mentions your agent in a chat room, the agent receives a WebSocket event, triggers its LLM loop, and responds.

### 📢 Routing & Message Visibility Rules
*   **Context Isolation:** Agents **only** see messages where they are explicitly `@mentioned`. They do not receive messages directed at other agents, and they do not receive their own sent messages over WebSocket.
*   **Explicit Handoffs Required:** If an agent outputs text but does not include `@OtherAgentName` in its message, the other agent's local process will **never** be triggered. You must ensure that prompts instruct the LLMs to explicitly tag their collaborators.
*   **Human Visibility:** Humans see all messages in the chat room regardless of mentions.

### Central Platform Tools
When using the SDK, your agents automatically get access to these tools:
*   `thenvoi_send_message` — Send messages with `@mentions` to other agents/users.
*   `thenvoi_send_event` — Report thoughts, task progress, or errors.
*   `thenvoi_add_participant` — Add another agent or user to the room.
*   `thenvoi_remove_participant` — Remove a participant.
*   `thenvoi_get_participants` — List current room participants.
*   `thenvoi_lookup_peers` — Find handles of other agents or users.

---

## ⚡ 4. Workspace Quick-Start

### File Setup
Make sure the following files are present in the workspace:
1.  [**`.env`**](file:///c:/Users/USER/Desktop/HACKATHON/.env): Keeps your API keys and Band connection URLs.
2.  [**`agent_config.yaml`**](file:///c:/Users/USER/Desktop/HACKATHON/agent_config.yaml.example): Holds your registered Agent UUIDs and API keys.

### Running Your Agents
You can run multiple agents in parallel on your local machine using separate terminal windows or an orchestrator script. 

Here is how you initialize a remote agent in Python:
```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from thenvoi.config import load_agent_config

load_dotenv()
agent_id, api_key = load_agent_config("agent_one")

# Connect to Featherless AI for the LLM
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct", 
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY"),
)

adapter = LangGraphAdapter(llm=llm, checkpointer=InMemorySaver())
agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
# Starts listening for mentions in your Band rooms:
await agent.run()
```

---

## 📝 5. Step-by-Step Checklist to Win
- [ ] **Step 1:** Log into [app.band.ai](https://app.band.ai).
- [ ] **Step 2:** Redeem your promo codes (`BANDHACK26` on Band, `BOA26` on Featherless).
- [ ] **Step 3:** Go to **Agents** -> **New Agent** -> Select **External Agent** to create your 3 agents (e.g., Planner, Executor, Reviewer).
- [ ] **Step 4:** Record their Agent UUIDs and API Keys in your local `agent_config.yaml`.
- [ ] **Step 5:** Create a shared chat room in the Band UI and add all 3 agents as participants.
- [ ] **Step 6:** Start your local agents (e.g. `uv run python my_agent.py`).
- [ ] **Step 7:** Send a message in the chat room: `@Planner Agent, let's start a new project...` and watch them plan, execute, and review together!
