# tests/test_bootstrap.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agent_factory import InterceptLangGraphAdapter

class MockMsg:
    def __init__(self, id_val, sender_id, content=""):
        self.id = id_val
        self.sender_id = sender_id
        self.sender_name = "test_user"
        self.content = content

class MockTools:
    def __init__(self, room_data):
        self.room_data = room_data
        self.fetch_calls = 0
        self.send_event = AsyncMock()
        self.send_message = AsyncMock()
        self.participants = []

    async def fetch_room_context(self, room_id):
        self.fetch_calls += 1
        return {"data": self.room_data}

@pytest.mark.asyncio
async def test_bootstrap_caching_and_skipping():
    # Setup test data
    # planner agent ID is loaded from config during credentials fetch
    from src.config import get_config
    cfg = get_config()
    planner_id, _, _ = cfg.get_agent_credentials("planner_agent")

    room_id = "test_room_123"
    
    # Context has two messages: U1 (user) followed by P1 (planner response)
    room_data = [
        {"id": "msg_u1", "sender_id": "user_id_123", "sender_name": "User", "content": "hello"},
        {"id": "msg_p1", "sender_id": planner_id, "sender_name": "Planner", "content": "plan"}
    ]
    
    tools = MockTools(room_data)
    adapter = InterceptLangGraphAdapter(role="planner", llm=MagicMock())
    
    with patch("src.agent_factory.InterceptLangGraphAdapter._run_graph", new_callable=AsyncMock) as mock_run_graph:
        # 1. Processing an old message (msg_u1) during bootstrap
        msg_u1 = MockMsg("msg_u1", "user_id_123")
        await adapter.on_message(
            msg=msg_u1,
            tools=tools,
            history=[],
            participants_msg=None,
            contacts_msg=None,
            is_session_bootstrap=True,
            room_id=room_id
        )
        
        # It should have skipped/returned before calling _run_graph
        mock_run_graph.assert_not_called()
        assert tools.fetch_calls == 1  # Called fetch_room_context once
        
        # 2. Processing the latest message (msg_p1) which was sent by us (planner) during bootstrap
        msg_p1 = MockMsg("msg_p1", planner_id)
        await adapter.on_message(
            msg=msg_p1,
            tools=tools,
            history=[],
            participants_msg=None,
            contacts_msg=None,
            is_session_bootstrap=True,
            room_id=room_id
        )
        
        # It should have skipped again because it was sent by us
        mock_run_graph.assert_not_called()
        assert tools.fetch_calls == 1  # Cached: did not call fetch_room_context again
        
        # 3. Processing a non-bootstrap new message (from another user)
        msg_u2 = MockMsg("msg_u2", "user_id_123", content="new message")
        await adapter.on_message(
            msg=msg_u2,
            tools=tools,
            history=[],
            participants_msg=None,
            contacts_msg=None,
            is_session_bootstrap=False,
            room_id=room_id
        )
        
        # It should NOT skip this, it should process it and call _run_graph
        mock_run_graph.assert_called_once()
        # The cache should be cleared on is_session_bootstrap=False
        assert not hasattr(adapter, "_bootstrap_contexts") or room_id not in adapter._bootstrap_contexts
