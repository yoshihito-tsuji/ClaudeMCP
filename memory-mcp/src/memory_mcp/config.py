"""Configuration for Memory MCP Server."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class MemoryConfig:
    """Memory storage configuration."""

    db_path: str
    collection_name: str
    # Phase 1: Sensory Buffer settings
    sensory_ttl_sec: int = 60  # Sensory buffer TTL (seconds)
    sensory_max_entries: int = 100  # Sensory buffer max entries
    # Phase 2: Memory Model V2 (Short-term Memory + Auto-promotion)
    memory_model_v2: bool = False  # Enable new memory model (default: off for compatibility)
    shortterm_ttl_sec: int = 3600  # Short-term memory TTL (1 hour)
    shortterm_max_entries: int = 50  # Short-term memory max entries
    auto_promote_threshold: int = 4  # Auto-promote to long-term if importance >= this value

    @classmethod
    def from_env(cls) -> "MemoryConfig":
        """Create config from environment variables."""
        default_path = str(Path.home() / ".claude" / "memories" / "chroma")

        return cls(
            db_path=os.getenv("MEMORY_DB_PATH", default_path),
            collection_name=os.getenv("MEMORY_COLLECTION_NAME", "claude_memories"),
            sensory_ttl_sec=int(os.getenv("SENSORY_TTL_SEC", "60")),
            sensory_max_entries=int(os.getenv("SENSORY_MAX_ENTRIES", "100")),
            # Phase 2: Memory Model V2
            memory_model_v2=os.getenv("MEMORY_MODEL_V2", "false").lower() in ("true", "1", "yes"),
            shortterm_ttl_sec=int(os.getenv("SHORTTERM_TTL_SEC", "3600")),
            shortterm_max_entries=int(os.getenv("SHORTTERM_MAX_ENTRIES", "50")),
            auto_promote_threshold=int(os.getenv("AUTO_PROMOTE_THRESHOLD", "4")),
        )


@dataclass(frozen=True)
class ServerConfig:
    """MCP Server configuration."""

    name: str = "memory-mcp"
    version: str = "0.1.0"

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create config from environment variables."""
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "memory-mcp"),
            version=os.getenv("MCP_SERVER_VERSION", "0.1.0"),
        )
