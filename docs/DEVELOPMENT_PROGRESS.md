# 開発進捗ログ

**新しいエントリを上に追記**する。各エントリは数文に留め、コミットや PR があればリンクする。

## 2026-05-30（ドキュメント日本語化）

- 日本人チーム向けにリポジトリ内の Markdown（`README.md`、`AGENT.md`、`docs/*`、`.cursor/skills/*`、`packages/design-integration/README.md`）を日本語化。コード識別子・CLI・パスは原文維持。

## 2026-05-26（自律 co-design MVP スキャフォールド）

- 自律 co-design ドメイン支援を追加: `CoDesignGoal`、`CoDesignIteration`、`CoDesignRun`、`AgentScopePolicy.autonomousCoDesign`、有界 AI-100 実行時のレビューキューバイパス意味論のヘルパー。
- Web: 目標入力・反復タイムライン・ライブ SSOT グラフ・来歴テール・自律熱ループ反復のリプレイ付き **Co-Design** ビュー；アクターポリシービューで自律モードを明示。
- Python: 新規 `packages/co-design` オーケストレータ + SQLite 永続化、`packages/connectors` の SSOS/ROS2 ブートストラップ取り込み CLI、`packages/design-integration` の熱排出スタンドイン分析と SSOT パラメータ直接同期。

## 2026-05-23（アクター境界 + Excel/Python 連携）

- ブランチ `feature/actor-boundaries-design-integration`: SSOT 変更を**人間エンジニア**、**ロジック自動化**、**AI エージェント**に帰属；`AgentScopePolicy`（AI デフォルト約 20%）、`aiTouchInHumanDomain` 警告付き `SsotProvenanceRecord`。
- `packages/domain` 拡張（`DesignArtifact`、`CellCodeBinding`、`IntegrationRun`、ポリシーヘルパー）；新規 `packages/design-integration` Python パッケージ（Excel→Python 同期 + スクリプトランナー）。
- Web: **Actor boundaries**、**Design integration** ビュー；要件・パラメータに来歴パネル。

## 2026-05-19（Web — フル SSOT UI）

- `apps/web` がグラフ SSOT を反映: **SSOT graph** エクスプローラ、**ICD**、**Design**（パラメータ + 制約）、**CAD**（同期状態）、ノード横断**グラフリンク**、マトリクスに制約を V&V 対象として含める、レビューキューに制約を含める。

## 2026-05-19（SSOT — ICD、制約、CAD）

- グラフ DB を SSOT とする方向を確定: サブシステムインターフェースごとの **ICD**、**設計パラメータ**、**設計制約**（V&V 用 `actsAsFunctionalRequirement`）、SSOT へライブ同期する **CAD モデル**。
- `packages/domain` 拡張（`EngineeringGraph`、`InterfaceControlDocument`、`DesignParameter`、`DesignConstraint`、`CadModel`、拡張 `TraceRelation`）；デモプログラムにサンプル ICD/CAD/制約をシード。

## 2026-05-19（SSOT アーキテクチャ）

- `docs/INFORMATION_ARCHITECTURE.md` に SSOT の位置づけを文書化: 正規化**プログラムグラフ**が権威；学問ツールとマトリクス/Excel は投影；自動 V&V の pull/push パターン。

## 2026-05-19（Web PoC）

- `apps/web`（Vite + React）追加: レベル別要件ツリー、コンプライアンスマトリクス、構成セレクタ、ライフサイクル操作付き人間レビューキュー；インメモリでデモプログラムをシード。
- `packages/domain` に `RequirementLevel`、`Program`、`VerificationActivity`、`MatrixCell` を拡張。

## 2026-05-19

- `docs/PROJECT_PLAN.md` の**原則**をハードウェア SE 5 原則で書き直し: トレーサビリティ/記録、完璧より反復、より賢い要件、横断設計、早期試験+自動化；旧デリバリー項目は短いデリバリー小節に統合。
- ビジョンを再定義: **あらゆるチーム規模**のハードウェアエンジニアリング加速（個人 → スタートアップ → 大規模プログラム）。

## 2026-05-10（SpaceX 2012 SE デッキ）

- 業界ハンドブック型デッキを参照；`AGENT.md`（エンジニアリング哲学、検証メモ、ワークフロー）、`docs/PROJECT_PLAN.md`（原則 6–7、外部の影響）、`docs/INFORMATION_ARCHITECTURE.md`（安定 vs 派生トレード、検証厳しさ表）、`.cursor/skills/systems-engineering-saas/SKILL.md` を整合。

## 2026-05-10（後）

- ミッション文言: **すべてのチーム規模**；**規模でタッチポイントが異なる**；GTM 楔として**小規模チーム優先**。`AGENT.md`、`docs/PROJECT_PLAN.md`、`docs/INFORMATION_ARCHITECTURE.md` を更新。

## 2026-05-10

- マルチエージェントオーケストレーション用 `AGENT.md` 追加（役割、ワークフロー、人間ゲート）。
- `docs/PROJECT_PLAN.md`、`docs/INFORMATION_ARCHITECTURE.md`、本ログを追加。
- プロジェクトスキル `systems-engineering-saas`、`human-design-review` と、エージェントをリポ文脈へ誘導する Cursor ルールを追加。

---

*将来エントリ用テンプレート:*

## YYYY-MM-DD

- …
