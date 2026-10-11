# OMG Systems Modeling APIとの接続

One-Piece 0.2.0は、OMG Systems Modeling API and Services 1.0のREST/HTTP参照境界を提供する。対象は **ProjectService Read** と **ElementNavigationService**。正式なパス、UUID、Project／Branch／Commit、要素・関係の取得、方向、ページ分割、Error形式を使う。書込、Query、OSLC、全サービスやSysML言語全体の準拠は対象外である。[対応範囲・交換形式・試験の詳細](../en/sysml_api.md)を正本とする。

最小の `onepiece-annotation-graph-1` では、プロジェクトをPackage、記録の各版をComment、その対応をAnnotation、5種類のトレースを名前付きDependencyとして表す。Comment本文には要求、KDP、詳細パラメータの値・単位・不確かさ・状態・出典・成果物ハッシュを含む元JSONをそのまま保持する。Dependencyの端点は特定のIDとrevisionを指す。異なる版を同時に保持でき、過去の証拠が新しい要求へ付け替わることはない。

これは標準APIで保存・取得できる注釈グラフである。ネイティブのRequirementDefinitionやAttributeDefinitionへの意味変換は今後の段階であり、`satisfy`／`verify` の名前だけでSysML固有の適合や実機合格を主張しない。外部ツールは標準APIでグラフを受け取った上で、用途に応じた意味変換を追加できる。

`onepiece --store STORE sysml export /tmp/model.json --project PROJECT` で交換ファイルとSHA-256を生成する。内部の `commit_request` が外部の標準Commit作成APIへ渡せる本文である。交換ファイル全体をそのままPOSTしない。`sysml check` は公式スキーマと元記録からの再生成一致を検査する。`sysml import --sha256 HASH` は同じ注釈プロファイルだけを検査付きで復元する。成果物の実体は別途、従来の証拠パックまたは `--artifacts-root` から復元する。

`sysml serve --port 9000` は明示したときだけ前面で動き、127.0.0.1に限定する。開始時点の記録集合を固定し、動作中にCommitの内容を書き換えない。新たな記録は再起動または再exportで別Commitとして公開する。全履歴を含む記録JSONがSSOTであり、APIや交換ファイルはその投影である。

公式のOpenAPI／JSON Schemaをwheelへ同梱し、取得元とSHA-256を固定する。選択した参照サービスに適用されるAnnex Aの動作、往復取込、版参照、書込拒否をローカルで試験する。第三者製リポジトリとの往復確認や独立した認証は未実施である。
