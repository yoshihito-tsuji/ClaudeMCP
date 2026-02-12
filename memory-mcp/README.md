# memory-mcp

AI に長期記憶を与える MCP サーバー。ChromaDB によるセマンティック検索でセッションを超えて記憶を保持します。

## 機能

- セマンティック記憶保存（感情タグ・重要度・カテゴリ付き）
- 自然言語によるセマンティック検索・文脈想起
- 自動リンク（類似記憶の自動関連付け）
- エピソード記憶（一連の体験をまとめて管理）
- 感覚記憶（画像・音声データとの統合）
- 作業記憶（直近の記憶への高速アクセス）
- 因果リンク（記憶間の因果・関連関係の記録）

## ツール一覧（18ツール）

### 基本ツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `remember` | content (必須), emotion?, importance?, category?, auto_link?, link_threshold? | 記憶を保存 |
| `search_memories` | query (必須), n_results?, emotion_filter?, category_filter?, date_from?, date_to? | セマンティック検索 |
| `recall` | context (必須), n_results? | 文脈に基づく想起 |
| `list_recent_memories` | limit?, category_filter? | 最近の記憶一覧 |
| `get_memory_stats` | なし | 統計情報（カテゴリ・感情別の集計） |

### 連想・リンクツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `recall_with_associations` | context (必須), n_results?, chain_depth? (1-3) | 関連記憶も含めて想起 |
| `get_memory_chain` | memory_id (必須), depth? (1-5) | 記憶の連鎖を取得 |

### エピソード記憶ツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `create_episode` | title (必須), memory_ids (必須), participants?, auto_summarize? | エピソード作成 |
| `search_episodes` | query (必須), n_results? | エピソード検索 |
| `get_episode_memories` | episode_id (必須) | エピソード内の記憶を時系列で取得 |

### 感覚記憶ツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `save_visual_memory` | content (必須), image_path (必須), camera_position (必須), emotion?, importance? | 画像付き記憶を保存 |
| `save_audio_memory` | content (必須), audio_path (必須), transcript (必須), emotion?, importance? | 音声付き記憶を保存 |
| `recall_by_camera_position` | pan_angle (必須), tilt_angle (必須), tolerance? (default: 15) | カメラ角度で記憶を想起 |

### 作業記憶ツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `get_working_memory` | n_results? (default: 10) | 直近の記憶を高速取得 |
| `refresh_working_memory` | なし | 重要な長期記憶で作業記憶を更新 |

### 行動記憶ツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `remember_action` | tool_name (必須), parameters_summary (必須), result_summary (必須), status?, reasoning?, importance?, related_memory_id? | ツール実行結果を構造化して記録 |

### 因果リンクツール

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `link_memories` | source_id (必須), target_id (必須), link_type?, note? | 記憶間にリンクを作成 |
| `get_causal_chain` | memory_id (必須), direction? (backward/forward), max_depth? (1-5) | 因果チェーンを辿る |

## パラメータ詳細

### remember の追加パラメータ

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `auto_link` | boolean | true | 類似する既存記憶への自動リンク |
| `link_threshold` | number | 0.8 | 自動リンクの類似度閾値（0-2、低いほど厳密） |

### LinkType（link_memories で使用）

| 値 | 説明 |
| --- | --- |
| `similar` | 類似（自動リンクと同等） |
| `caused_by` | この記憶の原因（デフォルト） |
| `leads_to` | この記憶から派生 |
| `related` | 一般的な関連 |

### Emotion

`happy`, `sad`, `surprised`, `moved`, `excited`, `nostalgic`, `curious`, `neutral`

### Category

`daily`, `philosophical`, `technical`, `memory`, `observation`, `feeling`, `conversation`, `action`

## セットアップ

### 依存関係インストール・起動

```bash
uv sync
uv run memory-mcp
```

### 設定

環境変数または `.env` ファイルで設定：

| 変数 | デフォルト | 説明 |
| --- | --- | --- |
| `MEMORY_DB_PATH` | `~/.claude/memories/chroma` | ChromaDB の保存先 |
| `MEMORY_COLLECTION_NAME` | `claude_memories` | コレクション名 |

## MCP 設定例

### Claude Code（.mcp.json）

```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/memory-mcp", "memory-mcp"]
    }
  }
}
```

## 開発

```bash
# 開発用依存関係インストール
uv sync --all-extras

# テスト実行
uv run pytest

# リント
uv run ruff check src/
```

## ライセンス

MIT License
