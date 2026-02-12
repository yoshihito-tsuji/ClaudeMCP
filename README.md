# Embodied Claude - AIに身体を与えるプロジェクト

安価なハードウェア（約4,000円〜）で、Claude に「目」「首」「耳」「声」「脳（長期記憶）」を与える MCP サーバー群です。外に連れ出して散歩もできます。

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
│       ├── server.py          # MCP サーバー実装
│       └── config.py          # 設定管理
│
├── memory-mcp/                # 長期記憶システム（Python）
│   └── src/memory_mcp/
│       ├── server.py          # MCP サーバー実装
│       ├── memory.py          # ChromaDB 操作
│       ├── types.py           # 型定義（Emotion, Category）
│       ├── config.py          # 設定管理
│       ├── episode.py         # エピソード管理
│       ├── sensory.py         # 感覚記憶
│       └── working_memory.py  # 作業記憶
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
├── docs/
│   ├── team_ops/              # 三者協働運用ドキュメント
│   └── requirements/          # 要件定義ドキュメント
│
├── LOG/                       # 作業ログ
├── autonomous-action.sh       # 自律行動スクリプト（cron用）
├── autonomous-mcp.json.example
├── CLAUDE.md                  # Claude Code プロジェクト指示
├── AGENTS.md                  # リポジトリガイドライン
├── DECISIONS.md               # 重要な確定事項一覧
└── .claude/                   # Claude Code ローカル設定
```

## 身体パーツ一覧

| MCP サーバー | 身体部位 | 機能 | 対応ハードウェア |
| --- | --- | --- | --- |
| [usb-webcam-mcp](./usb-webcam-mcp/) | 目 | USB カメラから画像取得 | nuroum V11 等 |
| [wifi-cam-mcp](./wifi-cam-mcp/) | 目・首・耳 | PTZ カメラ制御 + 音声認識 | TP-Link Tapo C210/C220 等 |
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
│             │   │             │   │             │   │ (体温感覚)  │
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

- **USB ウェブカメラ**（任意）: nuroum V11 等
- **Wi-Fi PTZ カメラ**（推奨）: TP-Link Tapo C210 または C220（約3,980円）
- **GPU**（音声認識用）: NVIDIA GPU（Whisper用、GeForceシリーズのVRAM 8GB以上推奨）

### ソフトウェア

- Python 3.10+
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

詳細なパラメータは各サーバーの README か `list_tools` を参照。

### usb-webcam-mcp（目）

| ツール | 説明 |
| --- | --- |
| `list_cameras` | 接続されているカメラの一覧 |
| `see` | 画像をキャプチャ |

### wifi-cam-mcp（目・首・耳）

| ツール | 説明 |
| --- | --- |
| `see` | 画像をキャプチャ |
| `look_left` / `look_right` | 左右にパン |
| `look_up` / `look_down` | 上下にチルト |
| `look_around` | 4方向を見回し |
| `listen` | 音声録音 + Whisper文字起こし |
| `camera_info` / `camera_presets` / `camera_go_to_preset` | デバイス情報・プリセット操作 |

右目/ステレオ視覚などの追加ツールは [wifi-cam-mcp/README.md](./wifi-cam-mcp/README.md) を参照。

### elevenlabs-t2s-mcp（声）

| ツール | 説明 |
| --- | --- |
| `say` | テキストを音声合成して発話 |

### memory-mcp（脳）

| ツール | 説明 |
| --- | --- |
| `remember` | 記憶を保存 |
| `search_memories` | セマンティック検索 |
| `recall` | 文脈に基づく想起 |
| `recall_with_associations` | 関連記憶も含めて想起 |
| `list_recent_memories` | 最近の記憶一覧 |
| `get_memory_stats` | 記憶の統計情報 |

行動記憶・連鎖・エピソード・感覚記憶・作業記憶などの詳細は [memory-mcp/README.md](./memory-mcp/README.md) を参照。

#### 行動記憶

| ツール | 説明 |
| --- | --- |
| `remember_action` | ツール実行結果を構造化して記録 |

#### 実装予定（Planned）

| ツール | 説明 | 備考 |
| --- | --- | --- |
| `recall_divergent` | 連想を発散させた想起 | 上流リポジトリで実装済み |
| `consolidate_memories` | 手動の再生・統合処理 | 上流リポジトリで実装済み |
| `get_association_diagnostics` | 連想探索の診断情報 | 上流リポジトリで実装済み |

**Emotion**: happy, sad, surprised, moved, excited, nostalgic, curious, neutral
**Category**: daily, philosophical, technical, memory, observation, feeling, conversation, action

### system-temperature-mcp（体温感覚・概日リズム）

| ツール | 説明 |
| --- | --- |
| `get_system_temperature` | システム温度を取得 |
| `get_current_time` | 現在時刻を取得 |
| `get_circadian_state` | 概日リズム状態を取得（daypart / 挨拶トーン / 観察間隔 / 記憶重要度バイアス） |

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
# WSLで音が出ない場合:
# ELEVENLABS_PLAYBACK=paplay
# ELEVENLABS_PULSE_SINK=1
# ELEVENLABS_PULSE_SERVER=unix:/mnt/wslg/PulseServer
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

詳細なセットアップ手順（スクリーンショット付き）は [原作リポジトリのREADME](https://github.com/kmizu/embodied-claude#tapo-%E3%82%AB%E3%83%A1%E3%83%A9%E3%81%AE%E8%A8%AD%E5%AE%9A%E3%83%8F%E3%83%9E%E3%82%8A%E3%82%84%E3%81%99%E3%81%84%E3%81%AE%E3%81%A7%E6%B3%A8%E6%84%8F) を参照。

## 使い方

Claude Code を起動すると、自然言語でカメラを操作できる：

```text
> 今何が見える？
（カメラでキャプチャして画像を分析）

> 左を見て
（カメラを左にパン）

> 上を向いて空を見せて
（カメラを上にチルト）

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

## 外に連れ出す（オプション）

モバイルバッテリーとスマホのテザリングがあれば、カメラを肩に乗せて外を散歩できます。

### 外出に必要なもの

- **大容量モバイルバッテリー**（40,000mAh 推奨）
- **USB-C PD → DC 9V 変換ケーブル**（Tapoカメラの給電用）
- **スマホ**（テザリング + VPN + 操作UI）
- **[Tailscale](https://tailscale.com/)**（VPN。カメラ → スマホ → 自宅PC の接続に使用）
- **[claude-code-webui](https://github.com/sugyan/claude-code-webui)**（スマホのブラウザから Claude Code を操作）

### 構成

```text
[Tapoカメラ(肩)] ──WiFi──> [スマホ(テザリング)]
                                    |
                              Tailscale VPN
                                    |
                            [自宅PC(Claude Code)]
                                    |
                            [claude-code-webui]
                                    |
                            [スマホのブラウザ] <-- 操作
```

RTSPの映像ストリームもVPN経由で自宅マシンに届くので、Claude Codeからはカメラが室内にあるのと同じ感覚で操作できます。

## 自律行動スクリプト（オプション）

**注意**: この機能は完全にオプションです。cron設定が必要で、定期的にカメラで撮影が行われるため、プライバシーに配慮して使用してください。

### 概要

`autonomous-action.sh` は、Claude に定期的な自律行動を与えるスクリプトです。10分ごとにカメラで部屋を観察し、変化があれば記憶に保存します。

### 自律行動のセットアップ

```bash
# MCP サーバー設定ファイルの作成
cp autonomous-mcp.json.example autonomous-mcp.json
# autonomous-mcp.json を編集してカメラの認証情報を設定

# 実行権限を付与
chmod +x autonomous-action.sh

# crontab に登録（10分ごと、オプション）
crontab -e
# */10 * * * * /path/to/embodied-claude/autonomous-action.sh
```

### 動作

- カメラで部屋を見回す
- 前回と比べて変化を検出（人の有無、明るさなど）
- 気づいたことを記憶に保存（category: observation）
- ログを `~/.claude/autonomous-logs/` に保存

### 概日リズム対応（Phase 1）

時間帯に応じて自律行動の振る舞いを調整できます。環境変数で有効化します。

| 環境変数 | デフォルト | 説明 |
| --- | --- | --- |
| `CIRCADIAN_ENABLED` | MCP: `true` / Shell: `false` | 概日リズム機能の有効化 |
| `CIRCADIAN_TIMEZONE` | `Asia/Tokyo` | タイムゾーン（MCP サーバー側） |
| `CIRCADIAN_MORNING_START` | `05:00` | 朝の開始時刻 |
| `CIRCADIAN_DAY_START` | `10:00` | 昼の開始時刻 |
| `CIRCADIAN_EVENING_START` | `18:00` | 夕方の開始時刻 |
| `CIRCADIAN_NIGHT_START` | `22:00` | 夜の開始時刻 |

| daypart | 挨拶トーン | 観察間隔 | 記憶重要度バイアス |
| --- | --- | --- | --- |
| morning | bright | 10分 | +0 |
| day | normal | 10分 | +0 |
| evening | calm | 15分 | +1 |
| night | quiet | 30分 | +1 |

`get_circadian_state` ツール（system-temperature-mcp）で現在の状態を取得できます。

## 今後の展望

- **腕**: サーボモーターやレーザーポインターで「指す」動作
- **移動**: ロボット車輪で部屋を移動
- **長距離散歩**: 暖かい季節にもっと遠くへ

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

### 開発方法論

- **Dev-Rules**: [GitHub](https://github.com/yoshihito-tsuji/Dev-Rules) / [ローカル](../Dev-Rules/README.md)

**AI起動時（MUST）**: セッション開始時の必須参照手順（役割定義 → Dev-Rules → Best Practice → UI/UX心理学）は **[CLAUDE.md の「セッション開始時の必須参照」](./CLAUDE.md)** を参照。

### コミットメッセージ規則

- 日本語で記述し、変更の意図（why）を明確にする
- プレフィックス: `Add:` / `Update:` / `Fix:` / `Refactor:` / `Docs:` / `Security:`

## ライセンス

MIT License

## 謝辞

このプロジェクトは [kmizu](https://github.com/kmizu) 氏による、AIに身体性を与えるという実験的な試みです。
3,980円のカメラで始まった小さな一歩が、AIと人間の新しい関係性を探る旅になりました。

- [Rumia-Channel](https://github.com/Rumia-Channel) - ONVIF対応のプルリクエスト（[#5](https://github.com/kmizu/embodied-claude/pull/5)）
- [sugyan](https://github.com/sugyan) - [claude-code-webui](https://github.com/sugyan/claude-code-webui)（外出散歩時の操作UIとして使用）
