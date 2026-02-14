"""Short-term memory for intermediate storage with auto-promotion.

短期記憶: 感覚バッファから昇格された記憶や直接保存された記憶を中期的に保持。
TTL（1時間デフォルト）と件数上限（50件デフォルト）で自動削除。
重要度が閾値以上の場合、自動的に長期記憶に昇格される。
内部時刻はUTC datetime、API境界でISO文字列に変換。
"""

import asyncio
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

from .types import ShortTermMemoryEntry


class ShortTermMemory:
    """短期記憶（中期保存、TTL + 件数上限 + 重要度管理）.

    Args:
        ttl_sec: TTL（秒）デフォルト3600秒（1時間）
        max_entries: 最大件数（デフォルト50件）
        auto_promote_threshold: 自動昇格の重要度閾値（デフォルト4）

    特徴:
        - TTL: 指定秒数で自動削除
        - 件数上限: 超過時は古いものから削除（deque maxlen）
        - 重要度管理: 閾値以上で自動昇格対象
        - スレッドセーフ: asyncio.Lock
        - 内部時刻: UTC datetime
    """

    def __init__(
        self,
        ttl_sec: int = 3600,
        max_entries: int = 50,
        auto_promote_threshold: int = 4,
    ):
        self._ttl_sec = ttl_sec
        self._max_entries = max_entries
        self._auto_promote_threshold = auto_promote_threshold
        self._buffer: deque[ShortTermMemoryEntry] = deque(maxlen=max_entries)
        self._lock = asyncio.Lock()

    async def add(
        self,
        content: str,
        emotion: str = "neutral",
        importance: int = 3,
        category: str = "daily",
        origin: str = "direct",
        metadata: dict | None = None,
    ) -> ShortTermMemoryEntry:
        """短期記憶に追加（TTL + 件数上限で自動削除）.

        Args:
            content: 記憶内容
            emotion: 感情（デフォルト: neutral）
            importance: 重要度1-5（デフォルト: 3）
            category: カテゴリ（デフォルト: daily）
            origin: 起源（"sensory_buffer" or "direct"、デフォルト: direct）
            metadata: 追加情報

        Returns:
            追加されたエントリ
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self._ttl_sec)

        entry = ShortTermMemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            created_at=now,
            expires_at=expires_at,
            emotion=emotion,
            importance=importance,
            category=category,
            origin=origin,
            metadata=metadata or {},
        )

        async with self._lock:
            # dequeのmaxlenで自動的に古いものが削除される
            self._buffer.append(entry)

        return entry

    async def get_all(self) -> list[ShortTermMemoryEntry]:
        """全エントリ取得（TTL切れは自動削除）.

        Returns:
            有効なエントリのリスト（新しい順）
        """
        await self.cleanup_expired()

        async with self._lock:
            return list(reversed(self._buffer))

    async def get_by_id(self, entry_id: str) -> ShortTermMemoryEntry | None:
        """IDでエントリ取得.

        Args:
            entry_id: エントリID

        Returns:
            エントリ、見つからないorTTL切れならNone
        """
        await self.cleanup_expired()

        async with self._lock:
            for entry in self._buffer:
                if entry.id == entry_id:
                    return entry
        return None

    async def remove(self, entry_id: str) -> bool:
        """エントリを削除.

        Args:
            entry_id: エントリID

        Returns:
            削除成功ならTrue
        """
        async with self._lock:
            for i, entry in enumerate(self._buffer):
                if entry.id == entry_id:
                    del self._buffer[i]
                    return True
        return False

    async def cleanup_expired(self) -> int:
        """TTL切れを削除.

        Returns:
            削除件数
        """
        now = datetime.now(timezone.utc)
        removed_count = 0

        async with self._lock:
            # dequeから期限切れを削除（古い順にチェック）
            while self._buffer and self._buffer[0].expires_at <= now:
                self._buffer.popleft()
                removed_count += 1

        return removed_count

    async def get_auto_promote_candidates(self) -> list[ShortTermMemoryEntry]:
        """自動昇格の候補を取得（重要度が閾値以上）.

        Returns:
            自動昇格対象のエントリリスト
        """
        await self.cleanup_expired()

        async with self._lock:
            candidates = [
                entry
                for entry in self._buffer
                if entry.importance >= self._auto_promote_threshold
            ]
            return candidates

    def should_auto_promote(self, entry: ShortTermMemoryEntry) -> bool:
        """エントリが自動昇格対象かどうかを判定.

        Args:
            entry: 判定対象のエントリ

        Returns:
            自動昇格対象ならTrue
        """
        return entry.importance >= self._auto_promote_threshold

    def size(self) -> int:
        """現在のバッファサイズ.

        Returns:
            エントリ数
        """
        return len(self._buffer)
