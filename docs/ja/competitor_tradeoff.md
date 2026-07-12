# 競合手法と採用トレードオフ

**One Piece Engineering** と **Engineering Agents** に共通する設計方針（特定プログラム専用ではない）。

出典: One Piece Engineering 市場調査 PDF（8社、2026-07-12）および各社公開情報。  
目的: **制約付き自動検証**・**データ結合**・**AI エージェント組み付け**の手法選定。requirement_id → shell の単純自動束縛は採らない。

## 各社スナップショット

| 層 | 企業 | データ結合 | 自動化 | AI エージェント |
|----|------|------------|--------|-----------------|
| ① | Synera | 76+ CAx/PLM ワークフロー接続 | 解析・最適化パイプライン | Supervisor＋専門エージェント |
| ① | Dyad | Intent→物理一貫モデル | 高速反復シム等 | Intent からモデル構築 |
| ② | Antaris | Design Studio＋ツイン＋Flight OS | 製造前仮想ミッション検証 | AI for Space 機能 |
| ② | SysGit | Git 上のテキスト SE／SSOT | Branch/PR/CI、SysML v2 | ingest／自動化 |
| ② | Flow | Digital Thread | パラメータ閾値 Pass/Fail | Impact／Budget 系 |
| ③ | Dassault | Cameo／3DEXPERIENCE | 要件→SysML 構造抽出 | NLP／セマンティック |
| ③ | Siemens | NX／Simcenter／Teamcenter | NL→幾何推論→CAE 自動 | CAD 内シム自動化 |
| ③ | CoLab | 図面／CAD レビュー | AutoReview | ナレッジグラフ |

## 採用判断（One Piece／EA）

| 手法パターン | 判定 | 理由 |
|--------------|------|------|
| システムグラフ＋制約評価（Flow 型） | **採用（方針）** | 制約が検証の中心。虚偽を閾値／証拠で切る |
| Git 上の機械可読 SE＋PR/CI（SysGit 型） | **採用（近傍）** | docs/`model` と整合 |
| Supervisor＋専門エージェント（Synera 型） | **採用（EA ConOps）** | L1＋L2。AI がループを回し時間ボトルネック低減 |
| 物理一貫シム／ツインゲート（Dyad／Antaris 型） | **採用（真実）** | AI の嘘を決定論評価でフィルタ |
| 要件構造抽出 Copilot（Dassault 型） | **後続候補** | 起草支援 |
| 局所 CAD/CAE 自動化（Siemens 型） | **保留** | 部品級 |
| DFM AutoReview（CoLab 型） | **保留** | 図面レビュー特化 |
| requirement_id→shell 自動束縛 | **不採用** | グラフ＋constrain＋真実ゲートが本筋 |

## 人間と真実

- 人間意思決定を既定経路にすると **時間ボトルネック** になる。
- 設計・検証ループは AI が回す。
- AI は虚偽を述べうる。**真実を求めること**を決定論シム・制約・証拠で確保する。

## 制約付き検証ループ

適用例（EA ソフトウェアモデル）: [programs/engineering_agents/system_model.md](programs/engineering_agents/system_model.md)。
