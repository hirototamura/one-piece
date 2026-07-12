# Engineering Agents — 検証計画

検証の問い: *ソフトウェアを shall どおり正しく作っているか？*  
妥当性確認（ConOps 達成）は [validation.md](validation.md)。  
マトリクス: [matrix.md](matrix.md)。

## 手法

- **試験 (test)** — 実行可能な回帰とループ・スモーク
- **分析 (analysis)** — 提案／証拠スキーマや層境界のレビュー（必要時）
- **検査 (inspection)** — 保存された実行成果物の確認

## 第一級 verification case

### `VC-ea-loop-2run`

| 欄 | 内容 |
|----|------|
| どの要求か | `EA-SW-SYS-010`, `EA-SW-SYS-020` |
| 何をもってか | CLI → scenario: Cycle1 → 提案出力 → 提案適用して Cycle2 |
| どう判定か | `C-N-ge-1`, `C-proposals_emitted`, `C-result_delta`, `C-truth-gate` |
| 証拠 | `E-run1`, `E-run2` |

ConOps の **ミニマムサクセス** ゲートにもアンカー（[validation.md](validation.md)）。

### `VC-ea-pytest`

| 欄 | 内容 |
|----|------|
| どの要求か | 各 `EA-SW-SUB-*` |
| 何をもってか | 開発用回帰テストスイート |
| どう判定か | `C-pytest_green` |
| 証拠 | `E-pytest` |

## 制約付き自動検証の立場

requirement_id → shell の単純自動束縛は用いない。  
**システムグラフ + constrain + 決定論的真実ゲート**（[competitor_tradeoff.md](competitor_tradeoff.md)）。

## 機械可読

[model/verification_cases.yaml](../../en/programs/engineering_agents/model/verification_cases.yaml)
