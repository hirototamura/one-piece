# 開発進捗ログ

**新しいエントリを上に追記**する。各エントリは数文に留め、コミットや PR があればリンクする。

## 2026-07-17（spacex-se サブエージェント）

- 2012 SpaceX SE デッキ（*System Engineering: A Traditional Discipline in a Non-traditional Organization*）と Hardware DevOps / モジュラー首席エンジニア運用を実行するプロジェクトサブエージェント `.cursor/agents/spacex-se.md` を追加。
- 安定した上位意図 vs 取引可能な KDP、Plan–Design–Build–Test スパイラル、Test Like You Fly、開発/認定/受入/HITL 階層、Tools not rules、および `docs/*/CORE.md` 成果物型への対応をプロンプトに組み込み。

## 2026-07-11（ドキュメント専用リポジトリ）

- 実装物をすべて削除: `apps/`、`packages/`、ルート `package.json`、`package-lock.json`、`pyproject.toml`、`tsconfig.base.json`。
- リポジトリの範囲は `docs/en/CORE.md`、`docs/ja/CORE.md`、本ログ、および `LICENSE` のみ。
- 削除したコードパスへの参照を `CORE.md` と `.gitignore` から除去。

## 2026-07-11（Web アプリ削除）

- `apps/web`（Vite + React PoC）と monorepo の `apps/` ワークスペースを削除。
- ルート `package.json` と `package-lock.json` を更新。

## 2026-07-11（ドキュメント整理）

- `docs/ja/`・`docs/en/` から `PROJECT_PLAN.md` と `INFORMATION_ARCHITECTURE.md` を削除。ライブ文書は README 索引と `development_progress.md` のみ。哲学・IA の内容は `ja/CORE.md` / `en/CORE.md` に集約。
- リポジトリ全体の README と `CORE.md` のリンクを更新。

## 2026-06-16（ドキュメント言語別整理）

- ライブ文書を `docs/ja/` と `docs/en/` に分割。ルート `README.md` と `AGENTS.md` を `ja/`・`en/` に移し、ルートには言語索引を配置。

## 2026-06-07（用語: 要求）

- ハードウェア SE の慣習に合わせ、日本語ドキュメントの「要件」を「要求」に統一（`Requirement` 等のコード識別子は原文維持）。

## 2026-06-07（README 充実）

- ルート `README.md` を書き直し: Web UI ツアー、SSOT/アクター用語、エコシステム上の位置づけ、インストール/実行コマンド、リポジトリマップ。

## 2026-06-07（Apache-2.0 ライセンス）

- ルートに `LICENSE`（Apache-2.0）を追加；`README.md` と `package.json`（ルート・`packages/domain`・`apps/web`）に `Apache-2.0` を明記。Codex レビュー（README のライセンス表記と実体の不一致）への対応。
- Python 側も `pyproject.toml` 4 件（ルート・`connectors`・`co-design`・`design-integration`）に `license = "Apache-2.0"` を追加。

## 2026-05-30（ドキュメント日本語化）

- 日本人チーム向けにリポジトリ内の Markdown（`README.md`、`AGENTS.md`、`docs/`*、`.cursor/skills/*`、`packages/design-integration/README.md`）を日本語化。コード識別子・CLI・パスは原文維持。

## 2026-05-26（自律 co-design MVP スキャフォールド）

- 自律 co-design ドメイン支援を追加: `CoDesignGoal`、`CoDesignIteration`、`CoDesignRun`、`AgentScopePolicy.autonomousCoDesign`、有界 AI-100 実行時のレビューキューバイパス意味論のヘルパー。
- Web: 目標入力・反復タイムライン・ライブ SSOT グラフ・来歴テール・自律熱ループ反復のリプレイ付き **Co-Design** ビュー；アクターポリシービューで自律モードを明示。
- Python: 新規 `packages/co-design` オーケストレータ + SQLite 永続化、`packages/connectors` の SSOS/ROS2 ブートストラップ取り込み CLI、`packages/design-integration` の熱排出スタンドイン分析と SSOT パラメータ直接同期。

## 2026-05-23（アクター境界 + Excel/Python 連携）

- ブランチ `feature/actor-boundaries-design-integration`: SSOT 変更を**人間エンジニア**、**ロジック自動化**、**AI エージェント**に帰属；`AgentScopePolicy`（AI デフォルト約 20%）、`aiTouchInHumanDomain` 警告付き `SsotProvenanceRecord`。
- `packages/domain` 拡張（`DesignArtifact`、`CellCodeBinding`、`IntegrationRun`、ポリシーヘルパー）；新規 `packages/design-integration` Python パッケージ（Excel→Python 同期 + スクリプトランナー）。
- Web: **Actor boundaries**、**Design integration** ビュー；要求・パラメータに来歴パネル。

## 2026-05-19（Web — フル SSOT UI）

- `apps/web` がグラフ SSOT を反映: **SSOT graph** エクスプローラ、**ICD**、**Design**（パラメータ + 制約）、**CAD**（同期状態）、ノード横断**グラフリンク**、マトリクスに制約を V&V 対象として含める、レビューキューに制約を含める。

## 2026-05-19（SSOT — ICD、制約、CAD）

- グラフ DB を SSOT とする方向を確定: サブシステムインターフェースごとの **ICD**、**設計パラメータ**、**設計制約**（V&V 用 `actsAsFunctionalRequirement`）、SSOT へライブ同期する **CAD モデル**。
- `packages/domain` 拡張（`EngineeringGraph`、`InterfaceControlDocument`、`DesignParameter`、`DesignConstraint`、`CadModel`、拡張 `TraceRelation`）；デモプログラムにサンプル ICD/CAD/制約をシード。

## 2026-05-19（SSOT アーキテクチャ）

- `docs/INFORMATION_ARCHITECTURE.md` に SSOT の位置づけを文書化: 正規化**プログラムグラフ**が権威；学問ツールとマトリクス/Excel は投影；自動 V&V の pull/push パターン。

## 2026-05-19（Web PoC）

- `apps/web`（Vite + React）追加: レベル別要求ツリー、コンプライアンスマトリクス、構成セレクタ、ライフサイクル操作付き人間レビューキュー；インメモリでデモプログラムをシード。
- `packages/domain` に `RequirementLevel`、`Program`、`VerificationActivity`、`MatrixCell` を拡張。

## 2026-05-19

- `docs/PROJECT_PLAN.md` の**原則**をハードウェア SE 5 原則で書き直し: トレーサビリティ/記録、完璧より反復、より賢い要求、横断設計、早期試験+自動化；旧デリバリー項目は短いデリバリー小節に統合。
- ビジョンを再定義: **あらゆるチーム規模**のハードウェアエンジニアリング加速（個人 → スタートアップ → 大規模プログラム）。

## 2026-05-10（SpaceX 2012 SE デッキ）

- 業界ハンドブック型デッキを参照；`AGENTS.md`（エンジニアリング哲学、検証メモ、ワークフロー）、`docs/PROJECT_PLAN.md`（原則 6–7、外部の影響）、`docs/INFORMATION_ARCHITECTURE.md`（安定 vs 派生トレード、検証厳しさ表）、`.cursor/skills/systems-engineering-saas/SKILL.md` を整合。

## 2026-05-10（後）

- ミッション文言: **すべてのチーム規模**；**規模でタッチポイントが異なる**；GTM 楔として**小規模チーム優先**。`AGENTS.md`、`docs/PROJECT_PLAN.md`、`docs/INFORMATION_ARCHITECTURE.md` を更新。

## 2026-05-10

- マルチエージェントオーケストレーション用 `AGENTS.md` 追加（役割、ワークフロー、人間ゲート）。
- `docs/PROJECT_PLAN.md`、`docs/INFORMATION_ARCHITECTURE.md`、本ログを追加。
- プロジェクトスキル `systems-engineering-saas`、`human-design-review` と、エージェントをリポ文脈へ誘導する Cursor ルールを追加。

---

*将来エントリ用テンプレート:*

## YYYY-MM-DD

- …
