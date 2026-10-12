# One-Piece 最小システムモデル

One-Pieceは要求、KDP（Key Design Parameter）、詳細パラメータ、構成、証拠、判断のSingle Source of Truthを管理する。Engineering Agentsと人間のHTMLは同じ版付き記録を読む。現在の対象はCubeの概念・開発試験段階である。

## 最小のグラフ

[OMG Systems Modeling API 1.0の参照境界](sysml_api.md)を使う。対象はProjectService ReadとElementNavigationServiceで、元グラフを標準の注釈と名前付きDependencyで保持する。SysMLテキストのパーサーやネイティブの要求メタモデルへの完全な意味変換は対象外である。各ノードは安定ID、revision、kind、product_node、data、出典を持つ。リンクは対象のIDとrevisionを指定する。

- `derive`：派生要求から親要求。
- `satisfy`：設計・製品から満たそうとする要求。対応関係の宣言であり、このリンクだけで合格を主張しない。
- `verify`：検証活動・証拠から対象の要求／試験ケース。合否と適用条件は証拠ノードに残す。
- `allocate`：要求・機能・KDPから責任を持つ製品ノード。
- `constrain`：要求・仕様から制約されるパラメータ／設計。

逆向きにもたどり、要求→関連設計→評価条件→証拠、失敗→試験→変更判断へ移動する。製品構成はCubeシステム、機械・駆動、センシング・推定、制御、電源と、検証を支えるプラットフォームを最小単位とする。要求はmission→systemからoperationalとsubsystemへ分岐する。

## 正本、版、根拠

JSONレコードを追記し、既存のID/revisionを異なる内容で上書きしない。SQLiteは検索用で、JSONから再構築できる。取込は参照とハッシュを検査した単位で公開する。モデル内の細かいパラメータを文脈に保持し、KDPの値・単位・不確かさ・model_path対応を省略しない。各実行でモデル、要求、評価条件、制御器の版を固定する。

未測定値は仮定、草案は草案のまま保存する。過去のconfirmedという元状態を新たな人間承認へ読み替えない。制御の比較用基準と、人間が採用したbaselineは別記録である。要求・評価条件・採用baselineは人間が確定する。

## 検証と妥当性確認

Verificationは指定した要求と条件への適合、Validationは意図した利用環境と目的への適合。CPU/GPU整合は数値実装の確認であり、床接触・モータ・熱・実機でのモデル妥当性を示さない。6秒の数値試験は実機30秒保持要求の証拠にならない。過去の半刻み確認は履歴として保持するが、新しいパイプラインでは実行しない。公開済み条件を再び設計改善へ使う場合は開発試験として扱う。

## Gitと証拠パック

自動要求検証とGitのようなモデルdiffを必須能力とする。差分から影響する検証ケースを特定し、結果がどの要求・構成の版へ適用できるかを保持する。現在の整合性検査とHTML設計比較は、その一部である。汎用の検証実行、semantic diff、再実行については[設計と受入条件の草案](verification_and_diff.md)を参照する。

小さな正本JSON・索引情報をGitへ保存し、DB、軌跡、HTML、動画は内容ハッシュ付きの証拠パックにする。GitHub ReleaseへのZIP添付は証拠の保管手段であり、要求や設計の承認とは別である。CLIで取得後にハッシュを照合でき、オフラインでも同じパックを復元できる。生成HTMLは正本からの投影であり、LLMはJSONのcontextを使う。

プロジェクト指定の `check` と `bundle` は、そのプロジェクトの成果物を検査する。全プロジェクトの証拠監査には指定なしの `check` を使う。復元後に再びGit cloneしても、正本JSONを変更せず成果物を再復元できる。極端によく圧縮できるZIPエントリは無圧縮で保存し、有効な証拠が取込時の展開率制限にも適合するようにする。

## 参考

- [NASA SE Engine](../engineering/nasa_se.md)：反復と階層的再帰、双方向トレース、構成管理、VerificationとValidationの区別。
- [SpaceX-style SE](../engineering/spacex_se.md)：上位意図を保ち、下位KDPを証拠付きでトレードし、安価な開発試験で学ぶ。
- [OMG SysML v2](https://www.omg.org/spec/SysML/2.0/)：構成・属性・要求・検証の参考。
- [ENPIRE](https://arxiv.org/html/2606.19980v2)：環境構築と、その環境を固定した改善ループを分離する。

要求の優先順位はISO/IEC/IEEE 29148:2018、適用するNASA標準・要求記述ガイド、ASD-STE100の順である。NASAの要求記述に従い、英語要求には`shall`を使う。現在のbalancing-cube表示は、明示的なactive system-model参照により `cube.simulation.snapshot@standards-draft-20261011-2` を選ぶ。比較基準designとcampaign_summaryは文脈件数制限の外に置く。Engineering Agentsは、別のsnapshotを選択するまで、実行時の明示的な既定値 `fixed-dt-mvp-2` を保持する。

[英語の要求草案](../en/balancing_cube_requirements.md)を原文として、対応する[日本語訳](balancing_cube_requirements.md)を作る。現在のモデルは、22個の試験義務、7個の整理用コンテナ、22個の計画済み検証ケースを持つ。コンテナは記録の互換性のためkindを`requirement`に保つが、`record_role: requirement_group`と空のstatementにより試験義務から区別する。製作と駆動の複合要求には、分割した子要求を持たせる。allocateは担当する製品を特定する。Cubeの性能は`cube.system`、駆動限界は`cube.actuation`、独立計測は`cube.verification`へ割り当てる。

新しい要求文の状態は`status: draft`、承認状態は`approval_state: pending_human_review`である。`source_status`は以前の要求文の状態を保持する。要求文の状態と実機検証は別である。`hardware_verification_required`は予定する実機作業を表し、合格フラグではない。数値evaluationは、元の開発test caseへのverifyを保持する。過去の版は、元のフィールド、グラフの厳密な接続先、出典のdigestを維持する。計画したケースや旧結果が、改訂した要求を自動的に検証することはない。
