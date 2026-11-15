# v0.5.0リリース候補：11月15日版CubeとExplorer

2026-11-15（Asia/Tokyo）に準備したリリース候補。タグ作成とリリース公開は未実施。

レビュー済みモデルとスナップショットは `requirements-review-20261115-3`。
`projects/balancing-cube/release_candidate.json` に、モデル、スナップショット、
レビュー判断、ベースライン、CM-01、構成カタログの版とSHA-256を固定した。
ベースラインの117メンバーもハッシュを照合する。過去版とv0.3.0の記録は保持する。

要求19件、分類7件、別枠の制約3件、KDP37件、機能9件、コンポーネント10件。
8頂点での保持、共通の10秒保持区間、保持制御前の頂点自動識別を含む。
材料は設計上の選択、予算はプロジェクト制約、各造形部品の寸法と国内調達は製造制約。
yawは保持開始時の固定した鉛直軸、R-TRACEは構成管理に割り当てる。
ミッション、システム性能、駆動系、計測系の導出関係を明示した。

Explorerは公開版の画面、文字サイズ、パネルの削除、英日表示、KDPナビゲーション、
ブラウザ内の改訂案・エクスポートを引き継ぐ。SitesやNode.jsは不要。
ECLSS/scrubberの同梱例はシナリオ契約である。

## 再現と公開までの手順

```sh
python -m pip install -e .
python projects/balancing-cube/apply_requirement_review.py --write-docs
python -m pytest
onepiece --store projects/balancing-cube/store explorer serve \
  --model-revision requirements-review-20261115-3
```

再生成は118件が変更なしとなる。wheelをソースツリー外で別途検証する。
wheel、ソースアーカイブ、ポータブルExplorer、SHA-256チェックサムを準備し、
生成成果物はGitに含めない。スタックの親PRと本PRをマージ後、最終リリースコミットから
再ビルドして `v0.5.0` タグと、そのコミットに対応する成果物を公開する。

## 引き継ぐ未解決事項

22件の検証計画（要求19件・制約3件）は全て `not_run` で、証拠は未添付。
項目別の未解決事項はリリース索引に記録した。roll/pitchの水平軸案はレビュー対象。
部品限界や計測手順の未解決事項も残す。制御アルゴリズムの変更範囲は契約に記録済みだが、
コード提案・実行の拡張と頂点識別のアルゴリズムは次段階となる。
数値採点は変更せず、過去の証拠は元の適用範囲を保つ。
本リリースは実機設計の採用や物理検証済みを意味しない。

[英語版](../en/cube_release_20261115.md) · [現行要求](balancing_cube_requirements.md)
