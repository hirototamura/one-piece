# Balancing Cubeの要求と制約

`requirements-review-20261115-3` · 2026-11-15

要求19件、分類グループ7件、別枠の制約3件。検証は計画段階・未実行。

`O-HOLD-INTERVAL = 10 s` · [Review / 改訂の根拠](cube_requirements_review.md)

Regenerate: `python projects/balancing-cube/apply_requirement_review.py --write-docs`.

## C-BUDGET: 初回試作の費用

`C-BUDGET@requirements-review-20261115-3` · constraint · project · not_run

Cubeの初回試作の費用は、承認された予算以下でなければならない。

Acceptance / 合否基準: {"limit_ref": {"id": "D-BUDGET", "revision": "requirements-review-20261115-3"}, "metric": "prototype_cost", "operator": "<=", "unit": "JPY"}

試作には明示的な費用上限が必要である。

Verification method: analysis

Open items / 未解決事項:
- C-BUDGET.TBR.1: 予算と費用の範囲を設定する。D-BUDGETの値は未設定である。

## C-FIT: 製作と搭載の要求集合

`C-FIT@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.mechanical

## C-FIT-INSTALL: 搭載部品の寸法

`C-FIT-INSTALL@requirements-review-20261115-3` · requirement · subsystem · not_run

各搭載部品の寸法は、Cube筐体内の搭載空間に指定された寸法以下でなければならない。

Acceptance / 合否基準: {"limits_status": "unresolved", "metric": "installed_components_inside_assigned_space", "operator": "==", "unit": "1", "value": true}

この要求は、元の複合的な製作要求を構成する一項目である。

Derived from: C-FIT

Allocation: cube.component.frame-housing, cube.component.reaction-wheels, cube.component.motor-drivers, cube.component.imu, cube.component.controller, cube.component.power-bus

Verification method: inspection

Open items / 未解決事項:
- C-FIT-INSTALL.TBR.1: プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。

## C-FIT-PRINT: 造形部品の寸法

`C-FIT-PRINT@requirements-review-20261115-3` · constraint · manufacturing · not_run

筐体の各造形部品の寸法は、3Dプリンタの指定された造形限界以下でなければならない。

Acceptance / 合否基準: {"metric": "printed_parts_inside_build_volume", "operator": "==", "unit": "1", "value": true}

Conditions / 条件:
- 各造形部品の造形姿勢で寸法を確認する。組立後のCube全体に造形範囲を適用しない。

この要求は、元の複合的な製作要求を構成する一項目である。

Verification method: inspection

Open items / 未解決事項:
- C-FIT-PRINT.TBR.1: Bambu Lab A1で各部品の形状、造形姿勢、工程上の余白を確認する。

## C-JAPAN: 日本への部品供給

`C-JAPAN@requirements-review-20261115-3` · constraint · manufacturing · not_run

Cubeは、供給元が日本へ供給できる部品を使用しなければならない。

Acceptance / 合否基準: {"metric": "components_available_for_supply_to_japan", "operator": "==", "unit": "1", "value": "all_purchased_components"}

ユーザーは日本で部品を入手する必要がある。

Verification method: inspection

Open items / 未解決事項:
- C-JAPAN.TBR.1: 許容する納期と供給費用を定義する。原文の「容易」には数値限界がない。

## C-PRINT: 筐体の製作

`C-PRINT@requirements-review-20261115-3` · requirement · subsystem · not_run

Cubeの筐体は、指定された3Dプリンタで製作できる部品でなければならない。

Acceptance / 合否基準: {"metric": "housing_manufacturable", "operator": "==", "requirement_ref": {"id": "C-FIT-PRINT", "revision": "requirements-review-20261115-3"}, "unit": "1", "value": true}

ユーザーは友人の3Dプリンタを使用する意図を持つ。

Derived from: cube.req.mechanical

Allocation: cube.component.frame-housing

Verification method: demonstration

Open items / 未解決事項:
- C-PRINT.TBR.1: Bambu Lab A1の造形条件を決め、製作可能性を確認する。材料は設計上の選択として扱う。

## M-VERTEX: 頂点保持のミッション

`M-VERTEX@requirements-review-20261115-3` · requirement · mission · not_run

Cubeは、3個のリアクションホイールを用いて8頂点のそれぞれで倒立保持しなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "distinct_corners_demonstrated", "operator": "==", "unit": "count", "value": 8}

このミッションではCubeの構想を実機で示す必要がある。

Allocation: cube.system

Verification method: test

Open items / 未解決事項:
- M-VERTEX.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-DETECT: 支持頂点の自動識別

`R-DETECT@requirements-review-20261115-3` · requirement · subsystem · not_run

制御系はバランス保持を開始する前に、Cubeの8頂点から対象の支持頂点を自動識別しなければならない。

Acceptance / 合否基準: {"metric": "correctly_identified_support_corners", "operator": "==", "value": 8, "unit": "count", "domain": "hardware"}

Conditions / 条件:
- 保持制御を有効にする前に、姿勢・センサ情報から支持頂点を識別する。

8頂点のミッションでは、保持制御の前に支持頂点に対応する座標系を選ぶ必要がある。

Derived from: M-VERTEX

Allocation: cube.function.estimate-attitude

Verification method: test

Open items / 未解決事項:
- R-DETECT.TBR.1: 有効な初期姿勢・センサ条件と、頂点を一意に識別できない場合の扱いを定義する。数値許容差は追加しない。

## R-DRIFT: 接地点の移動

`R-DRIFT@requirements-review-20261115-3` · requirement · system · not_run

保持区間中、Cubeの接地点は初期位置から2 mmを超えて移動してはならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_contact_point_displacement", "operator": "<=", "unit": "mm", "value": 2}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-DRIFT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-DRIVE: 駆動限界の要求集合

`R-DRIVE@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.system

## R-DRIVE-CURRENT: バス電流の限界

`R-DRIVE-CURRENT@requirements-review-20261115-3` · requirement · subsystem · not_run

駆動系は、バス電流をバス回路の承認済みの最小値と最大値の間に保たなければならない。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_current_limit_exceeded", "operator": "==", "unit": "1", "value": false}

この要求は、元の複合的な駆動要求を構成する一項目である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-CURRENT.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。
- R-DRIVE-CURRENT.TBR.2: バス回路の定格を定義する。バス電流は各モーターの巻線電流を示さない。

## R-DRIVE-SPEED: ホイールの回転速度限界

`R-DRIVE-SPEED@requirements-review-20261115-3` · requirement · subsystem · not_run

各リアクションホイールの回転速度の大きさは、その組立体の承認済みの限界以下でなければならない。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "wheel_speed_limit_exceeded", "operator": "==", "unit": "1", "value": false}

この要求は、元の複合的な駆動要求を構成する一項目である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.generate-torque

Verification method: test

Open items / 未解決事項:
- R-DRIVE-SPEED.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-TEMP: 部品の温度限界

`R-DRIVE-TEMP@requirements-review-20261115-3` · requirement · subsystem · not_run

各モーターとドライバの温度は、それぞれの承認済みの最小値と最大値の間でなければならない。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "component_temperature_limit_exceeded", "operator": "==", "unit": "1", "value": false}

この要求は、元の複合的な駆動要求を構成する一項目である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-TEMP.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-TORQUE: モーターのトルク限界

`R-DRIVE-TORQUE@requirements-review-20261115-3` · requirement · subsystem · not_run

各モーターのトルクは、測定した各回転速度における承認済みの最小値と最大値の間でなければならない。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "motor_torque_envelope_exceeded", "operator": "==", "unit": "1", "value": false}

この要求は、元の複合的な駆動要求を構成する一項目である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.generate-torque

Verification method: test

Open items / 未解決事項:
- R-DRIVE-TORQUE.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-DRIVE-VOLTAGE: バス電圧の限界

`R-DRIVE-VOLTAGE@requirements-review-20261115-3` · requirement · subsystem · not_run

駆動系は、バス電圧を各接続部品の承認済みの最小値と最大値の間に保たなければならない。

Acceptance / 合否基準: {"domain": "hardware", "limits_status": "unresolved", "metric": "bus_voltage_limit_exceeded", "operator": "==", "unit": "1", "value": false}

この要求は、元の複合的な駆動要求を構成する一項目である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.manage-power

Verification method: test

Open items / 未解決事項:
- R-DRIVE-VOLTAGE.TBR.1: 合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。

## R-HOLD: 手動解放後の保持

`R-HOLD@requirements-review-20261115-3` · requirement · operational · not_run

手動で設置して解放した後、Cubeは外部支持なしで頂点姿勢を10 s以上保持しなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "unsupported_vertex_hold_duration", "operator": ">=", "unit": "s", "value": 10, "limit_ref": {"id": "O-HOLD-INTERVAL", "revision": "requirements-review-20261115-3"}}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。

初回試作は手動設置から開始する。自動起立はこの草案の対象外である。

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-HOLD.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-MODEL: モデルの独立比較

`R-MODEL@requirements-review-20261115-3` · requirement · verification_platform · not_run

検証基盤は、対応する試験条件で、モデルの結果と独立した実測値を比較しなければならない。

Acceptance / 合否基準: {"domain": "hardware_model_comparison", "metric": "model_error", "operator": "<=", "unit": "defined_per_quantity", "value": null}

CPUとGPUの整合は数値的な挙動を確認する。モデル誤差の評価には実測値が必要である。

Derived from: R-TILT, R-RMS

Allocation: cube.function.measure-motion, cube.function.evaluate-trace

Verification method: analysis

Open items / 未解決事項:
- R-MODEL.TBR.1: 合否判定の前に、比較する量、単位、誤差限界、独立した実測データを定義する。

## R-REPEAT: 保持試験の反復

`R-REPEAT@requirements-review-20261115-3` · requirement · operational · not_run

固定した試験条件で、Cubeは10回の試行のうち9回以上、保持試験に合格しなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "successful_hold_trials", "operator": ">=", "sample_count": 10, "unit": "trials/10", "value": 9}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。

反復試行により、定めた試験条件での再現性を確認する。

Derived from: R-HOLD

Allocation: cube.function.control-balance, cube.function.evaluate-trace

Verification method: test

Open items / 未解決事項:
- R-REPEAT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。
- R-REPEAT.TBR.2: 試験前に試行順序、リセット方法、保持試験の合格規則全体を定義する。

## R-RMS: 傾斜角のRMS

`R-RMS@requirements-review-20261115-3` · requirement · system · not_run

保持区間中、Cubeの傾斜角のRMSは2 deg以下でなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "tilt_angle_rms", "operator": "<=", "unit": "deg", "value": 2}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Derived from: M-VERTEX

Allocation: cube.function.control-balance

Verification method: test

Open items / 未解決事項:
- R-RMS.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-SYNC: 動画とMCUの時刻の対応

`R-SYNC@requirements-review-20261115-3` · requirement · verification_platform · not_run

検証基盤は、動画とMCUのタイムスタンプ間の時刻関係を、0.005 s以下の時刻不確かさで算出しなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "video_mcu_time_uncertainty", "operator": "<=", "unit": "s", "value": 0.005}

独立した計測と制御器のログを比較するには、時刻の対応を把握する必要がある。

Derived from: R-TILT, R-RMS

Allocation: cube.function.capture-synchronize

Verification method: test

Open items / 未解決事項:
- R-SYNC.TBR.1: 時刻不確かさと校正方法を定義する。60 frame/sの動画だけでは0.005 sを示せない。

## R-TILT: 最大傾斜角

`R-TILT@requirements-review-20261115-3` · requirement · system · not_run

保持区間中、Cubeは傾斜角を5 deg以下に保たなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "peak_tilt_angle", "operator": "<=", "unit": "deg", "value": 5}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。

この限界値は実機の保持試験中におけるCubeの性能を表す。

Derived from: M-VERTEX

Allocation: cube.function.control-balance, cube.function.maintain-contact

Verification method: test

Open items / 未解決事項:
- R-TILT.TBR.1: 床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。

## R-TRACE: 実行の厳密な版参照

`R-TRACE@requirements-review-20261115-3` · requirement · verification_platform · not_run

検証基盤は、各実行について、要求、KDP、設計、条件、結果の厳密な版を特定しなければならない。

Acceptance / 合否基準: {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "unit": "count", "value": 0}

厳密な参照により変更と証拠の適用範囲が分かる。

Derived from: R-MODEL, R-REPEAT

Allocation: cube.function.manage-configuration

Verification method: inspection

## R-VISION: 独立した姿勢計測

`R-VISION@requirements-review-20261115-3` · requirement · verification_platform · not_run

独立した姿勢計測系の角度の標準不確かさは、0.5 deg以下でなければならない。

Acceptance / 合否基準: {"domain": "hardware", "metric": "attitude_standard_uncertainty", "operator": "<=", "unit": "deg", "value": 0.5}

独立した計測により、Cubeが使用する姿勢推定値を確認する。

Derived from: R-TILT, R-RMS

Allocation: cube.function.measure-motion

Verification method: test

Open items / 未解決事項:
- R-VISION.TBR.1: 姿勢成分、校正方法、不確かさの計算方法を定義する。この草案では標準不確かさを用いる。

## R-YAW: ヨー角速度の監視

`R-YAW@requirements-review-20261115-3` · requirement · subsystem · not_run

保持区間中、制御系はヨー角速度のRMSを監視しなければならない。

Acceptance / 合否基準: {"metric": "yaw_rate_rms_recorded", "operator": "==", "target_only": {"unit": "deg/s", "value": 5}, "unit": "1", "value": true}

Conditions / 条件:
- 手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。
- yawは保持開始時の支持頂点を通る鉛直軸周りとする。機体z軸周りの回転とは区別する。

原文は監視を求めている。固定したヨー方位は要求していない。

Derived from: cube.req.gnc

Allocation: cube.function.estimate-attitude

Verification method: test

Open items / 未解決事項:
- R-YAW.TBR.1: 5 deg/sを限界値にするか決定する。サンプリング周波数とRMSの計算方法を定義する。

## cube.req.gnc: 制御要求集合

`cube.req.gnc@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.system

## cube.req.mechanical: 機械要求集合

`cube.req.mechanical@requirements-review-20261115-3` · requirement_group · subsystem · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.system

## cube.req.operation: 運用要求集合

`cube.req.operation@requirements-review-20261115-3` · requirement_group · operational · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.system

## cube.req.system: システム要求集合

`cube.req.system@requirements-review-20261115-3` · requirement_group · system · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: M-VERTEX

## cube.req.verification: 検証基盤の要求集合

`cube.req.verification@requirements-review-20261115-3` · requirement_group · verification_platform · not_run

Acceptance / 合否基準: {"applicability": "not_applicable", "reason": "Organizational container"}

このノードは要求をまとめる。独立した試験義務ではない。

Derived from: cube.req.system
