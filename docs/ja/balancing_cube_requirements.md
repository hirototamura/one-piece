# Balancing Cubeのレビュー済み要求

`reviewed-20261019-1` · human review: 2026-10-19 · reviewer: hirototamura

要求文と機能・構成品への割当は人によるレビュー済み。検証結果、未解決事項、過去の証拠の適用範囲は別に管理する。

Canonical baseline: `cube.baseline.requirements-allocation@reviewed-20261019-1`.

22個の義務と7個の整理用グループを含む。未確定の数値限界と検証手順は未確定のままであり、レビューは実機試験の合格を意味しない。

Regenerate: `python projects/balancing-cube/review_requirements.py --write-docs`.

## C-BUDGET: 初回試作の費用

`C-BUDGET@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Cubeの初回試作の費用は、承認された予算以下でなければならない。

試作には明示的な費用上限が必要である。

Acceptance / 合否基準: {"limit_ref": {"id": "D-BUDGET", "revision": "reviewed-20261019-1"}, "metric": "prototype_cost", "operator": "<=", "unit": "JPY"}

Allocation: cube.system

Open items / 未解決事項:
- C-BUDGET.TBR.1: 予算と費用の範囲を設定する。D-BUDGETの値は未設定である。

## C-FIT: 製作と搭載の要求集合

`C-FIT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## C-FIT-INSTALL: 搭載部品の寸法

`C-FIT-INSTALL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

各搭載部品の寸法は、Cube筐体内の搭載空間に指定された寸法以下でなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "installed_components_inside_assigned_space", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Open items / 未解決事項:
- C-FIT-INSTALL.TBR.1: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

## C-FIT-MATERIAL: 造形材料の選定

`C-FIT-MATERIAL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Cubeの筐体は、指定された3Dプリンタの承認済み材料一覧にある造形材料を使用しなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "material_on_printer_material_list", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-FIT-MATERIAL.TBR.1: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

## C-FIT-PRINT: 造形部品の寸法

`C-FIT-PRINT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

筐体の各造形部品の寸法は、3Dプリンタの指定された造形限界以下でなければならない。

この要求は、元の複合的な製作要求を構成する一項目である。

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "printed_parts_inside_build_volume", "operator": "==", "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-FIT-PRINT.TBR.1: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

## C-JAPAN: 日本への部品供給

`C-JAPAN@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Cubeは、供給元が日本へ供給できる部品を使用しなければならない。

ユーザーは日本で部品を入手する必要がある。

Acceptance / 合否基準: {"metric": "components_available_for_supply_to_japan", "operator": "==", "unit": "1", "value": "all_purchased_components"}

Allocation: cube.component.frame-housing, cube.component.vertex-contact, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Open items / 未解決事項:
- C-JAPAN.TBR.1: 許容する納期と供給費用を定義する。原文の「容易」には数値限界がない。

## C-PRINT: 筐体の製作

`C-PRINT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Cubeの筐体は、指定された3Dプリンタで製作できる部品でなければならない。

ユーザーは友人の3Dプリンタを使用する意図を持つ。

Acceptance / 合否基準: {"metric": "housing_manufacturable", "operator": "==", "requirement_ref": {"id": "C-FIT-PRINT", "revision": "reviewed-20261019-1"}, "unit": "1", "value": true}

Allocation: cube.component.frame-housing

Open items / 未解決事項:
- C-PRINT.TBR.1: 指定するプリンタ、材料、造形条件を特定する。

## M-VERTEX: 頂点保持のミッション

`M-VERTEX@reviewed-20261019-1` · reviewed · human_reviewed · not_run

Cubeは、実機試験環境で3個のリアクションホイールを用いて頂点姿勢を保持しなければならない。

このミッションではCubeの構想を実機で示す必要がある。

Acceptance / 合否基準: {"domain": "hardware", "metric": "vertex_hold_demonstrated", "operator": "==", "unit": "1", "value": true}

Allocation: cube.system

Open items / 未解決事項:
- M-VERTEX.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-DRIFT: 接地点の移動

`R-DRIFT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

保持区間中、Cubeの接地点は初期位置から2 mmを超えて移動してはならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_contact_point_displacement", "operator": "<=", "unit": "mm", "value": 2}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-DRIFT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-DRIVE: 駆動限界の要求集合

`R-DRIVE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## R-DRIVE-CURRENT: バス電流の限界

`R-DRIVE-CURRENT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

駆動系は、バス電流をバス回路の承認済みの最小値と最大値の間に保たなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_current_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-CURRENT.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。
- R-DRIVE-CURRENT.TBR.2: バス回路の定格を定義する。バス電流は各モーターの巻線電流を示さない。

## R-DRIVE-SPEED: ホイールの回転速度限界

`R-DRIVE-SPEED@reviewed-20261019-1` · reviewed · human_reviewed · not_run

各リアクションホイールの回転速度の大きさは、その組立体の承認済みの限界以下でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "wheel_speed_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.generate-torque

Open items / 未解決事項:
- R-DRIVE-SPEED.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-TEMP: 部品の温度限界

`R-DRIVE-TEMP@reviewed-20261019-1` · reviewed · human_reviewed · not_run

各モーターとドライバの温度は、それぞれの承認済みの最小値と最大値の間でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "component_temperature_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-TEMP.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-TORQUE: モーターのトルク限界

`R-DRIVE-TORQUE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

各モーターのトルクは、測定した各回転速度における承認済みの最小値と最大値の間でなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "motor_torque_envelope_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.generate-torque

Open items / 未解決事項:
- R-DRIVE-TORQUE.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-VOLTAGE: バス電圧の限界

`R-DRIVE-VOLTAGE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

駆動系は、バス電圧を各接続部品の承認済みの最小値と最大値の間に保たなければならない。

この要求は、元の複合的な駆動要求を構成する一項目である。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_voltage_limit_exceeded", "operator": "==", "unit": "1", "value": false}

Allocation: cube.function.manage-power

Open items / 未解決事項:
- R-DRIVE-VOLTAGE.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-HOLD: 手動解放後の保持

`R-HOLD@reviewed-20261019-1` · reviewed · human_reviewed · not_run

手動で設置して解放した後、Cubeは外部からの支持なしで頂点姿勢を30 s以上保持しなければならない。

初回試作は手動設置から開始する。自動起立はこの草案の対象外である。

Acceptance / 合否基準: {"domain": "hardware", "metric": "unsupported_vertex_hold_duration", "operator": ">=", "unit": "s", "value": 30}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-HOLD.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-MODEL: モデルの独立比較

`R-MODEL@reviewed-20261019-1` · reviewed · human_reviewed · not_run

検証基盤は、対応する試験条件で、モデルの結果と独立した実測値を比較しなければならない。

CPUとGPUの整合は数値的な挙動を確認する。モデル誤差の評価には実測値が必要である。

Acceptance / 合否基準: {"domain": "hardware_model_comparison", "metric": "model_error", "operator": "<=", "unit": "defined_per_quantity", "value": null}

Allocation: cube.function.measure-motion, cube.function.evaluate-trace

Open items / 未解決事項:
- R-MODEL.TBR.1: 合否判定の前に、比較する量、単位、誤差限界、独立した実測データを定義する。

## R-REPEAT: 保持試験の反復

`R-REPEAT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

固定した試験条件で、Cubeは10回の試行のうち9回以上、保持試験に合格しなければならない。

反復試行により、定めた試験条件での再現性を確認する。

Acceptance / 合否基準: {"domain": "hardware", "metric": "successful_hold_trials", "operator": ">=", "sample_count": 10, "unit": "trials/10", "value": 9}

Allocation: cube.function.control-balance, cube.function.evaluate-trace

Open items / 未解決事項:
- R-REPEAT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。
- R-REPEAT.TBR.2: 試験前に試行順序、リセット方法、保持試験の合格規則全体を定義する。

## R-RMS: 傾斜角のRMS

`R-RMS@reviewed-20261019-1` · reviewed · human_reviewed · not_run

保持区間中、Cubeの傾斜角のRMSは2 deg以下でなければならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Acceptance / 合否基準: {"domain": "hardware", "metric": "tilt_angle_rms", "operator": "<=", "unit": "deg", "value": 2}

Allocation: cube.function.control-balance

Open items / 未解決事項:
- R-RMS.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-SYNC: 動画とMCUの時刻の対応

`R-SYNC@reviewed-20261019-1` · reviewed · human_reviewed · not_run

検証基盤は、動画とMCUのタイムスタンプ間の時刻関係を、0.005 s以下の時刻不確かさで算出しなければならない。

独立した計測と制御器のログを比較するには、時刻の対応を把握する必要がある。

Acceptance / 合否基準: {"domain": "hardware", "metric": "video_mcu_time_uncertainty", "operator": "<=", "unit": "s", "value": 0.005}

Allocation: cube.function.capture-synchronize

Open items / 未解決事項:
- R-SYNC.TBR.1: 時刻不確かさと校正方法を定義する。60 frame/sの動画だけでは0.005 sを示せない。

## R-TILT: 最大傾斜角

`R-TILT@reviewed-20261019-1` · reviewed · human_reviewed · not_run

保持区間中、Cubeは傾斜角を5 deg以下に保たなければならない。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_tilt_angle", "operator": "<=", "unit": "deg", "value": 5}

Allocation: cube.function.control-balance, cube.function.maintain-contact

Open items / 未解決事項:
- R-TILT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-TRACE: 実行の厳密な版参照

`R-TRACE@reviewed-20261019-1` · reviewed · human_reviewed · not_run

検証基盤は、各実行について、要求、KDP、設計、条件、結果の厳密な版を特定しなければならない。

厳密な参照により変更と証拠の適用範囲が分かる。

Acceptance / 合否基準: {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "unit": "count", "value": 0}

Allocation: cube.function.capture-synchronize, cube.function.evaluate-trace

## R-VISION: 独立した姿勢計測

`R-VISION@reviewed-20261019-1` · reviewed · human_reviewed · not_run

独立した姿勢計測系の角度の標準不確かさは、0.5 deg以下でなければならない。

独立した計測により、Cubeが使用する姿勢推定値を確認する。

Acceptance / 合否基準: {"domain": "hardware", "metric": "attitude_standard_uncertainty", "operator": "<=", "unit": "deg", "value": 0.5}

Allocation: cube.function.measure-motion

Open items / 未解決事項:
- R-VISION.TBR.1: 姿勢成分、校正方法、不確かさの計算方法を定義する。この草案では標準不確かさを用いる。

## R-YAW: ヨー角速度の監視

`R-YAW@reviewed-20261019-1` · reviewed · human_reviewed · not_run

保持区間中、制御系はヨー角速度のRMSを監視しなければならない。

原文は監視を求めている。固定したヨー方位は要求していない。

Acceptance / 合否基準: {"metric": "yaw_rate_rms_recorded", "operator": "==", "target_only": {"unit": "deg/s", "value": 5}, "unit": "1", "value": true}

Allocation: cube.function.estimate-attitude

Open items / 未解決事項:
- R-YAW.TBR.1: 5 deg/sを限界値にするか決定する。サンプリング周波数とRMSの計算方法を定義する。

## cube.req.gnc: 制御要求集合

`cube.req.gnc@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## cube.req.mechanical: 機械要求集合

`cube.req.mechanical@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## cube.req.operation: 運用要求集合

`cube.req.operation@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## cube.req.system: システム要求集合

`cube.req.system@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。

## cube.req.verification: 検証基盤の要求集合

`cube.req.verification@reviewed-20261019-1` · reviewed · human_reviewed · not_run

このノードは要求をまとめる。独立した試験義務ではない。
