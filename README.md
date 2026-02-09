# Embodied Claude - AIに身体を与えるプロジェクト

安価なハードウェア（約4,000円）で、Claude に「目」「首」「耳」「脳（長期記憶）」「声」を与える MCP サーバー群です。

> 原作: [kmizu/embodied-claude](https://github.com/kmizu/embodied-claude)

## コンセプト

従来の LLM は「見せてもらう」存在だったが、身体を持つことで「自分で見る」存在になる。
3,980円の Wi-Fi カメラで目と首は十分実現できる。本質（見る・動かす）だけ抽出したシンプルな構成。

## ディレクトリ構造

```text
embodied-claude/
├── usb-webcam-mcp/            # USB ウェブカメラ制御（Python）
│   └── src/usb_webcam_mcp/
│       └── server.py
│
├── wifi-cam-mcp/              # Wi-Fi PTZ カメラ制御（Python）
│   └── src/wifi_cam_mcp/
│       ├── server.py          # MCP サーバー実装
│       ├── camera.py          # Tapo カメラ制御
│       └── config.py          # 設定管理
│
├── elevenlabs-t2s-mcp/        # ElevenLabs TTS（Python）
│   └── src/elevenlabs_t2s_mcp/
│       └── server.py
│
├── memory-mcp/                # 長期記憶システム（Python）
│   └── src/memory_mcp/
│       ├── server.py          # MCP サーバー実装
│       ├── memory.py          # ChromaDB 操作
│       ├── types.py           # 型定義（Emotion, Category）
│       └── config.py          # 設定管理
│
├── system-temperature-mcp/    # 体温感覚（Python）
│   └── src/system_temperature_mcp/
│       └── server.py
│
├── installer/                 # PyInstaller ベース GUI インストーラー
│   └── src/installer/
│       ├── main.py
│       └── pages/             # ウィザード形式の各ページ
│
├── autonomous-action.sh       # 自律行動スクリプト（cron用）
├── autonomous-mcp.json.example
├── CLAUDE.md                  # Claude Code プロジェクト指示
├── AGENTS.md                  # リポジトリガイドライン
└── .claude/                   # Claude Code ローカル設定
```

## 身体パーツ一覧

| MCP サーバー | 身体部位 | 機能 | 対応ハードウェア |
| --- | --- | --- | --- |
| [usb-webcam-mcp](./usb-webcam-mcp/) | 目 | USB カメラから画像取得 | nuroum V11 等 |
| [wifi-cam-mcp](./wifi-cam-mcp/) | 目・首・耳 | PTZ カメラ制御 + 音声認識 | TP-Link Tapo C210/C220 |
| [elevenlabs-t2s-mcp](./elevenlabs-t2s-mcp/) | 声 | ElevenLabs で音声合成 | ElevenLabs API |
| [memory-mcp](./memory-mcp/) | 脳 | 長期記憶（セマンティック検索） | ChromaDB |
| [system-temperature-mcp](./system-temperature-mcp/) | 体温感覚 | システム温度監視 | Linux sensors |

## アーキテクチャ

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code                              │
│                    (MCP Client / AI Brain)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol (stdio)
          ┌───────────────┼───────────────┬───────────────┐
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ usb-webcam  │   │  wifi-cam   │   │   memory    │   │   system    │
│    -mcp     │   │    -mcp     │   │    -mcp     │   │ temperature │
│   (目)      │   │ (目/首/耳)  │   │   (脳)      │   │    -mcp     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ USB Webcam  │   │ Tapo Camera │   │  ChromaDB   │   │Linux Sensors│
│ (nuroum V11)│   │  (C210等)   │   │  (Vector)   │   │(/sys/class) │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

## 必要なもの

### ハードウェア

- **Wi-Fi PTZ カメラ**（推奨）: TP-Link Tapo C210 または C220（約3,980円）
- **USB ウェブカメラ**（任意）: nuroum V11 等
- **GPU**（音声認識用）: NVIDIA GPU（Whisper用、VRAM 8GB以上推奨）

### ソフトウェア

- Python 3.10+（system-temperature-mcp は 3.12+）
- uv（Python パッケージマネージャー）
- ffmpeg（画像・音声キャプチャ用）
- OpenCV（USB カメラ用）
- ElevenLabs API キー（音声合成用）

## 開発ガイドライン

### 共通ルール

- **パッケージマネージャー**: uv
- **テストフレームワーク**: pytest + pytest-asyncio
- **リンター**: ruff（行長 100）
- **非同期**: asyncio ベース
- **命名規則**: `snake_case`、テストファイルは `test_*.py`
- **インデント**: 4スペース

### 基本コマンド

```bash
# 依存関係インストール（各サブプロジェクトディレクトリで実行）
uv sync

# テスト実行（現在 memory-mcp のみ）
cd memory-mcp && uv run pytest

# リント
uv run ruff check .

# サーバー起動
uv run <server-name>
```

## MCP ツール一覧

### usb-webcam-mcp（目）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `list_cameras` | なし | 接続カメラ一覧 |
| `see` | camera_index?, width?, height? | 画像キャプチャ |

### wifi-cam-mcp（目・首・耳）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `see` | なし | 画像キャプチャ |
| `look_left` | degrees (1-90, default: 30) | 左パン |
| `look_right` | degrees (1-90, default: 30) | 右パン |
| `look_up` | degrees (1-90, default: 20) | 上チルト |
| `look_down` | degrees (1-90, default: 20) | 下チルト |
| `look_around` | なし | 4方向スキャン |
| `camera_info` | なし | デバイス情報 |
| `camera_presets` | なし | プリセット一覧 |
| `camera_go_to_preset` | preset_id | プリセット移動 |
| `listen` | duration (1-30秒), transcribe? | 音声録音 |

#### ステレオ視覚（右目カメラ対応時）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `see_right` | なし | 右目で撮影 |
| `see_both` | なし | 左右同時撮影 |
| `right_eye_look_*` | degrees | 右目の個別制御 |
| `both_eyes_look_*` | degrees | 両目の同時制御 |
| `get_eye_positions` | なし | 両目の角度を取得 |
| `align_eyes` | なし | 右目を左目に合わせる |
| `reset_eye_positions` | なし | 角度追跡をリセット |

### elevenlabs-t2s-mcp（声）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `say` | text, voice_id?, model_id?, output_format?, play_audio? | 音声合成して発話 |

### memory-mcp（脳）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `remember` | content, emotion?, importance?, category? | 記憶保存 |
| `search_memories` | query, n_results?, filters... | セマンティック検索 |
| `recall` | context, n_results? | 文脈に基づく想起 |
| `recall_with_associations` | context, n_results?, chain_depth? | 関連記憶も含めて想起 |
| `list_recent_memories` | limit?, category_filter? | 最近の記憶一覧 |
| `get_memory_stats` | なし | 統計情報 |
| `get_memory_chain` | memory_id, depth? | 記憶の連鎖を取得 |
| `link_memories` | source_id, target_id, link_type?, note? | 記憶をリンク |
| `get_causal_chain` | memory_id, direction?, max_depth? | 因果チェーン取得 |
| `create_episode` | title, memory_ids, participants?, auto_summarize? | エピソード作成 |
| `search_episodes` | query, n_results? | エピソード検索 |
| `get_episode_memories` | episode_id | エピソード内の記憶取得 |
| `save_visual_memory` | content, image_path, camera_position, emotion?, importance? | 画像付き記憶保存 |
| `save_audio_memory` | content, audio_path, transcript, emotion?, importance? | 音声付き記憶保存 |
| `recall_by_camera_position` | pan_angle, tilt_angle, tolerance? | カメラ角度で想起 |
| `get_working_memory` | n_results? | 作業記憶を取得 |
| `refresh_working_memory` | なし | 作業記憶を更新 |

**Emotion**: happy, sad, surprised, moved, excited, nostalgic, curious, neutral
**Category**: daily, philosophical, technical, memory, observation, feeling, conversation

### system-temperature-mcp（体温感覚）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `get_system_temperature` | なし | システム温度 |
| `get_current_time` | なし | 現在時刻 |

## セットアップ

### GUI インストーラー（推奨）

`installer/` ディレクトリに GUI インストーラーが用意されています。

```bash
cd installer
uv sync
uv run embodied-claude-installer
```

依存関係チェック、カメラ設定、MCP 設定の自動生成をウィザード形式で行えます。
詳細は [installer/README.md](./installer/README.md) を参照。

### 手動セットアップ

#### 1. 各 MCP サーバーの依存関係インストール

```bash
# 使用するサーバーのディレクトリで実行
cd wifi-cam-mcp && uv sync
cd memory-mcp && uv sync
cd elevenlabs-t2s-mcp && uv sync
# 必要に応じて他も
```

#### 2. 環境変数の設定

```bash
# Wi-Fi カメラ
cd wifi-cam-mcp
cp .env.example .env
# .env を編集してカメラの IP、ユーザー名、パスワードを設定

# ElevenLabs
cd elevenlabs-t2s-mcp
cp .env.example .env
# .env に ELEVENLABS_API_KEY を設定
```

#### 3. Claude Code 設定（.mcp.json）

```json
{
  "mcpServers": {
    "usb-webcam": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/embodied-claude/usb-webcam-mcp", "usb-webcam-mcp"]
    },
    "wifi-cam": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/embodied-claude/wifi-cam-mcp", "wifi-cam-mcp"],
      "env": {
        "TAPO_CAMERA_HOST": "192.168.1.xxx",
        "TAPO_USERNAME": "your-username",
        "TAPO_PASSWORD": "your-password"
      }
    },
    "memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/embodied-claude/memory-mcp", "memory-mcp"]
    },
    "elevenlabs-t2s": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/embodied-claude/elevenlabs-t2s-mcp", "elevenlabs-t2s"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Tapo カメラの設定（注意点）

1. Tapo アプリでカメラをセットアップ
2. **TP-Link クラウドアカウントではなく、カメラのローカルアカウントを作成する**
   - アプリ → カメラ選択 → 歯車 → 高度な設定 → カメラのアカウント
3. カメラの IP アドレスを確認（端末情報から確認可能、固定IP推奨）
4. サードパーティ連携をオンにする（「私」タブ → 音声アシスタント → サードパーティ連携）

## 使い方

Claude Code を起動すると、自然言語でカメラを操作できる：

```text
> 今何が見える？
（カメラでキャプチャして画像を分析）

> 左を見て
（カメラを左にパン）

> 周りを見回して
（4方向をスキャンして画像を返す）

> 何か聞こえる？
（音声を録音してWhisperで文字起こし）

> これ覚えておいて：コウタは眼鏡をかけてる
（長期記憶に保存）

> コウタについて何か覚えてる？
（記憶をセマンティック検索）

> 声で「おはよう」って言って
（音声合成で発話）
```

## 自律行動スクリプト（オプション）

定期的にカメラで部屋を観察し、変化があれば記憶に保存する機能です。

**注意**: プライバシーに配慮して使用してください。

```bash
# セットアップ
cp autonomous-mcp.json.example autonomous-mcp.json
# autonomous-mcp.json を編集してカメラの認証情報を設定

chmod +x autonomous-action.sh

# crontab に登録（10分ごと）
crontab -e
# */10 * * * * /path/to/embodied-claude/autonomous-action.sh
```

## 注意事項

### WSL2 環境

- **USB カメラ**: `usbipd` でカメラを WSL に転送する必要がある
- **温度センサー**: WSL2 では `/sys/class/thermal/` にアクセスできない
- **GPU**: CUDA は WSL2 でも利用可能（Whisper用）

### セキュリティ

- `.env` ファイルはコミットしない（.gitignore に追加済み）
- カメラパスワードは環境変数で管理
- ElevenLabs API キーは環境変数で管理
- 長期記憶は `~/.claude/memories/` に保存される

## 三者協働開発モデル

本プロジェクトは **Yoshihitoさん（プロジェクトオーナー）**、**Codex（アーキテクト）**、**Claude Code（実装エンジニア）** の三者協働体制で開発しています。

### 役割分担

| 役割 | 担当 | 責務 |
| --- | --- | --- |
| プロジェクトオーナー | Yoshihitoさん | 最終意思決定、要件定義、リリース判断 |
| アーキテクト | Codex | 上流設計、要件整理、アーキテクチャ策定 |
| 実装エンジニア | Claude Code | 実装、テスト、コードレビュー、LOG記録 |

### 意思決定フロー

```text
課題/要望の明確化（Yoshihitoさん）
    ↓
設計提案と影響整理（Codex）
    ↓
実装方針・見積もり共有（Claude Code）
    ↓
最終判断（Yoshihitoさん）
    ↓
記録（LOG / DECISIONS.md）
```

### コミュニケーションルール

- すべて日本語で記述
- AI発信メッセージは `From: / To:` 形式を使用
- 作業記録は `LOG/YYYY-MM-DD.md` に追記
- 重要な決定事項は `DECISIONS.md` に転記

### 開発プロセスドキュメント

| ドキュメント | 説明 |
| --- | --- |
| [三者協働ガイド](./docs/team_ops/triad_collaboration.md) | セッション開始手順、言語ルール、レビュー運用 |
| [Claude Code 役割定義](./docs/team_ops/claude_code_role.md) | Claude Code の責務、Startup Procedure、品質基準 |
| [Codex 役割定義](./docs/team_ops/codex_role.md) | Codex の責務、設計方針、Startup Procedure |
| [チームアーキテクチャ](./docs/team_ops/team_architecture.md) | 役割分担、意思決定フロー、エスカレーション基準 |
| [ログテンプレート](./docs/team_ops/LOG_TEMPLATE.md) | 日次ログの記入形式（5セクション） |
| [DECISIONS.md](./DECISIONS.md) | 重要な確定事項一覧 |

### 📚 開発方法論の詳細

- **GitHub版**: [Dev-Rules](https://github.com/yoshihito-tsuji/Dev-Rules)
- **ローカル版**: [../Dev-Rules/README.md](../Dev-Rules/README.md)
- **Codex向けガイド**: [../Dev-Rules/CODEX_ONBOARDING.md](../Dev-Rules/CODEX_ONBOARDING.md)
- **Claude Code Best Practice**: [../Dev-Rules/claude-code/README.md](../Dev-Rules/claude-code/README.md)
- **UI/UX心理学**: [../Dev-Rules/setup/ux-design-principles.md](../Dev-Rules/setup/ux-design-principles.md)

**AI起動時**: 役割定義（claude_code_role.md または codex_role.md）を読んだ後、Best Practice と UI/UX心理学も必ず確認してください。

### コミットメッセージ規則

- 日本語で記述し、変更の意図（why）を明確にする
- プレフィックス: `Add:` / `Update:` / `Fix:` / `Refactor:` / `Docs:` / `Security:`

## ライセンス

MIT License

## 謝辞

このプロジェクトは [kmizu](https://github.com/kmizu) 氏による、AIに身体性を与えるという実験的な試みです。
3,980円のカメラで始まった小さな一歩が、AIと人間の新しい関係性を探る旅になりました。
