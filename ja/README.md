# one-piece — ハードウェア向けシステムエンジニアリング SaaS

**ミッションから検証まで**、ハードウェア製品の要求・設計・インターフェース・検証を**一つのトレーサブルなグラフ**で管理する SaaS の概念実証（PoC）です。**あらゆる規模のチーム**を対象としつつ、ロードマップでは**小規模チームを最優先**に、スプレッドシート並みに扱えるコンプライアンスビューを目指します。

人間のエンジニアが**ベースラインと判断**を担い、AI エージェントはドラフト・横断チェック・一貫性維持を支援します。本リポジトリは**本番 SaaS ではなく**、ドメインモデル・Web UI PoC・Python 連携パッケージ・エージェント運用ルールを同居させた**研究・開発用モノレポ**です。

---

## 一目でわかる（Web UI）

`apps/web` のデモ UI（`npm run dev`）では、インメモリのサンプルプログラムを軸に、次の 10 ビューから SSOT（Single Source of Truth）を辿れます。

### 1. SSOT graph — プログラム全体の権威グラフ

要求・ICD・設計パラメータ・制約・CAD・検証活動・トレースエッジを**一つのグラフ**として探索します。マトリクスやツリーはこのグラフの**投影**であり、正本はここに集約されます。

### 2. Requirements — 階層要求ツリー

`mission` → `system` → `operational` → `subsystem` の階層で要求を表示し、選択ノードの詳細・ライフサイクル（`draft` / `under_review` / `baseline`）・上流トレースを確認できます。システム要求には **AIV**（Assembly and Integration Verification）計画を紐づけます。

### 3. Interfaces (ICD) — サブシステム間インターフェース

提供者・消費者ペアごとの **Interface Control Document** と信号・限界値・単位を管理します。横断的な整合チェックの起点になります。

### 4. Design — パラメータと設計制約

`DesignParameter`（値・単位・境界・学科タグ）と `DesignConstraint` を一覧します。`actsAsFunctionalRequirement` が立った制約は、機能要求と同様に**配分と V&V** に参加します。

### 5. CAD — モデルリビジョンと同期状態

CAD ノードのリビジョン・チェックサム・同期ステータスを SSOT 上で追跡します。ジオメトリ本体は PLM / オブジェクトストレージに置き、**リビジョンと抽出パラメータは設計変更のたびに SSOT へ反映**する方針です。

### 6. Design integration — Excel ↔ Python 連携

`DesignArtifact`（Excel ワークブック・Python スクリプト）と `CellCodeBinding` で、セル値と `SSOT:PARAM:KEY` マーカーを同期します。**ロジック自動化**（AI 非介在）がセル更新 → スクリプト再実行 → `IntegrationRun` 記録を行います。

### 7. Co-Design — 自律設計イテレーション

`CoDesignGoal`（自然言語目標 + 数値メトリクス）に対し、AI が許可スコープ内で派生パラメータを更新し、解析を挟みながらイテレーションを進めます。タイムライン・SSOT グラフ・プロベナンス・イテレーション再生を同期表示します。

### 8. Actor boundaries — 誰が SSOT を変えたか

各変更は **human engineer** / **logic automation** / **AI agent** のいずれかに帰属します。`AgentScopePolicy`（デフォルト AI 約 20%）と `SsotProvenanceRecord` で、`aiTouchInHumanDomain` 警告を含む監査証跡を可視化します。

### 9. Compliance matrix — 要求 ↔ 証拠

行＝要求（または検証対象）、列＝証拠（テストケース・解析 ID・検査記録）、セル＝ステータス（planned / passed / failed / waived）。Excel 並みの読みやすさを UX 目標とし、下層は正規化トレースから生成します。

### 10. Review queue — 人間ゲート

ドラフトや AI 提案を **baseline** へ進めるレビューキュー。設計ベースライン・免除（waiver）・「検証済み」主張の前に、人間のサインオフを必須とします。

---

## なぜ one-piece か

ハードウェアプログラムでは、要求の曖昧さ・サブシステム間のインターフェース齟齬・検証証拠の散逸が、統合試験の直前まで表面化しません。現実のチームは次のループを回します。

1. **意図を階層化**する（ミッション → システム → 運用 → サブシステム）
2. **設計と検証計画**をトレースで結ぶ
3. **ビルド・試験・解析**から派生仕様を更新し、根拠を残す
4. **コンプライアンスマトリクス**で穴を見つけ、人間がベースライン化する

one-piece はこのループを **SaaS のデータモデルと UI** で再現可能にし、エージェントがドラフトと横断チェックを担う前提をコードとドキュメントに落とし込むことが目的です。

**設計思想（抜粋）**


| 原則            | 意味                          |
| ------------- | --------------------------- |
| トレーサビリティと記録が先 | リンクと記録がなければ「起きていない」         |
| 完璧より反復        | ミッション意図は固定し、派生仕様は証拠で更新      |
| 間抜けな要求を減らす    | 曖昧さを減らし、検証可能な記述へ            |
| 学際設計          | 機械・電気・熱・ソフト・運用・試験を一グラフで     |
| 早期試験・自動化      | 開発試験を早く回し、人間判断はベースラインと異常に集中 |


詳細は [docs/ja/PROJECT_PLAN.md](../docs/ja/PROJECT_PLAN.md) と [ja/AGENT.md](./AGENT.md) を参照してください。

---

## コア概念（用語）


| 用語                        | 説明                                                        |
| ------------------------- | --------------------------------------------------------- |
| **SSOT**                  | プログラム単位の正規化グラフ（DB が権威）。マトリクス・ツリーは投影                       |
| **Program**               | 一製品／一プログラムのエンジニアリングコンテキスト（設定 V1/V2 など）                    |
| **Requirement level**     | `mission` / `system` / `operational` / `subsystem`        |
| **AIV**                   | Assembly and Integration Verification — システム統合レベルの検証計画    |
| **ICD**                   | Interface Control Document — サブシステム間の合意インターフェース           |
| **Design package**        | サブシステム設計記述 + 支持解析                                         |
| **Verification activity** | 解析・試験・検査のいずれか（報告書・証拠にリンク）                                 |
| **Compliance matrix**     | 要求 ↔ 証拠のグリッド（単純ステータス + アーティファクト参照）                        |
| **AgentScopePolicy**      | AI が変更してよいノード種・重要度の上限（`autonomousCoDesign` で PoC 100% も可） |
| **CoDesignRun**           | 目標駆動の自律設計ループ（イテレーション・メトリクス・収束状態）                          |
| **Logic automation**      | LLM 非介在の決定論的同期（Excel 同期・CI 試験・コネクタ webhook）               |


**安定意図 vs 派生トレード**

- **ミッション／顧客／ユーザー意図** — 追跡・検証対象として扱う
- **派生仕様・下位要求** — 設計中にトレード可能。ただし**根拠・決定・免除へのリンク必須**

### 要求グラフ（デフォルトの流れ）

```text
[Mission requirements]
        |
        v
[System requirements] -----> [AIV plan]
        |
   +----+----+
   v         v
[Operational]  [Subsystem requirements]
                      |
                      +--> [Design package + analysis]
                      +--> [Verification plan + platform needs]
```

### SSOT ミューテーションの 3 アクター


| アクター                 | 役割                    | 例                                 |
| -------------------- | --------------------- | --------------------------------- |
| **Human engineer**   | ベースライン・重大判断・現実世界との接点  | 要求編集、免除承認                         |
| **Logic automation** | 再現可能・決定論的             | `one-piece-sync`、試験ランナー、SSOS 取り込み |
| **AI agent**         | ポリシー内ドラフト（デフォルト ~20%） | 要求文案、パラメータ提案、co-design 反復         |


---

## このリポジトリと engineering_agents / SSOS の位置づけ

```text
[ one-piece（本リポジトリ）]
  packages/domain     … TypeScript ドメインモデル（SSOT 型）
  apps/web            … SSOT 探索・マトリクス・レビュー UI PoC
  packages/co-design  … 自律設計ループ orchestrator
  packages/design-integration … Excel ↔ Python 同期
  packages/connectors … 外部ソース逆取り込み（SSOS 等）

[ 連携先（研究・開発途中）]
  engineering_agents  … ECLSS 異常シミュレーション + 設計提案 JSONL
  Space Station OS    … 軌道上運用ソフトのモック／将来アダプタ
```


| 領域                          | 状態                | 参照                                                                             |
| --------------------------- | ----------------- | ------------------------------------------------------------------------------ |
| ドメインカーネル（`packages/domain`） | **利用可能**          | [docs/ja/INFORMATION_ARCHITECTURE.md](../docs/ja/INFORMATION_ARCHITECTURE.md)           |
| Web UI PoC（`apps/web`）      | **利用可能**（インメモリデモ） | 本 README [Web UI](#一目でわかるweb-ui)                                               |
| Excel/Python 連携             | **利用可能**（PoC）     | [packages/design-integration/README.md](packages/design-integration/README.md) |
| 自律 co-design ループ            | **利用可能**（PoC）     | [packages/co-design/README.md](packages/co-design/README.md)                   |
| SSOS 逆取り込み                  | **スタブ／CLI**       | [packages/connectors/README.md](packages/connectors/README.md)                 |
| 本番 API・永続 DB・マルチテナント        | **未実装**           | [docs/ja/PROJECT_PLAN.md](../docs/ja/PROJECT_PLAN.md)                                   |


[engineering_agents](https://github.com/hirototamura/engineering_agents) は運用中の異常 → チーム判断 → 恒久設計提案までをシミュレートし、**設計提案のプロベナンス**を one-piece 形式へエクスポートする連携を想定しています（詳細: 相手リポジトリの `docs/one-piece-integration.md`）。

---

## ドキュメント


| ドキュメント                                                               | 対象読者            | 内容                                 |
| -------------------------------------------------------------------- | --------------- | ---------------------------------- |
| [ja/AGENT.md](./AGENT.md)                                               | エージェント・コントリビュータ | 役割分担、ワークフロー、人間ゲート、ドキュメント義務         |
| [docs/ja/PROJECT_PLAN.md](../docs/ja/PROJECT_PLAN.md)                         | プロダクト・開発        | フェーズ、バックログ、リスク、成功指標                |
| [docs/ja/INFORMATION_ARCHITECTURE.md](../docs/ja/INFORMATION_ARCHITECTURE.md) | モデラー・設計者        | SSOT、アーティファクト、トレース、マトリクス、co-design |
| [docs/ja/DEVELOPMENT_PROGRESS.md](../docs/ja/DEVELOPMENT_PROGRESS.md)         | 全員              | 時系列の変更ログ                           |
| [docs/ja/README.md](../docs/ja/README.md)                                     | 全員              | 上記ドキュメントの索引                        |
| [en/README.md](../en/README.md)                                     | English readers   | English documentation index                 |


**Cursor プロジェクトスキル**


| スキル                                        | 用途                     |
| ------------------------------------------ | ---------------------- |
| `.cursor/skills/systems-engineering-saas/` | 要求階層、V&V、マトリクス、ドメイン型拡張 |
| `.cursor/skills/human-design-review/`      | 設計ベースライン、解析信頼性の人間判断    |


---

## 必要条件

- **Node.js 20+**（Web UI・`packages/domain`）
- **npm**（ワークスペース monorepo）
- **Python 3.11+**（`packages/co-design` / `design-integration` / `connectors`）
- **uv** または **pip**（Python パッケージのローカルインストール用）

---

## インストール（ゼロから）

### 1. リポジトリを取得

```bash
git clone https://github.com/hirototamura/one-piece.git
cd one-piece
```

### 2. Node 依存関係とドメインビルド

```bash
npm install
npm run build -w @one-piece/domain
```

### 3. Web UI の起動確認

```bash
npm run dev
```

ブラウザで `http://localhost:5173` を開きます。サイドバーから 10 ビューを切り替えてください。

### 4. Python パッケージ（任意）

各パッケージは独立しています。例: 設計連携 PoC

```bash
cd packages/design-integration
uv sync          # または: pip install -e .
uv run pytest
```

同様に `packages/co-design`・`packages/connectors` でも `uv sync` / `pip install -e .` が使えます。

---

## 実行方法

### Web UI（デモプログラム）

```bash
npm run dev
# → http://localhost:5173
```

- 設定（Configuration）セレクタで V1/V2 を切り替え
- **Co-Design** ビューで自律ループの開始・停止・イテレーション再生
- **Review queue** でライフサイクル遷移（人間ゲートの UX 確認）

### ドメイン型のビルド・型チェック

```bash
npm run build -w @one-piece/domain
npm run typecheck -w @one-piece/domain   # package.json に script がある場合
```

### Excel ↔ Python 同期（`one-piece-sync`）

```bash
cd packages/design-integration
uv run python examples/create_workbook.py
uv run one-piece-sync \
  --workbook examples/propulsion_budget.xlsx \
  --script examples/thrust_margin.py \
  --bind "Inputs!B2:P-VBUS:P-VBUS:VBUS" \
  --bind "Inputs!B3:P-M-MOTOR:P-M-MOTOR:MOTOR_MASS_KG"
```

熱拒否スタンドイン解析: `examples/thermal_rejection.py`（co-design ループから呼び出し可能）。

### 自律 co-design CLI

```bash
cd packages/co-design
python -m one_piece_codesign.cli \
  --program ../../tmp/program.json \
  --output ../../tmp/program-out.json \
  --db ../../tmp/codesign.db
```

### 外部ソース取り込み（SSOS スタブ）

```bash
cd packages/connectors
python -m one_piece_connectors.cli \
  --source ssos \
  --path /path/to/space_station_os \
  --output /tmp/ssos-graph.json
```

---

## リポジトリ構成


| パス                             | 用途                                    |
| ------------------------------ | ------------------------------------- |
| `packages/domain/`             | 共有ドメインモデル（要求、グラフ、トレース、co-design、ポリシー） |
| `apps/web/`                    | Vite + React の Web UI PoC             |
| `packages/design-integration/` | Excel ↔ Python バインディング、ロジック自動化ランナー    |
| `packages/co-design/`          | 自律設計ループ orchestrator + SQLite 永続化     |
| `packages/connectors/`         | SSOS 等への逆取り込み CLI                     |
| `docs/ja/`、`docs/en/`                        | 生きた設計ドキュメント（計画・IA・進捗、言語別）                 |
| `.cursor/skills/`              | ドメイン + 人間レビュー用エージェントスキル               |
| `.cursor/rules/`               | エージェント向けリポジトリコンテキスト                   |


**依存の目安:** `apps/web` → `packages/domain`；Python パッケージは PoC 段階ではドメイン JSON をファイル経由でやり取り。

**ロードマップ（要約）**


| フェーズ         | 成果物                               |
| ------------ | --------------------------------- |
| P0 ドメインカーネル  | 豊富な `packages/domain`（進行中）        |
| P1 縦スライス API | CRUD + トレースクエリ + マトリクス API        |
| P2 Web UI    | 要求ツリー・マトリクス・レビュー（PoC 済み、永続化はこれから） |
| P3 エージェントフック | サーバー側ドラフト → diff レビュー             |
| P4 コラボレーション  | 組織・ロール・監査ログ・ベースラインスナップショット        |


---

## ライセンス

[Apache License 2.0](./LICENSE)