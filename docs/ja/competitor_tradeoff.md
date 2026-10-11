# 競合調査と現在の設計課題

この文書は、[旧調査（commit 6576c356）](https://github.com/hirototamura/one-piece/blob/6576c356b14c7d287b7ec72a7381d3c7b30b49cd/docs/ja/competitor_tradeoff.md)から競合の観察を引き継ぐ。**旧文書の採用・近傍・後続候補・保留・不採用の判定は、現在の方針として使用しない。** 旧文書末尾の人間／エージェントの権限に関する判断も、現在の[共通方針](../engineering/standards.md)を変更しない。

旧文書は市場調査PDF（8社、2026-07-12）と各社公開情報を出典としている。このPRではそのPDFを照合していない。以下の8社の要約は当時の観察であり、現在の製品仕様、性能、接続数を再確認した一覧ではない。今回はユーザーが必須とした自動要求検証とdiffに関係するFlow／SysGitの公式資料を追加確認した（2026-10-11）。

## 引き継ぐ競合スナップショット

- **Synera**：旧調査では、CAx／PLMのワークフロー接続、解析・最適化パイプライン、Supervisorと専門エージェントの構成に着目していた。「76+」という接続数も旧調査の値である。
- **Dyad**：Intentから物理モデルを構築し、物理的な一貫性を保ってシミュレーションを反復する方法に着目していた。
- **Antaris**：Design Studio、デジタルツイン、Flight OSを接続し、製造前に仮想ミッションを検証する方法に着目していた。
- **SysGit**：Git上の機械可読なシステムモデルとSSOT、Branch／PR／CI、SysML v2を接続する方法に着目していた。
- **Flow**：Digital Threadで要求と設計パラメータを結び、閾値に対して適否を評価する方法に着目していた。
- **Dassault**：Cameo／3DEXPERIENCE、要求からの構造抽出、NLP／セマンティック支援に着目していた。
- **Siemens**：NX／Simcenter／Teamcenterを接続し、自然言語から幾何・CAEへ進む自動化に着目していた。
- **CoLab**：図面／CADレビュー、AutoReview、ナレッジグラフに着目していた。

これらは調査の再利用であり、特定ベンダーや方式の採用を決定するものではない。比較時には、対応範囲、接続可能な実行系、版管理、証拠の再現性、移行性を実例で確認する。

## 今回確認した公式情報

**Flow**の公開資料では、要求をシステム・試験と結ぶSystems Graphと変更履歴を説明している。[Requirements Management](https://www.flowengineering.com/product/requirements-management)。また、Excelのセル値を要求と照合する接続、Onshapeの寸法・質量などを使う自動検証、Python解析結果と要求の接続を説明している。MatlabやSimScaleなど、一部の接続は「Coming Soon」と表示されているため、すべてが利用可能とは扱わない。[Integrations](https://www.flowengineering.com/integrations)。本調査では製品を実操作しておらず、性能やAPI動作は未検証である。

**SysGit**の公式解説では、`.sysml`のテキストをGitで管理し、branch／mergeとテキスト・グラフのdiffでモデル変更を確認する構成を説明している。[SysGit Saturday #1](https://resources.sysgit.io/sysgit-saturday-1-a-purpose-built-collaborative-sysml-v2-ide/)。これは自社製品の説明であり、One-Pieceへの移行確認や性能比較を実施した結果ではない。

## 現在の必須能力

ユーザー指定の必須能力は次の2点である。競合の採用判断とは分けて、One-Piece自身の設計と受入条件へ落とす。

1. **要求への適合を自動検証する。** 要求の特定版、条件、設計構成、試験、評価器を結び、実行結果から決定論的に判定する。未実行・証拠不足・対象外の条件を合格へまとめない。
2. **Gitのようにdiffを管理する。** 変更前後の構成を指定し、要求文だけでなく値・単位・閾値・関係・証拠の版参照を比較する。変更がどの検証結果を再利用できなくするかも追跡する。

この2つを接続することが重要である。要求や設計が変わったらdiffから影響する試験を特定し、再実行し、同じ要求・構成の版へ結果を記録する。過去に合格していても、前提が変わった証拠を新しい版の合格として流用しない。

実行側はEngineering Agents、要求・構成・証拠・判断の正本はOne-Pieceとする。ISO/IEC/IEEE 29148:2018を要求標準の第一参照とし、SysML APIの標準参照境界を維持する。競合製品のデータモデルをそのまま採用する判断は行わない。

[必須能力の設計と受入条件](VERIFICATION_AND_DIFF.md)に、現状の実装、未実装部分、次に確認する最小ケースを記す。英語版は[こちら](../en/competitor_tradeoff.md)。
