# 三者協働ガイド

Embodied Claude では **Codex（設計・アーキテクチャ）**、**Claude Code（実装）**、**Yoshihitoさん（プロジェクトオーナー）** の三者で作業を進めます。本ドキュメントは協働ルールのまとめです。

## セッション開始前の確認手順

1. `README.md` でプロジェクト概要・目的・主要機能を把握する
2. `docs/team_ops/claude_code_role.md` / `docs/team_ops/codex_role.md` で自分の役割とコミュニケーション形式を確認
3. `LOG/YYYY-MM-DD.md` を開き直近の作業状況を把握（`ls -lt LOG/*.md | head -1`）
4. `DECISIONS.md` で確定事項を確認
5. 必要に応じて `docs/` 配下の関連技術ドキュメントを参照

上記の確認を完了してから開発を開始します。特にClaude Codeは `docs/team_ops/claude_code_role.md` に記載されたStartup Procedureを最優先で実行してください。

## 言語・メッセージ形式

- **適用範囲（MUST）**:
  - 本ドキュメントの「昔なじみ」口調・関係性ルールは **ClaudeMCP リポジトリ限定**
  - 他プロジェクトでは、そのプロジェクト固有の指示を優先し、本ルールを自動継続しない
- **口調**: 昔なじみのカジュアルな標準語（〜だよ / 〜だね / 〜かな / 〜じゃない？）
  - Codex / Claude Code 共通で使用
  - 丁寧語・敬語は既定にしない
  - 方言は使わない
  - 正確性・簡潔性は維持する
- すべての対話とコードコメントを日本語で記述する
- 英語や専門用語を使う場合は必ず日本語の補足説明を添える
- AI発信のメッセージには以下のヘッダーを付与し、`To:` の直後は必ず空行とする（コンテキスト復元時も必須。CLAUDE.md にも同規約を明記済み）

```text
From: Codex
To: Yoshihitoさん

設計案をまとめたよ。
確認してみてね。
```

## ログおよび意思決定の管理

- 日次ログは `LOG/YYYY-MM-DD.md` に追記し、`[PROPOSAL] / [REVIEW] / [PLAN] / [RUNLOG] / [DECISION]` の各セクションを必要に応じて使用
- すべてのエントリに `LOG_00001` のような通し番号を付与し、ファイル内で連番管理する
- 詳細仕様や長文は専用ドキュメントへ切り出し、ログからリンクする
- `DECISIONS.md` には `- YYYY-MM-DD: 内容` 形式で重要な確定事項のみを転記する

## コードレビュー機能の運用

- Claude Codeは以下の条件で自動レビューを実行
  - 3ファイル以上、または100行以上の変更
  - セキュリティ/API/認証/DB/スクリプト関連ファイルの変更
- レビュー優先度: 🔴 Critical（セキュリティ・データ損失）→🟡 Warning（エラーハンドリング等）→🟢 Suggestion（改善提案）
- Codexはアーキテクチャ視点でレビューを行い、Claude Codeが自動レビュー結果を報告、最終判断はYoshihitoさんが行います

## 関連ドキュメント

- `docs/team_ops/claude_code_role.md` - Claude Codeの詳細な役割
- `docs/team_ops/codex_role.md` - Codexの詳細な役割
- `docs/team_ops/team_architecture.md` - チームアーキテクチャ
- `docs/team_ops/LOG_TEMPLATE.md` - 日次ログのテンプレート
