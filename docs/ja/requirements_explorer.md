# 要求エクスプローラー

要求エクスプローラーのソースとデータ投影処理を One-Piece で管理します。
ローカル試作のコミット `d5bcc0c70be1f7b190fbe8368c90e5eec4ac75bf` から移行しました。
画面のソースは `src/onepiece/explorer_assets/` に含まれ、生成した画面とデータは Git 管理外です。

```sh
python -m pip install -e .
onepiece --store projects/balancing-cube/store explorer build \
  projects/balancing-cube/explorer --model-revision reviewed-20261019-1
python -m http.server 8791 --bind 127.0.0.1 \
  --directory projects/balancing-cube/explorer
```

`http://127.0.0.1:8791/` を開きます。停止は Ctrl-C です。配信するのは生成済みの
静的ファイルだけです。正本を書き換える API は公開しません。wheel にも画面の
ソースを含めるため、Node.js は不要です。

現在のレビュー済みスナップショットは、要求22件、グループ7件、関連パラメータ37件、
計画中の検証ケース22件を参照します。件数をコードで固定せず、選択した
スナップショットの ID と revision から取得します。`--model-id` と
`--model-revision` で対象を指定できます。revision を省略すると、その ID の最新モデルを
選び、記録されている承認状態をそのまま表示します。

`provenance.json` と `explorer-manifest.json` に、モデル・スナップショット・
記録集合・生成ファイルのハッシュを保存します。英日要求文は同じ正本から取得します。
草案の構成図は、指定された基準モデルと revision が一致する場合だけ表示します。
`satisfy` は設計意図を表す元の版への関係を保ち、検証合格や新しい要求版への適用を
自動的に認めません。

画面の編集はブラウザー内の改訂案です。保存領域をプロジェクトとモデルのハッシュで
分離し、エクスポートにモデルとスナップショットの参照を含めます。画面からの要求承認、
正本の取込、ベースライン変更は行いません。人間の判断は版管理された記録に残します。

標準 API との境界は既存の [`onepiece sysml`](../en/sysml_api.md) を使います。
この画面自体が SysML 言語全体を実装しているという意味ではありません。

ECLSS と scrubber の比較画面は任意です。`.[explorer]` をインストールして
`--engineering-agents-root /path/to/engineering_agents` を指定すると、選択した
チェックアウトの設定とハッシュを記録します。これらの設定は One-Piece の
レビュー済み要求と区別します。

[データの保存と取得](dataset_storage.md) · [英語版](../en/requirements_explorer.md)
