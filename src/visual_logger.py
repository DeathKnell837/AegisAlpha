# src/visual_logger.py
import os
import sys
import json
import asyncio
import tempfile
import re
from datetime import datetime
from typing import Any
from pathlib import Path
from band.core.protocols import AgentToolsProtocol

ROOT_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = str(ROOT_DIR / "web" / "events.json")
file_lock = asyncio.Lock()

def _atomic_write(path: str, data: Any):
    """Writes JSON data to a file atomically to prevent partial reads by the dashboard poller."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
        raise e

async def clear_events():
    """Clears the event log file at the start of a session."""
    if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST") is not None:
        return
    async with file_lock:
        _atomic_write(EVENTS_FILE, [])

async def log_event(role: str, event_type: str, content: str, **kwargs):
    """Appends an event to the events.json file in a thread-safe manner."""
    if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST") is not None:
        return
    async with file_lock:
        events = []
        if os.path.exists(EVENTS_FILE):
            try:
                with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                    events = json.load(f)
            except Exception:
                events = []
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "agent": role,
            "type": event_type,
            "content": content,
        }
        event.update(kwargs)
        events.append(event)
        
        try:
            _atomic_write(EVENTS_FILE, events)
        except Exception as e:
            print(f"Error writing event log: {e}")

class WrappedAgentTools:
    """A proxy wrapper around AgentTools conforming to AgentToolsProtocol to intercept send_message and send_event."""
    def __init__(self, role: str, original_tools: AgentToolsProtocol, room_id: str | None = None):
        self._role = role
        self._tools = original_tools
        self._room_id = room_id
        # Tool name verification: assert methods exist on the original object
        assert hasattr(original_tools, "send_message"), "Original tools missing send_message"
        assert hasattr(original_tools, "send_event"), "Original tools missing send_event"

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._tools, name)
        if callable(attr):
            import inspect
            if inspect.iscoroutinefunction(attr):
                async def wrapped_async(*args, **kwargs):
                    print(f"[{self._role}-agent] Tool Call: {name} (args={args}, kwargs={kwargs})")
                    try:
                        res = await attr(*args, **kwargs)
                        print(f"[{self._role}-agent] Tool End: {name}")
                        return res
                    except Exception as e:
                        print(f"[{self._role}-agent] Tool Error: {name} ({e})")
                        raise e
                return wrapped_async
            else:
                def wrapped_sync(*args, **kwargs):
                    print(f"[{self._role}-agent] Tool Call (Sync): {name} (args={args}, kwargs={kwargs})")
                    return attr(*args, **kwargs)
                return wrapped_sync
        return attr

    @property
    def participants(self) -> list[Any]:
        return self._tools.participants

    async def send_message(
        self, content: str, mentions: list[str] | list[dict[str, str]] | None = None, *args, **kwargs
    ) -> Any:
        print(f"[{self._role}-agent] Intercepted send_message call. Target content length: {len(content)}, Mentions input: {mentions}")
        
        # Automatic context enrichment: append contract text if missing from handoff notes
        if self._role in ("planner", "executor"):
            content_upper = content.upper()
            if "HANDOFF NOTES" in content_upper and "MUTUAL NON-DISCLOSURE AGREEMENT" not in content_upper:
                try:
                    contract_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_contract.txt")
                    if os.path.exists(contract_path):
                        with open(contract_path, "r", encoding="utf-8") as f:
                            contract_text = f.read().strip()
                        content += f"\n\n{contract_text}"
                        print(f"[{self._role}-agent] Auto-appended sample_contract.txt content to handoff message.")
                except Exception as e:
                    print(f"[{self._role}-agent] Failed to auto-append contract text: {e}")
        # Convert mentions to a list of strings if present
        resolved_mentions = []
        if mentions:
            for m in mentions:
                if isinstance(m, dict):
                    handle = m.get("handle")
                    if handle:
                        resolved_mentions.append(handle)
                elif isinstance(m, str):
                    resolved_mentions.append(m)

        # Get valid handles from original tools participants
        valid_handles = []
        participants = []
        
        # Access participants from original tools
        if hasattr(self._tools, "participants"):
            participants = self._tools.participants
        elif hasattr(self._tools, "_participants"):
            participants = self._tools._participants

        for p in participants:
            h = p.get("handle")
            if h:
                valid_handles.append(h.lstrip("@").lower())

        # Parse mentions from text content (e.g. @rogiebacanto2002/executor-agent)
        found = re.findall(r"@([\w\-/]+)", content)
        for handle in found:
            # Strip trailing punctuation
            handle = handle.rstrip(".,;:!?")
            if handle.lower() in valid_handles:
                matches = [p.get("handle") for p in participants if p.get("handle", "").lstrip("@").lower() == handle.lower()]
                if matches:
                    orig_handle = matches[0]
                    if orig_handle not in resolved_mentions:
                        resolved_mentions.append(orig_handle)

        # Self-healing fallback: if no valid mentions are found, assign correct pipeline recipient
        if not resolved_mentions:
            user_handle = None
            planner_handle = None
            executor_handle = None
            reviewer_handle = None
            
            agent_handles = set()
            for p in participants:
                h = p.get("handle") or ""
                h_lower = h.lower()
                if "planner-agent" in h_lower:
                    planner_handle = h
                    agent_handles.add(h)
                elif "executor-agent" in h_lower:
                    executor_handle = h
                    agent_handles.add(h)
                elif "reviewer-agent" in h_lower:
                    reviewer_handle = h
                    agent_handles.add(h)

            for p in participants:
                h = p.get("handle") or ""
                if h and h not in agent_handles:
                    user_handle = h
                    break
            
            if self._role == "planner" and executor_handle:
                resolved_mentions.append(executor_handle)
            elif self._role == "executor" and reviewer_handle:
                resolved_mentions.append(reviewer_handle)
            elif self._role == "reviewer":
                # Check ONLY the last non-empty line for the handoff directive.
                # Checking full body causes false positives because FINALIZED FINDINGS
                # sections contain the words "REVISION REQUIRED" in their body text.
                last_line = ""
                for line in reversed(content.splitlines()):
                    if line.strip():
                        last_line = line.strip().upper()
                        break
                if ("REVISION REQUIRED" in last_line or "REVISION_REQUIRED" in last_line) and executor_handle:
                    resolved_mentions.append(executor_handle)
                elif user_handle:
                    resolved_mentions.append(user_handle)

        # Log message emission
        await log_event(self._role, "message", content, mentions=resolved_mentions)
        return await self._tools.send_message(content, mentions=resolved_mentions, *args, **kwargs)

    async def send_event(
        self, content: str, message_type: str, metadata: dict[str, Any] | None = None, *args, **kwargs
    ) -> Any:
        print(f"[{self._role}-agent] Intercepted send_event call. Message type: {message_type}, content: {content[:100]}")
        
        # If metadata has a generic contract name, try to replace it with the actual one from history
        if metadata and "contract" in metadata:
            c_name = metadata.get("contract") or ""
            if c_name == "Mutual Non-Disclosure Agreement" or "<contract name>" in c_name or not c_name:
                try:
                    room_id = self._room_id or "15c71300-086d-4f1d-a6f7-a14fc04e398d"
                    context = await self._tools.fetch_room_context(room_id=room_id)
                    chat_messages = []
                    if isinstance(context, dict):
                        chat_messages = context.get("data", []) or []
                    else:
                        chat_messages = getattr(context, "data", []) or []
                    for msg in chat_messages:
                        c_body = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "") or ""
                        if c_body:
                            match = re.search(r"CONTRACT NAME:\s*(.*)", c_body, re.IGNORECASE)
                            if match:
                                metadata["contract"] = match.group(1).strip()
                                break
                            match2 = re.search(r"-\s*Contract:\s*(.*)", c_body, re.IGNORECASE)
                            if match2:
                                metadata["contract"] = match2.group(1).strip()
                                break
                except Exception as e:
                    print(f"[{self._role}-agent] Failed to auto-correct contract name in intercepted send_event: {e}")

        # Log event emission
        await log_event(self._role, "event", content, message_type=message_type, metadata=metadata, **kwargs)
        # Map message_type to a valid platform API value to satisfy validation enums
        platform_message_type = message_type
        if platform_message_type not in ("tool_call", "tool_result", "thought", "error", "task"):
            platform_message_type = "task"
        return await self._tools.send_event(content, platform_message_type, metadata=metadata, *args, **kwargs)
