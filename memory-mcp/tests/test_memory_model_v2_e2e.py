"""E2E tests for Memory Model V2 using public tool interface.

Tests that verify Phase 2 features work correctly via the public MCP tool interface.
"""

import pytest

from memory_mcp.config import MemoryConfig
from memory_mcp.server import MemoryMCPServer


@pytest.fixture
def v2_config(temp_db_path, monkeypatch):
    """Create a config with V2 enabled."""
    monkeypatch.setenv("MEMORY_DB_PATH", temp_db_path)
    monkeypatch.setenv("MEMORY_MODEL_V2", "true")
    monkeypatch.setenv("SHORTTERM_TTL_SEC", "60")
    monkeypatch.setenv("SHORTTERM_MAX_ENTRIES", "10")
    monkeypatch.setenv("AUTO_PROMOTE_THRESHOLD", "4")

    return MemoryConfig.from_env()


@pytest.fixture
async def v2_server(v2_config):
    """Create and initialize server with V2 enabled."""
    server = MemoryMCPServer()
    await server.connect_memory()
    yield server
    await server.disconnect_memory()


@pytest.fixture
def v1_config(temp_db_path, monkeypatch):
    """Create a config with V1 mode (default)."""
    monkeypatch.setenv("MEMORY_DB_PATH", temp_db_path)
    monkeypatch.setenv("MEMORY_MODEL_V2", "false")
    return MemoryConfig.from_env()


@pytest.fixture
async def v1_server(v1_config):
    """Create and initialize server with V1 mode."""
    server = MemoryMCPServer()
    await server.connect_memory()
    yield server
    await server.disconnect_memory()


class TestRememberToolE2E:
    """E2E tests for remember tool via public interface."""

    @pytest.mark.asyncio
    async def test_remember_saves_to_shortterm_in_v2_mode(self, v2_server):
        """Test that remember tool saves to short-term memory in V2 mode."""
        # Call remember tool via public interface
        result = await v2_server._handle_tool_call(
            name="remember",
            arguments={
                "content": "E2E test memory via remember tool",
                "emotion": "curious",
                "importance": 3,
                "category": "daily",
            },
        )

        # Verify response indicates V2 mode
        assert len(result) == 1
        response_text = result[0].text
        assert "short-term storage (V2 mode)" in response_text
        assert "E2E test memory via remember tool" not in response_text  # ID is in response, not content

        # Verify actually saved to short-term memory
        entries = await v2_server._shortterm_memory.get_all()
        assert len(entries) == 1
        assert entries[0].content == "E2E test memory via remember tool"
        assert entries[0].origin == "direct"
        assert entries[0].importance == 3

        # Verify NOT saved to long-term memory yet
        memories = await v2_server._memory_store.list_recent(limit=10)
        assert len(memories) == 0

    @pytest.mark.asyncio
    async def test_remember_saves_to_longterm_in_v1_mode(self, v1_server):
        """Test that remember tool saves directly to long-term memory in V1 mode."""
        # Call remember tool via public interface
        result = await v1_server._handle_tool_call(
            name="remember",
            arguments={
                "content": "E2E test memory in V1 mode",
                "emotion": "neutral",
                "importance": 3,
                "category": "daily",
                "auto_link": False,
            },
        )

        # Verify response indicates V1 mode (no "short-term storage" message)
        assert len(result) == 1
        response_text = result[0].text
        assert "Memory saved!" in response_text
        assert "short-term storage" not in response_text

        # Verify saved to long-term memory
        memories = await v1_server._memory_store.list_recent(limit=10)
        assert len(memories) == 1
        assert memories[0].content == "E2E test memory in V1 mode"


class TestPromoteSensoryToolE2E:
    """E2E tests for save_sensory and promote_sensory_to_memory tools via public interface."""

    @pytest.mark.asyncio
    async def test_promote_sensory_to_shortterm_in_v2_mode(self, v2_server):
        """Test that promote_sensory_to_memory promotes to short-term in V2 mode."""
        # 1. Save sensory data via public interface
        save_result = await v2_server._handle_tool_call(
            name="save_sensory",
            arguments={
                "content": "E2E test camera detection",
                "sensory_type": "visual",
                "metadata": {"camera_position": {"pan": 0, "tilt": 0}},
            },
        )

        # Extract entry ID from response
        response_text = save_result[0].text
        assert "Saved to sensory buffer!" in response_text
        # Extract ID from response (format: "ID: <id>")
        entry_id = response_text.split("ID: ")[1].split("\n")[0]

        # Verify in sensory buffer
        assert v2_server._sensory_buffer.size() == 1

        # 2. Promote to memory via public interface
        promote_result = await v2_server._handle_tool_call(
            name="promote_sensory_to_memory",
            arguments={
                "entry_id": entry_id,
                "emotion": "curious",
                "importance": 4,
                "category": "observation",
            },
        )

        # Verify response indicates V2 mode
        response_text = promote_result[0].text
        assert "short-term memory (V2 mode)" in response_text

        # Verify promoted to short-term memory
        entries = await v2_server._shortterm_memory.get_all()
        assert len(entries) == 1
        assert "[visual] E2E test camera detection" in entries[0].content
        assert entries[0].origin == "sensory_buffer"
        assert entries[0].importance == 4

        # Verify removed from sensory buffer
        assert v2_server._sensory_buffer.size() == 0

        # Verify NOT saved to long-term memory yet
        memories = await v2_server._memory_store.list_recent(limit=10)
        assert len(memories) == 0

    @pytest.mark.asyncio
    async def test_promote_sensory_to_longterm_in_v1_mode(self, v1_server):
        """Test that promote_sensory_to_memory promotes directly to long-term in V1 mode."""
        # 1. Save sensory data
        save_result = await v1_server._handle_tool_call(
            name="save_sensory",
            arguments={
                "content": "E2E test in V1 mode",
                "sensory_type": "visual",
            },
        )

        # Extract entry ID
        response_text = save_result[0].text
        entry_id = response_text.split("ID: ")[1].split("\n")[0]

        # 2. Promote to memory
        promote_result = await v1_server._handle_tool_call(
            name="promote_sensory_to_memory",
            arguments={
                "entry_id": entry_id,
                "emotion": "neutral",
                "importance": 3,
                "category": "observation",
            },
        )

        # Verify response indicates V1 mode
        response_text = promote_result[0].text
        assert "Promoted to long-term memory!" in response_text
        assert "short-term memory" not in response_text

        # Verify saved to long-term memory
        memories = await v1_server._memory_store.list_recent(limit=10)
        assert len(memories) == 1
        assert "[visual] E2E test in V1 mode" in memories[0].content
