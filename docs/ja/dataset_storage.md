# データの保存と取得

ソースコード、小さな正本記録、取得用カタログは Git で管理します。大きな実行データは
ハッシュを固定した GitHub Release の添付ファイルとして保存します。

最初のカタログは `datasets/integration_validation_20261024.json` です。
42データセット、過去の2,427ファイルを索引化しています。新規の30アーカイブは
非公開リポジトリ `hirototamura/balancing-cube-simulation` の
`validation-archive-20261024` Release に保存します。既存の12アーカイブは、
SHA-256 が一致する既存 Release のファイルを再利用します。既存ファイルの公開範囲を
保ち、新しいデータは非公開にします。

対象は実行結果、受入記録、過去のソースパック、画面キャプチャ、検証用スクリプトです。
実行・検証環境ごとに取得できます。Git メタデータ、シンボリックリンク、仮想環境、
ビルド結果、キャッシュ、再構築可能な SQLite 索引は除外します。元のローカルファイルは
保持します。保存したという事実は、検証合格や設計の採用を意味しません。

```sh
python -m pip install -e .
gh auth login
onepiece datasets list datasets/integration_validation_20261024.json --query qwen
onepiece datasets fetch datasets/integration_validation_20261024.json \
  --id qwen27b-memory10-results-20261012 --destination /path/to/workspace
onepiece datasets verify datasets/integration_validation_20261024.json \
  --id qwen27b-memory10-results-20261012 --destination /path/to/workspace
```

別の環境では、カタログを含む One-Piece のコミットを取得してください。非公開データの
認証には、その環境で本人の GitHub CLI を使います。認証情報を Mac から複製しません。

`--id` は複数指定できます。`--path` で復元するファイルやディレクトリを絞れます。
必要なアーカイブを一度取得し、`~/.cache/onepiece/datasets` に SHA-256 ごとに保存します。
`--cache` で保存先を、`--assets-dir` でオフラインのアーカイブ置場を指定できます。
既存ファイルが異なる内容なら、新しいファイルの配置前に停止します。上書きは行いません。

アーカイブと各ファイルのサイズ・ハッシュを検査します。ZIP の内容とカタログを照合し、
危険なパスやシンボリックリンクを拒否して、配置前にステージングで検査します。
元から ZIP・tar だった資料は、そのまま復元し、自動展開や実行はしません。

データセットの取得は、過去の作業ファイルの復元です。正本ストアへの取込は別操作です。
One-Piece 証拠パックを取り込む場合は、既存の `import` / `fetch` の記録検査を使います。

今後は `onepiece datasets pack` でカタログとアーカイブを作成し、新しい非公開 Release に
保存してください。リモートのハッシュとクリーン環境での復元を確認してからカタログを
Git にコミットします。公開済みのアーカイブや過去の測定結果を置換せず、新しいデータや
版として追加します。

[要求エクスプローラー](requirements_explorer.md) · [英語版](../en/dataset_storage.md)
