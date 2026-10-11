# Balancing Cubeの要求草案

この表示は`standards-draft-20261011-2`の正本JSONから生成する。`python projects/balancing-cube/migrate_standards.py --write-docs`で再生成する。

英語が原文であり、日本語はその翻訳である。改訂したすべての要求文は、人間による確認が必要な草案である。

優先順位はISO/IEC/IEEE 29148:2018、NASAのシステムズエンジニアリング標準と要求記述ガイド、ASD-STE100 Issue 9の順である。
要求文の規範語はshallとする。NASA Appendix Cはshallを要求の規範語とする。ASD-STE100 Issue 9の辞書はshallを非承認語、mustを代替語とするが、ここでは指定された優先順位に従う。
能動態、定義した技術名、文の長さなど、上位の方針と両立するSTE規則を適用する。ISO規格の全文が得られず条項単位の審査は未実施である。STE辞書の全語審査と規格適合認証も未実施である。

7個の整理用コンテナは独立した試験義務ではない。22個の義務には、元の複合要求から分割した8個の子要求を含む。
検証ケースは計画のみである。新しい実機結果はない。過去の数値的証拠は、元の版への参照を維持する。

[執筆標準](../engineering/standards.md)、[システムモデル](system_model.md)、[APIの範囲](sysml_api.md)を参照する。

## cube.req.system: システム要求集合

`cube.req.system@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

cube.req.operation, cube.req.mechanical, cube.req.gnc, cube.req.verification, R-DRIVE, R-TILT, R-RMS, R-DRIFT

## cube.req.operation: 運用要求集合

`cube.req.operation@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

R-HOLD, R-REPEAT

## cube.req.mechanical: 機械要求集合

`cube.req.mechanical@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

C-FIT, C-JAPAN, C-PRINT, C-BUDGET

## cube.req.gnc: 制御要求集合

`cube.req.gnc@standards-draft-20261011-2` · `cube.gnc` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

R-YAW

## cube.req.verification: 検証基盤の要求集合

`cube.req.verification@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

R-VISION, R-SYNC, R-MODEL, R-TRACE

## C-FIT: 製作と搭載の要求集合

`C-FIT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

C-FIT-PRINT, C-FIT-MATERIAL, C-FIT-INSTALL

## R-DRIVE: 駆動限界の要求集合

`R-DRIVE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

このノードは要求をまとめる。独立した試験義務ではない。

R-DRIVE-TORQUE, R-DRIVE-SPEED, R-DRIVE-TEMP, R-DRIVE-VOLTAGE, R-DRIVE-CURRENT

## M-VERTEX: 頂点保持のミッション

`M-VERTEX@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

Cubeは、実機試験環境で3個のリアクションホイールを用いて頂点姿勢を保持しなければならない。

このミッションではCubeの構想を実機で示す必要がある。


判定基準：実機試験で頂点姿勢の保持を示す。

検証方法：test

元の要求文の状態：confirmed

- `M-VERTEX.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

Source: `M-VERTEX@trace-20261010-2`; SHA-256 `4799937318ed4f7404c2cee216a46f84f04fab3d9b215fc0a964588190ae652d`.

## C-JAPAN: 日本への部品供給

`C-JAPAN@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Cubeは、供給元が日本へ供給できる部品を使用しなければならない。

ユーザーは日本で部品を入手する必要がある。


判定基準：購入するすべての部品について、日本への供給元を確認する。

検証方法：inspection

元の要求文の状態：confirmed

- `C-JAPAN.TBR.1`: 許容する納期と供給費用を定義する。原文の「容易」には数値限界がない。

Source: `C-JAPAN@trace-20261010-2`; SHA-256 `a30d6923b8b4218c9a9713f23f4f1c52982e7c89dc49c850aa8ebb7575487a13`.

## C-PRINT: 筐体の製作

`C-PRINT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Cubeの筐体は、指定された3Dプリンタで製作できる部品でなければならない。

ユーザーは友人の3Dプリンタを使用する意図を持つ。


判定基準：指定された3Dプリンタで筐体を製作できることを確認する。

検証方法：demonstration

元の要求文の状態：confirmed

- `C-PRINT.TBR.1`: 指定するプリンタ、材料、造形条件を特定する。

Source: `C-PRINT@trace-20261010-2`; SHA-256 `e926acac7b34ad0bae42e8af5b332e5ef4462ebf90f047f9fc67285da2627b6e`.

## C-BUDGET: 初回試作の費用

`C-BUDGET@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Cubeの初回試作の費用は、承認された予算以下でなければならない。

試作には明示的な費用上限が必要である。


判定基準：初回試作の費用を、D-BUDGETで承認した金額以下とする。

検証方法：analysis

元の要求文の状態：draft

- `C-BUDGET.TBR.1`: 予算と費用の範囲を設定する。D-BUDGETの値は未設定である。

Source: `C-BUDGET@trace-20261010-2`; SHA-256 `a1fd01730722f6c6718dd3b5f407302457f30c889412198ffefb58a3647b24cc`.

## R-HOLD: 手動解放後の保持

`R-HOLD@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

手動で設置して解放した後、Cubeは外部からの支持なしで頂点姿勢を30 s以上保持しなければならない。

初回試作は手動設置から開始する。自動起立はこの草案の対象外である。

条件：手動で解放した時点から最初の30 sを保持区間とする。

判定基準：実機で外部支持のない頂点保持時間を30 s以上とする。

検証方法：test

元の要求文の状態：draft

- `R-HOLD.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

Source: `R-HOLD@trace-20261010-2`; SHA-256 `f0fcce1b22e2d58b3463a9882ed9a8bbccf720bc6657da40a42a3f20b2a5c0cf`.

## R-TILT: 最大傾斜角

`R-TILT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

保持区間中、Cubeは傾斜角を5 deg以下に保たなければならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

条件：手動で解放した時点から最初の30 sを保持区間とする。

判定基準：保持区間全体について最大傾斜角を5 deg以下とする。

検証方法：test

元の要求文の状態：draft

- `R-TILT.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

Source: `R-TILT@trace-20261010-2`; SHA-256 `b4a542e2c2f5cebfa4deaa111a9bda7e1fea97d68dead7b743f5618913873a76`.

## R-RMS: 傾斜角のRMS

`R-RMS@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

保持区間中、Cubeの傾斜角のRMSは2 deg以下でなければならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

条件：手動で解放した時点から最初の30 sを保持区間とする。

判定基準：保持区間全体について傾斜角のRMSを2 deg以下とする。

検証方法：test

元の要求文の状態：draft

- `R-RMS.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

Source: `R-RMS@trace-20261010-2`; SHA-256 `2ceec81d22e96442798bf229832d6eda67871b3b78fa2a546c84353595325500`.

## R-DRIFT: 接地点の移動

`R-DRIFT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

保持区間中、Cubeの接地点は初期位置から2 mmを超えて移動してはならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

条件：手動で解放した時点から最初の30 sを保持区間とする。

判定基準：保持区間全体について接地点の移動を2 mm以下とする。

検証方法：test

元の要求文の状態：draft

- `R-DRIFT.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

Source: `R-DRIFT@trace-20261010-2`; SHA-256 `7eab0b2b715e5047db9905d881508a7a862b328e3824003a1d247385abe58968`.

## R-REPEAT: 保持試験の反復

`R-REPEAT@standards-draft-20261011-2` · `cube.system` · `draft` · `not_run`

固定した試験条件で、Cubeは10回の試行のうち9回以上、保持試験に合格しなければならない。

反復試行により、定めた試験条件での再現性を確認する。


判定基準：同じ実機試験条件で10回実施し、9回以上の保持試験成功を得る。

検証方法：test

元の要求文の状態：draft

- `R-REPEAT.TBR.1`: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

- `R-REPEAT.TBR.2`: 試験前に試行順序、リセット方法、保持試験の合格規則全体を定義する。

Source: `R-REPEAT@trace-20261010-2`; SHA-256 `3af5a6d2e1248bee831cfb28d5f6f5ce14a728987cabdfc4970c63cdf250e8d1`.

## R-YAW: ヨー角速度の監視

`R-YAW@standards-draft-20261011-2` · `cube.gnc` · `draft` · `not_run`

保持区間中、制御系はヨー角速度のRMSを監視しなければならない。

原文は監視を求めている。固定したヨー方位は要求していない。

条件：手動で解放した時点から最初の30 sを保持区間とする。

判定基準：ヨー角速度のRMSを記録する。5 deg/sは目標値であり、合否の閾値ではない。

検証方法：test

元の要求文の状態：draft

- `R-YAW.TBR.1`: 5 deg/sを限界値にするか決定する。サンプリング周波数とRMSの計算方法を定義する。

Source: `R-YAW@trace-20261010-2`; SHA-256 `05910a799d4afe495aedfc265b6832f5a6e62365bfb7a98b6430589ee81e1c41`.

## R-VISION: 独立した姿勢計測

`R-VISION@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

独立した姿勢計測系の角度の標準不確かさは、0.5 deg以下でなければならない。

独立した計測により、Cubeが使用する姿勢推定値を確認する。


判定基準：独立した姿勢計測の角度の標準不確かさを0.5 deg以下とする。

検証方法：test

元の要求文の状態：draft

- `R-VISION.TBR.1`: 姿勢成分、校正方法、不確かさの計算方法を定義する。この草案では標準不確かさを用いる。

Source: `R-VISION@trace-20261010-2`; SHA-256 `c8d56c9806b3af8fd91bda34f31fc689ab3daaeaa8f761a075d2e0a804f17f99`.

## R-SYNC: 動画とMCUの時刻の対応

`R-SYNC@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

検証基盤は、動画とMCUのタイムスタンプ間の時刻関係を、0.005 s以下の時刻不確かさで算出しなければならない。

独立した計測と制御器のログを比較するには、時刻の対応を把握する必要がある。


判定基準：動画とMCUの対応時刻の不確かさを0.005 s以下とする。

検証方法：test

元の要求文の状態：draft

- `R-SYNC.TBR.1`: 時刻不確かさと校正方法を定義する。60 frame/sの動画だけでは0.005 sを示せない。

Source: `R-SYNC@trace-20261010-2`; SHA-256 `8312021ccda4e9af192f732206a41e34ae46eb83cd60f9409c3f099dca5ce96f`.

## R-MODEL: モデルの独立比較

`R-MODEL@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

検証基盤は、対応する試験条件で、モデルの結果と独立した実測値を比較しなければならない。

CPUとGPUの整合は数値的な挙動を確認する。モデル誤差の評価には実測値が必要である。


判定基準：対応する試験条件でモデル誤差を算出する。許容値と各量の単位は未定である。

検証方法：analysis

元の要求文の状態：draft

- `R-MODEL.TBR.1`: 合否判定の前に、比較する量、単位、誤差限界、独立した実測データを定義する。

Source: `R-MODEL@trace-20261010-2`; SHA-256 `f3f7fa2059d2740844b4b22c5e81f323b316636c9848c3f400f958000a56997b`.

## R-TRACE: 実行の厳密な版参照

`R-TRACE@standards-draft-20261011-2` · `cube.verification` · `draft` · `not_run`

検証基盤は、各実行について、要求、KDP、設計、条件、結果の厳密な版を特定しなければならない。

厳密な参照により変更と証拠の適用範囲が分かる。


判定基準：各実行の要求、KDP、設計、条件、結果の参照に欠落と曖昧な版を残さない。

検証方法：inspection

元の要求文の状態：confirmed

Source: `R-TRACE@trace-20261010-2`; SHA-256 `5d961ba1f586672fa4d92e60a94a6978f8c2d5b523564caf13444dca46398cbf`.

## R-DRIVE-TORQUE: モーターのトルク限界

`R-DRIVE-TORQUE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

各モーターのトルクは、測定した各回転速度における承認済みの最小値と最大値の間でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。


判定基準：対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。

検証方法：test

元の要求文の状態：draft

- `R-DRIVE-TORQUE.TBR.1`: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-SPEED: ホイールの回転速度限界

`R-DRIVE-SPEED@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

各リアクションホイールの回転速度の大きさは、その組立体の承認済みの限界以下でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。


判定基準：対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。

検証方法：test

元の要求文の状態：draft

- `R-DRIVE-SPEED.TBR.1`: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-TEMP: 部品の温度限界

`R-DRIVE-TEMP@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

各モーターとドライバの温度は、それぞれの承認済みの最小値と最大値の間でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。


判定基準：対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。

検証方法：test

元の要求文の状態：draft

- `R-DRIVE-TEMP.TBR.1`: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-VOLTAGE: バス電圧の限界

`R-DRIVE-VOLTAGE@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

駆動系は、バス電圧を各接続部品の承認済みの最小値と最大値の間に保たなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。


判定基準：対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。

検証方法：test

元の要求文の状態：draft

- `R-DRIVE-VOLTAGE.TBR.1`: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## R-DRIVE-CURRENT: バス電流の限界

`R-DRIVE-CURRENT@standards-draft-20261011-2` · `cube.actuation` · `draft` · `not_run`

駆動系は、バス電流をバス回路の承認済みの最小値と最大値の間に保たなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。


判定基準：対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。

検証方法：test

元の要求文の状態：draft

- `R-DRIVE-CURRENT.TBR.1`: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

- `R-DRIVE-CURRENT.TBR.2`: バス回路の定格を定義する。バス電流は各モーターの巻線電流を示さない。

Source: `R-DRIVE@trace-20261010-2`; SHA-256 `5f55625c658011d360d978b465484866f85152b9fb3a7a46960d75072d6e264e`.

## C-FIT-PRINT: 造形部品の寸法

`C-FIT-PRINT@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

筐体の各造形部品の寸法は、3Dプリンタの指定された造形限界以下でなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。


判定基準：指定する造形範囲、材料一覧、搭載空間の該当条件を満たす。

検証方法：inspection

元の要求文の状態：draft

- `C-FIT-PRINT.TBR.1`: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.

## C-FIT-MATERIAL: 造形材料の選定

`C-FIT-MATERIAL@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

Cubeの筐体は、指定された3Dプリンタの承認済み材料一覧にある造形材料を使用しなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。


判定基準：指定する造形範囲、材料一覧、搭載空間の該当条件を満たす。

検証方法：inspection

元の要求文の状態：draft

- `C-FIT-MATERIAL.TBR.1`: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.

## C-FIT-INSTALL: 搭載部品の寸法

`C-FIT-INSTALL@standards-draft-20261011-2` · `cube.mechanical` · `draft` · `not_run`

各搭載部品の寸法は、Cube筐体内の搭載空間に指定された寸法以下でなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。


判定基準：指定する造形範囲、材料一覧、搭載空間の該当条件を満たす。

検証方法：inspection

元の要求文の状態：draft

- `C-FIT-INSTALL.TBR.1`: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

Source: `C-FIT@trace-20261010-2`; SHA-256 `521cf3051c08776477a9bf539ed2b263c2e4c269dd4efb4502c9914b3da5e074`.
