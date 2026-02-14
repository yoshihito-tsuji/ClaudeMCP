"""Tests for ShortTermMemory (Phase 2)."""

import asyncio

import pytest

from memory_mcp.short_term_memory import ShortTermMemory


@pytest.mark.asyncio
async def test_add_and_get():
    """基本的な追加・取得."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry = await memory.add(
        content="Test memory",
        emotion="happy",
        importance=3,
        category="daily",
        origin="direct",
        metadata={"test": "data"},
    )

    assert entry.content == "Test memory"
    assert entry.emotion == "happy"
    assert entry.importance == 3
    assert entry.category == "daily"
    assert entry.origin == "direct"
    assert entry.metadata == {"test": "data"}

    entries = await memory.get_all()
    assert len(entries) == 1
    assert entries[0].id == entry.id


@pytest.mark.asyncio
async def test_add_with_defaults():
    """デフォルト値での追加."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry = await memory.add(content="Test memory")

    assert entry.emotion == "neutral"
    assert entry.importance == 3
    assert entry.category == "daily"
    assert entry.origin == "direct"
    assert entry.metadata == {}


@pytest.mark.asyncio
async def test_get_by_id():
    """IDでエントリ取得."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry1 = await memory.add("Memory 1", importance=3)
    entry2 = await memory.add("Memory 2", importance=4)

    found = await memory.get_by_id(entry1.id)
    assert found is not None
    assert found.id == entry1.id
    assert found.content == "Memory 1"

    not_found = await memory.get_by_id("non-existent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_remove():
    """エントリ削除."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry = await memory.add("Test memory", importance=3)
    assert memory.size() == 1

    removed = await memory.remove(entry.id)
    assert removed is True
    assert memory.size() == 0

    # 存在しないIDの削除
    removed_again = await memory.remove(entry.id)
    assert removed_again is False


@pytest.mark.asyncio
async def test_ttl_expiration():
    """TTL切れで自動削除される."""
    memory = ShortTermMemory(ttl_sec=1, max_entries=10)  # 1秒TTL

    await memory.add("Memory 1", importance=3)
    assert memory.size() == 1

    # 1.5秒待機
    await asyncio.sleep(1.5)

    # cleanup実行
    removed = await memory.cleanup_expired()
    assert removed == 1
    assert memory.size() == 0


@pytest.mark.asyncio
async def test_get_all_auto_cleanup():
    """get_all時にTTL切れが自動削除される."""
    memory = ShortTermMemory(ttl_sec=1, max_entries=10)

    await memory.add("Memory 1", importance=3)
    await memory.add("Memory 2", importance=4)
    assert memory.size() == 2

    # 1.5秒待機
    await asyncio.sleep(1.5)

    # get_allで自動cleanup
    entries = await memory.get_all()
    assert len(entries) == 0
    assert memory.size() == 0


@pytest.mark.asyncio
async def test_max_entries():
    """件数上限で古いものから削除."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=3)

    entry1 = await memory.add("Memory 1", importance=3)
    entry2 = await memory.add("Memory 2", importance=3)
    entry3 = await memory.add("Memory 3", importance=4)
    entry4 = await memory.add("Memory 4", importance=5)  # entry1が削除される

    entries = await memory.get_all()
    assert len(entries) == 3
    assert entry1.id not in [e.id for e in entries]
    assert entry2.id in [e.id for e in entries]
    assert entry3.id in [e.id for e in entries]
    assert entry4.id in [e.id for e in entries]


@pytest.mark.asyncio
async def test_auto_promote_candidates():
    """自動昇格候補の取得."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10, auto_promote_threshold=4)

    # 重要度3（昇格対象外）
    entry1 = await memory.add("Low importance", importance=3)

    # 重要度4（昇格対象）
    entry2 = await memory.add("High importance", importance=4)

    # 重要度5（昇格対象）
    entry3 = await memory.add("Very high importance", importance=5)

    candidates = await memory.get_auto_promote_candidates()
    assert len(candidates) == 2
    assert entry1.id not in [c.id for c in candidates]
    assert entry2.id in [c.id for c in candidates]
    assert entry3.id in [c.id for c in candidates]


@pytest.mark.asyncio
async def test_should_auto_promote():
    """自動昇格判定."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10, auto_promote_threshold=4)

    entry_low = await memory.add("Low", importance=3)
    entry_threshold = await memory.add("Threshold", importance=4)
    entry_high = await memory.add("High", importance=5)

    assert memory.should_auto_promote(entry_low) is False
    assert memory.should_auto_promote(entry_threshold) is True
    assert memory.should_auto_promote(entry_high) is True


@pytest.mark.asyncio
async def test_concurrent_access():
    """並行アクセス."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=100)

    async def add_entries():
        for i in range(10):
            await memory.add(f"Memory {i}", importance=3)

    # 10個のタスクを並行実行
    await asyncio.gather(*[add_entries() for _ in range(10)])

    # 合計100個追加される
    assert memory.size() == 100


@pytest.mark.asyncio
async def test_to_dict_conversion():
    """エントリのISO文字列変換."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry = await memory.add(
        content="Test memory",
        emotion="excited",
        importance=4,
        category="observation",
        origin="sensory_buffer",
        metadata={"camera_position": {"pan": 0, "tilt": 0}},
    )

    dict_data = entry.to_dict()
    assert dict_data["id"] == entry.id
    assert dict_data["content"] == "Test memory"
    assert dict_data["emotion"] == "excited"
    assert dict_data["importance"] == 4
    assert dict_data["category"] == "observation"
    assert dict_data["origin"] == "sensory_buffer"
    assert isinstance(dict_data["created_at"], str)  # ISO文字列
    assert isinstance(dict_data["expires_at"], str)  # ISO文字列
    assert dict_data["metadata"] == {"camera_position": {"pan": 0, "tilt": 0}}


@pytest.mark.asyncio
async def test_origin_tracking():
    """起源追跡（sensory_buffer vs direct）."""
    memory = ShortTermMemory(ttl_sec=60, max_entries=10)

    entry_sensory = await memory.add("From sensory", importance=3, origin="sensory_buffer")
    entry_direct = await memory.add("Direct input", importance=4, origin="direct")

    entries = await memory.get_all()
    assert len(entries) == 2

    origins = {entry.origin for entry in entries}
    assert origins == {"sensory_buffer", "direct"}
