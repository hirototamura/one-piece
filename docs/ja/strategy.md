# 現在のエンジニアリング戦略

この文書に具体的な戦略と仕様を記す。長期的な理念・ビジョンは[CORE.md](CORE.md)に保持する。CORE.mdの変更は、変更内容を特定した人間の明示的な事前承認を必要とする。

## 標準と共通の方法論

人間とすべてのエージェントは共通の[標準方針](../engineering/standards.md)、[NASA SE](../engineering/nasa_se.md)、[SpaceX-style SE](../engineering/spacex_se.md)を参照する。**要求標準の第一参照はISO/IEC/IEEE 29148:2018**とする。英語の要求・技術文書には**適用可能な範囲でASD-STE100 Simplified Technical English**を使う。NASA／SpaceXの方法論はこれを補完する。過去の原文は維持し、文言の変更は新しい草案として提案する。

## 必須のプラットフォーム能力

要求への自動適合検証と、Gitのような履歴・モデルdiff管理を必須の製品能力とする。構成の差分から影響する試験を特定し、再実行または根拠付き再評価を行い、要求・構成の特定版へ証拠を記録する。未実行・失敗・変更後に適用できない証拠を明示する。[競合調査](competitor_tradeoff.md)の旧採用判定は適用しない。[設計と受入条件の草案](verification_and_diff.md)に現状と未実装部分を記す。

## 関連する仕様

- [システムモデル](system_model.md)：版付き記録、トレース関係、証拠の適用範囲。
- [SysML API](sysml_api.md)：対応する標準サービスと交換形式。
- [自動検証とdiff](verification_and_diff.md)：現在の範囲と受入条件の草案。
- [競合調査](competitor_tradeoff.md)：過去の採用判断を除いた観察。

今後の具体的な戦略、仕様上の判断、実装の優先順位はこの文書に記す。技術的な詳細文書はここから参照する。正式な要求と証拠の正本は版付きJSONに置く。現在の実装範囲やマイルストーンをCORE.mdへ追加しない。

[英語版strategy](../en/strategy.md)。
