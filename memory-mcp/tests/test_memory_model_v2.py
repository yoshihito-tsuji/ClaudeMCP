"""Regression tests for Memory Model V2 backward compatibility.

These tests ensure that when MEMORY_MODEL_V2=false (default),
the system behaves exactly like Phase 1 (before Phase 2 changes).
"""

import os

import pytest

from memory_mcp.config import MemoryConfig
from memory_mcp.server import MemoryMCPServer


class TestMemoryModelV2BackwardCompatibility:
    """Test that MEMORY_MODEL_V2=false maintains Phase 1 behavior."""

    def test_config_defaults_to_v1_mode(self):
        """Test that default config has MEMORY_MODEL_V2=false."""
        # Without setting env var, should default to false
        config = MemoryConfig.from_env()
        assert config.memory_model_v2 is False

    def test_config_reads_v2_flag_from_env(self, monkeypatch):
        """Test that MEMORY_MODEL_V2 env var is read correctly."""
        # Test true values
        for true_value in ["true", "True", "TRUE", "1", "yes"]:
            monkeypatch.setenv("MEMORY_MODEL_V2", true_value)
            config = MemoryConfig.from_env()
            assert config.memory_model_v2 is True, f"Failed for value: {true_value}"

        # Test false values
        for false_value in ["false", "False", "FALSE", "0", "no", ""]:
            monkeypatch.setenv("MEMORY_MODEL_V2", false_value)
            config = MemoryConfig.from_env()
            assert config.memory_model_v2 is False, f"Failed for value: {false_value}"

    def test_config_v2_parameters_have_defaults(self):
        """Test that Phase 2 config parameters have sensible defaults."""
        config = MemoryConfig.from_env()
        assert config.shortterm_ttl_sec == 3600  # 1 hour
        assert config.shortterm_max_entries == 50
        assert config.auto_promote_threshold == 4

    def test_config_v2_parameters_from_env(self, monkeypatch):
        """Test that Phase 2 config can be customized via env vars."""
        monkeypatch.setenv("SHORTTERM_TTL_SEC", "7200")
        monkeypatch.setenv("SHORTTERM_MAX_ENTRIES", "100")
        monkeypatch.setenv("AUTO_PROMOTE_THRESHOLD", "5")

        config = MemoryConfig.from_env()
        assert config.shortterm_ttl_sec == 7200
        assert config.shortterm_max_entries == 100
        assert config.auto_promote_threshold == 5

    @pytest.mark.asyncio
    async def test_server_behavior_unchanged_in_v1_mode(self, memory_config):
        """Test that server behavior is unchanged when MEMORY_MODEL_V2=false."""
        # Ensure we're in V1 mode
        assert memory_config.memory_model_v2 is False

        # Create and connect server
        server = MemoryMCPServer()
        await server.connect_memory()

        try:
            # Verify Phase 1 components are initialized
            assert server._sensory_buffer is not None
            assert server._memory_store is not None
            assert server._episode_manager is not None
            assert server._sensory_integration is not None

            # In V1 mode, these Phase 2 components should NOT be initialized
            # (We'll add these attributes in Phase 2 implementation)
            # assert not hasattr(server, '_shortterm_memory') or server._shortterm_memory is None

        finally:
            await server.disconnect_memory()

    @pytest.mark.asyncio
    async def test_sensory_buffer_still_works_in_v1_mode(self, memory_config):
        """Test that sensory buffer (Phase 1) still works when V2 flag is false."""
        assert memory_config.memory_model_v2 is False

        server = MemoryMCPServer()
        await server.connect_memory()

        try:
            # Add to sensory buffer
            entry = await server._sensory_buffer.add(
                content="Test entry in V1 mode",
                sensory_type="text",
            )

            # Verify it works exactly like Phase 1
            assert entry.content == "Test entry in V1 mode"
            assert server._sensory_buffer.size() == 1

            # Get all entries
            entries = await server._sensory_buffer.get_all()
            assert len(entries) == 1

        finally:
            await server.disconnect_memory()


class TestMemoryModelV2ParameterValidation:
    """Test validation of Phase 2 configuration parameters."""

    def test_shortterm_ttl_must_be_positive(self, monkeypatch):
        """Test that SHORTTERM_TTL_SEC must be positive."""
        # Note: This test documents current behavior.
        # Validation should be added in Phase 2 implementation.
        monkeypatch.setenv("SHORTTERM_TTL_SEC", "-1")
        config = MemoryConfig.from_env()
        # Currently no validation - this will become -1
        # TODO: Add validation to raise ValueError for negative values
        assert config.shortterm_ttl_sec == -1  # Current behavior (should be validated)

    def test_shortterm_max_entries_must_be_positive(self, monkeypatch):
        """Test that SHORTTERM_MAX_ENTRIES must be positive."""
        monkeypatch.setenv("SHORTTERM_MAX_ENTRIES", "0")
        config = MemoryConfig.from_env()
        # Currently no validation
        # TODO: Add validation to raise ValueError for zero/negative values
        assert config.shortterm_max_entries == 0  # Current behavior (should be validated)

    def test_auto_promote_threshold_range(self, monkeypatch):
        """Test that AUTO_PROMOTE_THRESHOLD should be in valid importance range (1-5)."""
        monkeypatch.setenv("AUTO_PROMOTE_THRESHOLD", "10")
        config = MemoryConfig.from_env()
        # Currently no validation
        # TODO: Add validation to ensure 1 <= threshold <= 5
        assert config.auto_promote_threshold == 10  # Current behavior (should be validated)
