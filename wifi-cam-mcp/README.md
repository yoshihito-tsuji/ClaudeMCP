# wifi-cam-mcp

Tapo C210 等の Wi-Fi PTZ カメラを MCP 経由で制御し、AI に「目」「首」「耳」を与えるサーバー。

## 対応カメラ

- TP-Link Tapo C210 (3MP)
- TP-Link Tapo C220 (4MP)
- その他 Tapo シリーズのパン・チルト対応カメラ

## ツール一覧

### 基本ツール（10ツール）

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `see` | なし | 画像をキャプチャ |
| `look_left` | degrees? (1-90, default: 30) | 左にパン |
| `look_right` | degrees? (1-90, default: 30) | 右にパン |
| `look_up` | degrees? (1-90, default: 20) | 上にチルト |
| `look_down` | degrees? (1-90, default: 20) | 下にチルト |
| `look_around` | なし | 4方向（中央・左・右・上）を見回し |
| `camera_info` | なし | カメラのデバイス情報を取得 |
| `camera_presets` | なし | 保存済みプリセット位置の一覧 |
| `camera_go_to_preset` | preset_id (必須) | プリセット位置に移動 |
| `listen` | duration? (1-30秒, default: 5), transcribe? (default: true) | 音声録音 + Whisper文字起こし |

### ステレオ視覚ツール（13ツール、右カメラ設定時のみ）

右カメラ（`TAPO_RIGHT_CAMERA_HOST`）を設定すると、以下のツールが追加されます。

| ツール | パラメータ | 説明 |
| --- | --- | --- |
| `see_right` | なし | 右目で撮影 |
| `see_both` | なし | 左右同時撮影（ステレオ視覚） |
| `right_eye_look_left` | degrees? (1-90, default: 30) | 右目を左へ |
| `right_eye_look_right` | degrees? (1-90, default: 30) | 右目を右へ |
| `right_eye_look_up` | degrees? (1-90, default: 20) | 右目を上へ |
| `right_eye_look_down` | degrees? (1-90, default: 20) | 右目を下へ |
| `both_eyes_look_left` | degrees? (1-90, default: 30) | 両目を左へ（同期移動） |
| `both_eyes_look_right` | degrees? (1-90, default: 30) | 両目を右へ（同期移動） |
| `both_eyes_look_up` | degrees? (1-90, default: 20) | 両目を上へ（同期移動） |
| `both_eyes_look_down` | degrees? (1-90, default: 20) | 両目を下へ（同期移動） |
| `get_eye_positions` | なし | 両目の現在角度（pan/tilt）を取得 |
| `align_eyes` | なし | 右目を左目の位置に合わせる |
| `reset_eye_positions` | なし | 両目の位置追跡を (0, 0) にリセット |

## セットアップ

### 1. カメラの初期設定（Tapo アプリ）

1. スマホに「TP-Link Tapo」アプリをインストール
2. Tapo アカウントを作成してカメラを登録
3. **カメラのローカルアカウントを作成**（TP-Link クラウドアカウントとは別）
   - アプリ → カメラ選択 → 歯車 → 高度な設定 → カメラのアカウント
4. カメラの IP アドレスを確認（端末情報から。固定IP推奨）
5. サードパーティ連携をオンにする（「私」タブ → 音声アシスタント → サードパーティ連携）

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集：

```bash
TAPO_CAMERA_HOST=192.168.1.100    # カメラの IP アドレス
TAPO_USERNAME=your-name            # カメラのローカルアカウント名
TAPO_PASSWORD=your-password        # カメラのローカルアカウントパスワード
```

### 3. 依存関係インストール・起動

```bash
uv sync
uv run wifi-cam-mcp
```

音声認識（Whisper）を使う場合は追加依存が必要：

```bash
uv sync --extra transcribe
```

## 環境変数一覧

### 必須（左目 / メインカメラ）

| 変数 | 説明 |
| --- | --- |
| `TAPO_CAMERA_HOST` | カメラの IP アドレス |
| `TAPO_USERNAME` | カメラのローカルアカウント名 |
| `TAPO_PASSWORD` | カメラのローカルアカウントパスワード |

### オプション

| 変数 | デフォルト | 説明 |
| --- | --- | --- |
| `TAPO_STREAM_URL` | 自動検出 | RTSP ストリーム URL |
| `CAPTURE_DIR` | `/tmp/wifi-cam-mcp` | キャプチャ画像の保存先 |
| `CAPTURE_MAX_WIDTH` | `1920` | キャプチャ最大幅 |
| `CAPTURE_MAX_HEIGHT` | `1080` | キャプチャ最大高さ |

### ステレオ視覚（右目カメラ、オプション）

| 変数 | 説明 |
| --- | --- |
| `TAPO_RIGHT_CAMERA_HOST` | 右カメラの IP アドレス（設定するとステレオ有効） |
| `TAPO_RIGHT_USERNAME` | 右カメラのアカウント名（省略時は左カメラと共有） |
| `TAPO_RIGHT_PASSWORD` | 右カメラのパスワード（省略時は左カメラと共有） |
| `TAPO_RIGHT_STREAM_URL` | 右カメラの RTSP URL |

## MCP 設定例

### Claude Code（.mcp.json）

```json
{
  "mcpServers": {
    "wifi-cam": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/wifi-cam-mcp", "wifi-cam-mcp"],
      "env": {
        "TAPO_CAMERA_HOST": "192.168.1.100",
        "TAPO_USERNAME": "your-name",
        "TAPO_PASSWORD": "your-password"
      }
    }
  }
}
```

## トラブルシューティング

| 問題 | 対処 |
| --- | --- |
| カメラに接続できない | カメラと PC が同じネットワーク上にあるか確認。IP アドレスを Tapo アプリで再確認 |
| 認証エラー | カメラのローカルアカウント（TP-Link クラウドアカウントではない）の認証情報を確認 |
| 画像が取得できない | カメラのファームウェアを最新に更新、カメラを再起動 |

## 注意事項

- pytapo は非公式ライブラリのため、TP-Link の仕様変更で動作しなくなる可能性があります
- カメラはローカルネットワーク内からのみアクセス可能です
- 認証情報（.env ファイル）は絶対に Git にコミットしないでください

## ライセンス

MIT License
