"""Sensory buffer for temporary storage of sensory data.

感覚バッファ: 一時的な感覚データ（視覚・聴覚・テキスト）の保存。
TTL（60秒デフォルト）と件数上限（100件デフォルト）で自動削除。
内部時刻はUTC datetime、API境界でISO文字列に変換。
"""

import asyncio
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

from .types import SensoryBufferEntry


class SensoryBuffer:
    """感覚バッファ（一時保存、TTL + 件数上限）.

    Args:
        ttl_sec: TTL（秒）デフォルト60秒
        max_entries: 最大件数（デフォルト100件）

    特徴:
        - TTL: 指定秒数で自動削除
        - 件数上限: 超過時は古いものから削除（deque maxlen）
        - スレッドセーフ: asyncio.Lock
        - 内部時刻: UTC datetime
    """

    def __init__(self, ttl_sec: int = 60, max_entries: int = 100):
        self._ttl_sec = ttl_sec
        self._max_entries = max_entries
        self._buffer: deque[SensoryBufferEntry] = deque(maxlen=max_entries)
        self._lock = asyncio.Lock()

    async def add(
        self,
        content: str,
        sensory_type: str,
        metadata: dict | None = None,
    ) -> SensoryBufferEntry:
        """感覚データを追加（TTL + 件数上限で自動削除）.

        Args:
            content: 簡潔な説明（「カメラ画像」等）
            sensory_type: "visual", "audio", "text"
            metadata: 追加情報（file_path, camera_position等）

        Returns:
            追加されたエントリ
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self._ttl_sec)

        entry = SensoryBufferEntry(
            id=str(uuid.uuid4()),
            content=content,
            created_at=now,
            expires_at=expires_at,
            sensory_type=sensory_type,
            metadata=metadata or {},
        )

        async with self._lock:
            # dequeのmaxlenで自動的に古いものが削除される
            self._buffer.append(entry)

        return entry

    async def get_all(self) -> list[SensoryBufferEntry]:
        """全エントリ取得（TTL切れは自動削除）.

        Returns:
            有効なエントリのリスト（新しい順）
        """
        await self.cleanup_expired()

        async with self._lock:
            return list(reversed(self._buffer))

    async def get_by_id(self, entry_id: str) -> SensoryBufferEntry | None:
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

    def size(self) -> int:
        """現在のバッファサイズ.

        Returns:
            エントリ数
        """
        return len(self._buffer)
