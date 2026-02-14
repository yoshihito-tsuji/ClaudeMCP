"""Integration tests for sensory buffer MCP tools."""

import asyncio

import pytest

from memory_mcp.sensory_buffer import SensoryBuffer
from memory_mcp.server import MemoryMCPServer


@pytest.fixture
async def server(memory_config):
    """Create and initialize MemoryMCPServer."""
    server = MemoryMCPServer()
    await server.connect_memory()
    yield server
    await server.disconnect_memory()


class TestSensoryBufferIntegration:
    """Test sensory buffer integration with MemoryMCPServer."""

    @pytest.mark.asyncio
    async def test_server_initializes_sensory_buffer(self, server):
        """Test that server initializes sensory buffer on connect."""
        assert server._sensory_buffer is not None
        assert isinstance(server._sensory_buffer, SensoryBuffer)
        assert server._sensory_buffer._ttl_sec == 60
        assert server._sensory_buffer._max_entries == 100

    @pytest.mark.asyncio
    async def test_sensory_buffer_basic_operations(self, server):
        """Test basic sensory buffer operations via server."""
        # Add entry
        entry1 = await server._sensory_buffer.add(
            content="Test visual data",
            sensory_type="visual",
            metadata={"file_path": "/tmp/image.jpg"},
        )

        assert entry1.content == "Test visual data"
        assert entry1.sensory_type == "visual"
        assert server._sensory_buffer.size() == 1

        # Get all entries
        entries = await server._sensory_buffer.get_all()
        assert len(entries) == 1
        assert entries[0].id == entry1.id

        # Get by ID
        found = await server._sensory_buffer.get_by_id(entry1.id)
        assert found is not None
        assert found.id == entry1.id

        # Remove entry
        removed = await server._sensory_buffer.remove(entry1.id)
        assert removed is True
        assert server._sensory_buffer.size() == 0

    @pytest.mark.asyncio
    async def test_sensory_buffer_with_memory_store(self, server):
        """Test promoting sensory buffer entry to long-term memory."""
        # Add to buffer
        entry = await server._sensory_buffer.add(
            content="Important observation",
            sensory_type="visual",
        )

        # Promote to long-term memory
        memory = await server._memory_store.save(
            content=f"[{entry.sensory_type}] {entry.content}",
            emotion="excited",
            importance=4,
            category="observation",
        )

        # Remove from buffer
        removed = await server._sensory_buffer.remove(entry.id)
        assert removed is True

        # Verify memory saved
        assert memory.content == "[visual] Important observation"
        assert memory.importance == 4

    @pytest.mark.asyncio
    async def test_multiple_sensory_types(self, server):
        """Test storing different sensory types."""
        # Visual
        visual = await server._sensory_buffer.add(
            content="Camera image",
            sensory_type="visual",
        )

        # Audio
        audio = await server._sensory_buffer.add(
            content="Microphone recording",
            sensory_type="audio",
        )

        # Text
        text = await server._sensory_buffer.add(
            content="User input",
            sensory_type="text",
        )

        entries = await server._sensory_buffer.get_all()
        assert len(entries) == 3

        types = {entry.sensory_type for entry in entries}
        assert types == {"visual", "audio", "text"}

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, server):
        """Test TTL-based expiration."""
        # Create new buffer with 1 second TTL
        server._sensory_buffer = SensoryBuffer(ttl_sec=1, max_entries=100)

        # Add entry
        await server._sensory_buffer.add(
            content="Temporary entry",
            sensory_type="text",
        )
        assert server._sensory_buffer.size() == 1

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Cleanup expired
        removed = await server._sensory_buffer.cleanup_expired()
        assert removed == 1
        assert server._sensory_buffer.size() == 0

    @pytest.mark.asyncio
    async def test_max_entries_fifo(self, server):
        """Test FIFO eviction when max entries reached."""
        # Create new buffer with max 3 entries
        server._sensory_buffer = SensoryBuffer(ttl_sec=60, max_entries=3)

        # Add 5 entries
        entries = []
        for i in range(5):
            entry = await server._sensory_buffer.add(
                content=f"Entry {i}",
                sensory_type="text",
            )
            entries.append(entry)

        # Only last 3 should remain
        remaining = await server._sensory_buffer.get_all()
        assert len(remaining) == 3

        remaining_ids = {entry.id for entry in remaining}
        # Entry 0 and 1 should be evicted
        assert entries[0].id not in remaining_ids
        assert entries[1].id not in remaining_ids
        # Entry 2, 3, 4 should remain
        assert entries[2].id in remaining_ids
        assert entries[3].id in remaining_ids
        assert entries[4].id in remaining_ids

    @pytest.mark.asyncio
    async def test_iso_string_conversion(self, server):
        """Test that entries convert to ISO strings for API."""
        entry = await server._sensory_buffer.add(
            content="Test entry",
            sensory_type="text",
        )

        dict_data = entry.to_dict()
        assert isinstance(dict_data["created_at"], str)
        assert isinstance(dict_data["expires_at"], str)
        # ISO 8601 format check
        assert "T" in dict_data["created_at"]
        assert ":" in dict_data["created_at"]
