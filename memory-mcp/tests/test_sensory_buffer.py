"""Tests for SensoryBuffer (Phase 1)."""

import asyncio

import pytest

from memory_mcp.sensory_buffer import SensoryBuffer


@pytest.mark.asyncio
async def test_add_and_get():
    """基本的な追加・取得."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entry = await buffer.add(
        content="Test image",
        sensory_type="visual",
        metadata={"file_path": "/tmp/test.jpg"},
    )

    assert entry.content == "Test image"
    assert entry.sensory_type == "visual"
    assert entry.metadata["file_path"] == "/tmp/test.jpg"

    entries = await buffer.get_all()
    assert len(entries) == 1
    assert entries[0].id == entry.id
    assert entries[0].content == "Test image"


@pytest.mark.asyncio
async def test_get_by_id():
    """IDでエントリ取得."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entry1 = await buffer.add("Entry 1", "text")
    entry2 = await buffer.add("Entry 2", "text")

    found = await buffer.get_by_id(entry1.id)
    assert found is not None
    assert found.id == entry1.id
    assert found.content == "Entry 1"

    not_found = await buffer.get_by_id("non-existent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_remove():
    """エントリ削除."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entry = await buffer.add("Test entry", "text")
    assert buffer.size() == 1

    removed = await buffer.remove(entry.id)
    assert removed is True
    assert buffer.size() == 0

    # 存在しないIDの削除
    removed_again = await buffer.remove(entry.id)
    assert removed_again is False


@pytest.mark.asyncio
async def test_ttl_expiration():
    """TTL切れで自動削除される."""
    buffer = SensoryBuffer(ttl_sec=1, max_entries=10)  # 1秒TTL

    await buffer.add("Entry 1", "text")
    assert buffer.size() == 1

    # 1.5秒待機
    await asyncio.sleep(1.5)

    # cleanup実行
    removed = await buffer.cleanup_expired()
    assert removed == 1
    assert buffer.size() == 0


@pytest.mark.asyncio
async def test_get_all_auto_cleanup():
    """get_all時にTTL切れが自動削除される."""
    buffer = SensoryBuffer(ttl_sec=1, max_entries=10)

    await buffer.add("Entry 1", "text")
    await buffer.add("Entry 2", "text")
    assert buffer.size() == 2

    # 1.5秒待機
    await asyncio.sleep(1.5)

    # get_allで自動cleanup
    entries = await buffer.get_all()
    assert len(entries) == 0
    assert buffer.size() == 0


@pytest.mark.asyncio
async def test_max_entries():
    """件数上限で古いものから削除."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=3)

    entry1 = await buffer.add("Entry 1", "text")
    entry2 = await buffer.add("Entry 2", "text")
    entry3 = await buffer.add("Entry 3", "text")
    entry4 = await buffer.add("Entry 4", "text")  # entry1が削除される

    entries = await buffer.get_all()
    assert len(entries) == 3
    assert entry1.id not in [e.id for e in entries]
    assert entry2.id in [e.id for e in entries]
    assert entry3.id in [e.id for e in entries]
    assert entry4.id in [e.id for e in entries]


@pytest.mark.asyncio
async def test_max_entries_order():
    """件数上限超過時、新しいものから順に保持される."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=5)

    # 10個追加（最後の5個が残る）
    entries_added = []
    for i in range(10):
        entry = await buffer.add(f"Entry {i}", "text")
        entries_added.append(entry)

    # 最新5個のみ残っている
    entries = await buffer.get_all()
    assert len(entries) == 5

    # 新しい順に取得される（9, 8, 7, 6, 5）
    assert entries[0].content == "Entry 9"
    assert entries[1].content == "Entry 8"
    assert entries[2].content == "Entry 7"
    assert entries[3].content == "Entry 6"
    assert entries[4].content == "Entry 5"


@pytest.mark.asyncio
async def test_concurrent_access():
    """並行アクセス."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=100)

    async def add_entries():
        for i in range(10):
            await buffer.add(f"Entry {i}", "text")

    # 10個のタスクを並行実行
    await asyncio.gather(*[add_entries() for _ in range(10)])

    # 合計100個追加される
    assert buffer.size() == 100


@pytest.mark.asyncio
async def test_to_dict_conversion():
    """エントリのISO文字列変換."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entry = await buffer.add(
        content="Test entry",
        sensory_type="visual",
        metadata={"file_path": "/tmp/test.jpg"},
    )

    dict_data = entry.to_dict()
    assert dict_data["id"] == entry.id
    assert dict_data["content"] == "Test entry"
    assert dict_data["sensory_type"] == "visual"
    assert isinstance(dict_data["created_at"], str)  # ISO文字列
    assert isinstance(dict_data["expires_at"], str)  # ISO文字列
    assert dict_data["metadata"] == {"file_path": "/tmp/test.jpg"}


@pytest.mark.asyncio
async def test_empty_buffer():
    """空のバッファ."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entries = await buffer.get_all()
    assert len(entries) == 0
    assert buffer.size() == 0

    removed = await buffer.cleanup_expired()
    assert removed == 0


@pytest.mark.asyncio
async def test_metadata_optional():
    """メタデータは省略可能."""
    buffer = SensoryBuffer(ttl_sec=60, max_entries=10)

    entry = await buffer.add("Test entry", "text")
    assert entry.metadata == {}
