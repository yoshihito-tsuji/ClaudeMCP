# elevenlabs-t2s-mcp

ElevenLabs API を使った音声合成 MCP サーバー。AI に「声」を与えます。

## ツール一覧

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `say` | text (必須), voice_id?, model_id?, output_format?, play_audio? | テキストを音声合成して発話 |

### say のパラメータ

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `text` | string | (必須) | 発話するテキスト |
| `voice_id` | string | 環境変数の値 | 使用する音声 ID |
| `model_id` | string | 環境変数の値 | 使用するモデル ID |
| `output_format` | string | 環境変数の値 | 出力フォーマット |
| `play_audio` | boolean | true | この端末で音声を再生するか |

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して API キーを設定：

```bash
ELEVENLABS_API_KEY=your-api-key
```

### 2. 依存関係インストール・起動

```bash
uv sync
uv run elevenlabs-t2s
```

## 環境変数一覧

### 必須

| 変数 | 説明 |
| --- | --- |
| `ELEVENLABS_API_KEY` | ElevenLabs API キー |

### オプション

| 変数 | デフォルト | 説明 |
| --- | --- | --- |
| `ELEVENLABS_VOICE_ID` | `uYp2UUDeS74htH10iY2e` | 音声 ID |
| `ELEVENLABS_MODEL_ID` | `eleven_v3` | モデル ID |
| `ELEVENLABS_OUTPUT_FORMAT` | `mp3_44100_128` | 出力フォーマット |
| `ELEVENLABS_PLAY_AUDIO` | `true` | 音声の自動再生 |
| `ELEVENLABS_SAVE_DIR` | `/tmp/elevenlabs-t2s` | 音声ファイルの保存先 |

### 再生バックエンド設定

| 変数 | デフォルト | 説明 |
| --- | --- | --- |
| `ELEVENLABS_PLAYBACK` | `auto` | 再生方法（`auto` / `paplay` / `elevenlabs` / `ffplay`） |
| `ELEVENLABS_PULSE_SINK` | なし | PulseAudio シンク ID（WSL 向け） |
| `ELEVENLABS_PULSE_SERVER` | 自動検出 | PulseAudio サーバー（WSL では `/mnt/wslg/PulseServer` を自動検出） |

`auto` モードでは `paplay` → `elevenlabs` → `ffplay` の順にフォールバックします。

## MCP 設定例

### Claude Code（.mcp.json）

```json
{
  "mcpServers": {
    "elevenlabs-t2s": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/elevenlabs-t2s-mcp", "elevenlabs-t2s"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

## ライセンス

MIT License
