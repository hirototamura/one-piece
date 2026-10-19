# v0.3.0: Cube要求と割当のレビュー済み版

2026-10-19の人によるレビューで、既存の要求文と機能・構成要素への割当分割を受け入れた。ユーザーの指示と対象範囲の回答「Requirements and allocation split」をレビュー判断に記録した。

- active modelとsnapshotの版：`reviewed-20261019-1`。
- 22個の義務と7個の整理用グループ：`status: reviewed`、`approval_state: human_reviewed`。
- 8機能・10構成要素：機上に5機能・7構成要素、外部検証文脈に3機能・3ツール。
- 22要求と37パラメータの割当は、受け入れた分割に対応する。要求から機能または製品へ、機能から実装する製品へ割り当てる。ミッションと総予算は全体への割当を保持する。
- レビュー判断：`cube.review.requirements-allocation@reviewed-20261019-1`。
- baseline：`cube.baseline.requirements-allocation@reviewed-20261019-1`。提案原本、レビュー判断、要求、機能、構成要素、パラメータ、検証計画、snapshot、active modelの112記録をハッシュで固定する。

113個の正式記録を追加する。過去の草案、要求の意味、パラメータ値・不確かさ、固定した力学モデル、制御器、評価契約を保持する。snapshotの文脈は、レビューした機能・構成要素の厳密な版を固定する。

## 検証の範囲

改訂した22検証ケースはすべて計画済み・`not_run`で、証拠は未添付である。実機検証は成立していない。未確定の数値限界と手順は未確定のままである。既存の設計充足宣言と数値結果は、元の要求の版への参照を保持する。新版への自動適用やハードウェア設計の採用は含まない。

リポジトリの試験は、記録の整合性、再生成の決定性、割当、baselineのハッシュ、厳密な文脈選択、証拠状態の保持を確認する。Cubeの検証計画そのものは実行しない。

## 再生成

ソースのcheckoutでパッケージをインストール後、次を実行する。

```sh
python projects/balancing-cube/review_requirements.py --write-docs
python -m pytest
```

この版に対する最初のコマンドは冪等で、113記録の変更なしを報告する。正本は版付きJSONであり、日英MarkdownとSQLite indexは派生表示である。

リリースのmetadata assetは追加した113記録とmanifestを含む。tagのソース内にある過去の記録を必要とし、simulation artifactの実体は含まない。実体の監査には既存のevidence releaseから復元する。

[要求本文](balancing_cube_requirements.md) · [システムモデル](system_model.md) · [English release notes](../en/reviewed_cube_release.md)
