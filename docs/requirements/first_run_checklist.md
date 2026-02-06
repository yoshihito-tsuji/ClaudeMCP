# Tapo C210 到着後チェックリスト (macOS)

## 1. 事前準備

- Tapo C210本体と電源アダプタを準備する
- スマートフォンに「TP-Link Tapo」アプリを用意する
- Macとカメラが同じWi-Fiに接続されていることを確認する

## 2. Tapoアプリでの初期設定

- アプリでカメラを追加し、Wi-Fi接続まで完了させる
- ファームウェアを最新に更新する
- 「カメラのアカウント」を作成する（ローカルアカウント）
- IPアドレスを確認する
- ルーター側でDHCP予約を行い、IP固定を推奨する
- 「サードパーティ連携」がある場合はオンにする

## 3. macOS側の疎通確認

- MacからカメラIPへ疎通確認を行う

```bash
ping -c 3 <camera-ip>
```

- RTSPポートが開いているか確認する（任意）

```bash
nc -zv <camera-ip> 554
```

## 4. プロジェクト側の準備

- 依存関係をインストールする

```bash
cd wifi-cam-mcp
uv sync
```

- 環境変数を設定する

```bash
cp .env.example .env
```

- `.env` に以下を設定する

```
TAPO_CAMERA_HOST=<camera-ip>
TAPO_USERNAME=<camera-local-username>
TAPO_PASSWORD=<camera-local-password>
```

## 5. Claude Code設定

- `.mcp.json` に wifi-cam を追加する
- 例は `wifi-cam-mcp/README.md` の Claude Code セクションを参照する

## 6. 記録

- カメラIP、ローカルアカウント名、初期動作の結果をメモする

