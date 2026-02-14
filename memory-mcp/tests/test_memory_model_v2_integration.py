"""Integration tests for Memory Model V2 (Short-term Memory + Auto-promotion).

These tests verify that Phase 2 features work correctly when MEMORY_MODEL_V2=true.
"""

import asyncio

import pytest

from memory_mcp.config import MemoryConfig
from memory_mcp.server import MemoryMCPServer
from memory_mcp.short_term_memory import ShortTermMemory


@pytest.fixture
def v2_config(temp_db_path, monkeypatch):
    """Create a config with V2 enabled."""
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


class TestMemoryModelV2Integration:
    """Test Memory Model V2 integration with server."""

    @pytest.mark.asyncio
    async def test_server_initializes_shortterm_memory_in_v2_mode(self, v2_server):
        """Test that server initializes short-term memory when V2=true."""
        assert v2_server._shortterm_memory is not None
        assert isinstance(v2_server._shortterm_memory, ShortTermMemory)
        assert v2_server._shortterm_memory._ttl_sec == 60
        assert v2_server._shortterm_memory._max_entries == 10
        assert v2_server._shortterm_memory._auto_promote_threshold == 4

    @pytest.mark.asyncio
    async def test_shortterm_memory_basic_operations(self, v2_server):
        """Test basic short-term memory operations via server."""
        # Add to short-term memory
        entry = await v2_server._shortterm_memory.add(
            content="Test short-term memory",
            emotion="curious",
            importance=3,
            category="observation",
        )

        assert entry.content == "Test short-term memory"
        assert entry.importance == 3
        assert v2_server._shortterm_memory.size() == 1

        # Get all entries
        entries = await v2_server._shortterm_memory.get_all()
        assert len(entries) == 1
        assert entries[0].id == entry.id

    @pytest.mark.asyncio
    async def test_auto_promotion_candidates(self, v2_server):
        """Test that high-importance memories are identified for auto-promotion."""
        # Add low-importance memory (not auto-promoted)
        await v2_server._shortterm_memory.add(
            content="Low importance",
            importance=3,
        )

        # Add high-importance memory (auto-promoted)
        await v2_server._shortterm_memory.add(
            content="High importance",
            importance=5,
        )

        # Get candidates
        candidates = await v2_server._shortterm_memory.get_auto_promote_candidates()
        assert len(candidates) == 1
        assert candidates[0].content == "High importance"

    @pytest.mark.asyncio
    async def test_manual_promotion_from_shortterm_to_longterm(self, v2_server):
        """Test manually promoting short-term memory to long-term."""
        # Add to short-term
        entry = await v2_server._shortterm_memory.add(
            content="Important observation",
            emotion="excited",
            importance=4,
            category="observation",
        )

        # Promote to long-term
        memory = await v2_server._memory_store.save(
            content=entry.content,
            emotion=entry.emotion,
            importance=entry.importance,
            category=entry.category,
        )

        # Remove from short-term
        removed = await v2_server._shortterm_memory.remove(entry.id)
        assert removed is True

        # Verify saved to long-term
        assert memory.content == "Important observation"
        assert memory.importance == 4

    @pytest.mark.asyncio
    async def test_sensory_to_shortterm_to_longterm_flow(self, v2_server):
        """Test the full flow: sensory → short-term → long-term."""
        # 1. Add to sensory buffer
        sensory_entry = await v2_server._sensory_buffer.add(
            content="Camera detected motion",
            sensory_type="visual",
        )

        # 2. Promote to short-term memory
        shortterm_entry = await v2_server._shortterm_memory.add(
            content=f"[{sensory_entry.sensory_type}] {sensory_entry.content}",
            emotion="curious",
            importance=4,
            category="observation",
            origin="sensory_buffer",
        )

        # Verify in short-term
        assert shortterm_entry.origin == "sensory_buffer"
        assert v2_server._shortterm_memory.size() == 1

        # 3. Promote to long-term memory
        longterm_memory = await v2_server._memory_store.save(
            content=shortterm_entry.content,
            emotion=shortterm_entry.emotion,
            importance=shortterm_entry.importance,
            category=shortterm_entry.category,
        )

        # Clean up
        await v2_server._sensory_buffer.remove(sensory_entry.id)
        await v2_server._shortterm_memory.remove(shortterm_entry.id)

        # Verify in long-term
        assert longterm_memory.content == "[visual] Camera detected motion"
        assert longterm_memory.importance == 4

    @pytest.mark.asyncio
    async def test_ttl_expiration_in_shortterm(self, v2_server):
        """Test TTL expiration in short-term memory."""
        # Create new buffer with 1 second TTL
        v2_server._shortterm_memory = ShortTermMemory(ttl_sec=1, max_entries=10)

        # Add entry
        await v2_server._shortterm_memory.add(
            content="Temporary memory",
            importance=3,
        )
        assert v2_server._shortterm_memory.size() == 1

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Cleanup
        removed = await v2_server._shortterm_memory.cleanup_expired()
        assert removed == 1
        assert v2_server._shortterm_memory.size() == 0

    @pytest.mark.asyncio
    async def test_v1_components_still_work_in_v2_mode(self, v2_server):
        """Test that Phase 1 components still work when V2 is enabled."""
        # Sensory buffer should still work
        sensory_entry = await v2_server._sensory_buffer.add(
            content="Test sensory",
            sensory_type="text",
        )
        assert sensory_entry.content == "Test sensory"

        # Long-term memory should still work
        memory = await v2_server._memory_store.save(
            content="Test long-term",
            importance=3,
        )
        assert memory.content == "Test long-term"

        # Episode manager should still work
        episode = await v2_server._episode_manager.create_episode(
            title="Test episode",
            memory_ids=[memory.id],
        )
        assert episode.title == "Test episode"
