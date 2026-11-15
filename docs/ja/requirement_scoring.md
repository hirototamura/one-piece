# 要求の不足量によるスコアリング

合意済みの方式は `requirement_max_deficit_v1`。正本の契約は
`cube.evaluation.requirement-shortfall@requirement-scoring-20261115-2` である。
`PYTHONPATH=src python projects/balancing-cube/adopt_requirement_scoring.py` で
このチェックアウトのCubeストアへ取り込む。同じ内容の再実行は冪等となる。

`onepiece.scoring.evaluate_requirements(contract, measurements, domain=...)` は、
要求の厳密な版、測定値、限界値、単位、合否、不足量を返す。
証拠領域は `hardware` または `simulation`。渡す測定値の出典・妥当性は呼出側が担い、
この計算自体は実機試験や設計採用を行わない。シミュレーションでは宣言した4要求の代理評価だけを判定し、
その他の要求・制約は未判定とする。

上限要求の不足量は `max(0, x/L - 1)`、下限要求は `max(0, 1 - x/L)`。
真偽値の違反は1、数値一致の要求は絶対相対差、目標0の場合は0/1とする。
欠測・非有限値・限界未確定・型の不一致は未判定で、不足量はnullとなる。
反復試験には `successful_hold_trials_sample_count: 10` も必要であり、
別の数値試験行列を10回の実機試験と見なさない。

必須要求に違反があれば、他の値にかかわらず全体は不合格となる。
未判定が残れば全体の合格を出さない。探索対象の合否は別に保持する。
目的は独立した要求と各試行を通じた最大不足量Dの最小化である。
従来の「大きいほど良い」クライアント向けに `score = -max_deficit` を返す。
探索対象での合格を不合格より優先し、要求達成後はすべて0点で同点とする。
重み、KDPの値への加点、余裕への加点、追加の回復目標は使わない。
ミッション・反復試験と、その子の性能判定を重複して加算しない。

`onepiece.cube_scoring.evaluate_cube_records(records, snapshot)` は、解放時から最初の10秒を評価する。
最大値は既存の軌跡サンプルを使う。RMSは傾斜の二乗を台形積分し、10秒の端点を補間する。
従来の最後の1秒のサンプルRMSとは区別する。欠測・非有限値・時刻の逆転・間隔の欠落では合格を出さない。
途中停止でも保持時間や観測済み最大値の不足量は返すが、全区間RMSは未判定のままとする。
判明分は `max_known_deficit` に残し、探索対象の不足量が一つでも不明なら
`max_deficit` と得点はnullにする。その候補は完全な採点候補として順位付けしない。
試行行列の空・欠落・重複は、シナリオ集計側で採点前に拒否する。

実行用の子版 `cube.simulation.snapshot@requirement-scoring-20261115-2` は、
`bottom-corner-000-20261017-3` の下側取付・corner-000の力学と制御器を保持する。
要求・KDPは `requirements-review-20261115-3` を参照し、保持区間と評価契約を変更する。
既存のdomain・解放条件・seedの行列は開発条件として維持する。
これは8頂点の実証でも、R-REPEATの実機反復試験でもない。
現在の数値代理評価はR-HOLD、R-TILT、R-RMS、R-DRIFTの4要求である。
電気・熱・製造・頂点識別などの未取得の証拠は不明のままとし、
シミュレーションの `physical_status` は常に `unjudged` とする。

Engineering Agentsは評価器2モジュールのソースハッシュを固定し、要求ごとの結果を保存し、要求ごとの最も悪い試行と未判定の参照をエージェントへ渡す。
記憶から最良スコアを選ぶ際も、同じ評価契約の版に限定する。
過去の契約と結果は元の式を保持し、移行時に実験を自動で再採点しない。

[英語版](../en/requirement_scoring.md)
