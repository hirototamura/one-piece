"""Append reviewed language and trace drafts; never rewrite an existing revision.

Run from the repository root. This file is an authoring/migration input; immutable
Store records, rather than this file or a generated document, are the live SSOT.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

from onepiece.model import digest, make_record, ref
from onepiece.store import Store

ROOT = Path(__file__).resolve().parent
REVISION = "standards-draft-20261011-1"
CREATED_AT = "2026-10-11T05:21:44+00:00"
PROJECT = "balancing-cube"
ACTOR = {"type": "agent", "id": "standards-language-migration"}
SHALL_REVISION = "standards-draft-20261011-2"
SHALL_CREATED_AT = "2026-10-11T05:48:54+00:00"
SHALL_ACTOR = {"type": "agent", "id": "standards-priority-correction"}


def bilingual(en, ja):
    return {"en": en, "ja": ja}


def requirement(name, ja_name, statement, ja_statement, owner, parent, criterion,
                ja_criterion, method, rationale, ja_rationale, unresolved=(),
                conditions=(), parameters=(), level="subsystem"):
    return dict(name=name, ja_name=ja_name, statement=statement,
                ja_statement=ja_statement, owner=owner, parent=parent,
                criterion=criterion, ja_criterion=ja_criterion, method=method,
                rationale=rationale, ja_rationale=ja_rationale,
                unresolved=list(unresolved), conditions=list(conditions),
                parameters=list(parameters), level=level)


HOLD_CONDITION = bilingual(
    "Use the first 30 s after manual release as the hold interval.",
    "手動で解放した時点から最初の30 sを保持区間とする。")
HOLD_OPEN = bilingual(
    "Define the floor, initial attitude, release method, sample rate and measurement uncertainty in the hardware test procedure.",
    "床面、初期姿勢、解放方法、サンプリング周波数、測定不確かさを実機試験手順で定義する。")
RATING_OPEN = bilingual(
    "Identify the component revision, rated limits, test conditions and measurement uncertainty before a pass decision.",
    "合否判定の前に部品の版、定格限界、試験条件、測定不確かさを特定する。")


def definitions():
    """English obligations first; Japanese strings translate those obligations."""
    r = {}
    r["M-VERTEX"] = requirement(
        "Vertex hold mission", "頂点保持のミッション",
        "The Cube must hold its vertex position with 3 reaction wheels in the physical test environment.",
        "Cubeは、実機試験環境で3個のリアクションホイールを用いて頂点姿勢を保持しなければならない。",
        "cube.system", None,
        {"metric": "vertex_hold_demonstrated", "operator": "==", "value": True, "unit": "1", "domain": "hardware"},
        "実機試験で頂点姿勢の保持を示す。", "test",
        "This mission requires a physical demonstration of the Cube concept.",
        "このミッションではCubeの構想を実機で示す必要がある。",
        [HOLD_OPEN], level="mission")
    r["C-JAPAN"] = requirement(
        "Component supply to Japan", "日本への部品供給",
        "The Cube must use components that suppliers can supply to Japan.",
        "Cubeは、供給元が日本へ供給できる部品を使用しなければならない。",
        "cube.mechanical", "cube.req.mechanical",
        {"metric": "components_available_for_supply_to_japan", "operator": "==", "value": "all_purchased_components", "unit": "1"},
        "購入するすべての部品について、日本への供給元を確認する。", "inspection",
        "The user needs to obtain parts in Japan.", "ユーザーは日本で部品を入手する必要がある。",
        [bilingual("Define acceptable lead time and supply cost. The source word 'easy' has no numerical limit.",
                   "許容する納期と供給費用を定義する。原文の「容易」には数値限界がない。")])
    r["C-PRINT"] = requirement(
        "Housing manufacture", "筐体の製作",
        "The Cube housing must be a part that the specified 3D printer can make.",
        "Cubeの筐体は、指定された3Dプリンタで製作できる部品でなければならない。",
        "cube.mechanical", "cube.req.mechanical",
        {"metric": "housing_manufacturable", "operator": "==", "value": True, "unit": "1", "requirement_ref": {"id": "C-FIT-PRINT", "revision": REVISION}},
        "指定された3Dプリンタで筐体を製作できることを確認する。", "demonstration",
        "The user intends to use a friend's 3D printer.", "ユーザーは友人の3Dプリンタを使用する意図を持つ。",
        [bilingual("Identify the specified printer, material and print settings.", "指定するプリンタ、材料、造形条件を特定する。")],
        parameters=["D-CORNER-R", "I-PRINT-MATERIAL"])
    r["C-BUDGET"] = requirement(
        "First prototype cost", "初回試作の費用",
        "The cost of the first Cube prototype must be no more than the approved budget.",
        "Cubeの初回試作の費用は、承認された予算以下でなければならない。",
        "cube.mechanical", "cube.req.mechanical",
        {"metric": "prototype_cost", "operator": "<=", "limit_ref": {"id": "D-BUDGET", "revision": REVISION}, "unit": "JPY"},
        "初回試作の費用を、D-BUDGETで承認した金額以下とする。", "analysis",
        "The prototype needs an explicit cost limit.", "試作には明示的な費用上限が必要である。",
        [bilingual("Set the budget and cost scope. D-BUDGET has no value.", "予算と費用の範囲を設定する。D-BUDGETの値は未設定である。")],
        parameters=["D-BUDGET"])
    r["R-HOLD"] = requirement(
        "Hold after manual release", "手動解放後の保持",
        "After manual placement and release, the Cube must hold its vertex position for at least 30 s without external support.",
        "手動で設置して解放した後、Cubeは外部からの支持なしで頂点姿勢を30 s以上保持しなければならない。",
        "cube.system", "cube.req.operation",
        {"metric": "unsupported_vertex_hold_duration", "operator": ">=", "value": 30, "unit": "s", "domain": "hardware"},
        "実機で外部支持のない頂点保持時間を30 s以上とする。", "test",
        "The first prototype starts from manual placement. Automatic stand-up is outside this draft scope.",
        "初回試作は手動設置から開始する。自動起立はこの草案の対象外である。",
        [HOLD_OPEN], [HOLD_CONDITION], ["D-SIDE", "I-PEAK-TORQUE", "I-DELAY"], "operational")
    for id, name, ja_name, statement, ja_statement, metric, limit, unit, params in [
        ("R-TILT", "Maximum tilt angle", "最大傾斜角",
         "During the hold interval, the Cube must keep its tilt angle no more than 5 deg.",
         "保持区間中、Cubeは傾斜角を5 deg以下に保たなければならない。", "peak_tilt_angle", 5, "deg", []),
        ("R-RMS", "Tilt angle RMS", "傾斜角のRMS",
         "During the hold interval, the Cube must have a tilt angle RMS no more than 2 deg.",
         "保持区間中、Cubeの傾斜角のRMSは2 deg以下でなければならない。", "tilt_angle_rms", 2, "deg", []),
        ("R-DRIFT", "Contact point movement", "接地点の移動",
         "During the hold interval, the Cube contact point must move no more than 2 mm from its initial position.",
         "保持区間中、Cubeの接地点は初期位置から2 mmを超えて移動してはならない。", "peak_contact_point_displacement", 2, "mm", ["D-CORNER-R", "I-MU"]),
    ]:
        r[id] = requirement(name, ja_name, statement, ja_statement, "cube.system", "cube.req.system",
            {"metric": metric, "operator": "<=", "value": limit, "unit": unit, "domain": "hardware"},
            f"保持区間全体について{ja_name}を{limit} {unit}以下とする。", "test",
            "This limit describes the Cube performance during the hardware hold test.",
            "この限界値は実機の保持試験中におけるCubeの性能を表す。",
            [HOLD_OPEN], [HOLD_CONDITION], params, "system")
    r["R-REPEAT"] = requirement(
        "Repeated hold tests", "保持試験の反復",
        "Under fixed test conditions, the Cube must pass the hold test in at least 9 of 10 trials.",
        "固定した試験条件で、Cubeは10回の試行のうち9回以上、保持試験に合格しなければならない。",
        "cube.system", "cube.req.operation",
        {"metric": "successful_hold_trials", "operator": ">=", "value": 9, "sample_count": 10, "unit": "trials/10", "domain": "hardware"},
        "同じ実機試験条件で10回実施し、9回以上の保持試験成功を得る。", "test",
        "Repeated trials check repeatability for the stated test conditions.", "反復試行により、定めた試験条件での再現性を確認する。",
        [HOLD_OPEN, bilingual("Define trial order, resets and the complete hold-test pass rule before testing.",
                             "試験前に試行順序、リセット方法、保持試験の合格規則全体を定義する。")], level="operational")
    r["R-YAW"] = requirement(
        "Yaw rate monitoring", "ヨー角速度の監視",
        "During the hold interval, the control system must monitor the yaw rate RMS.",
        "保持区間中、制御系はヨー角速度のRMSを監視しなければならない。",
        "cube.gnc", "cube.req.gnc",
        {"metric": "yaw_rate_rms_recorded", "operator": "==", "value": True, "unit": "1", "target_only": {"value": 5, "unit": "deg/s"}},
        "ヨー角速度のRMSを記録する。5 deg/sは目標値であり、合否の閾値ではない。", "test",
        "The source asks for monitoring. It does not require a fixed yaw heading.",
        "原文は監視を求めている。固定したヨー方位は要求していない。",
        [bilingual("Decide whether 5 deg/s will become a limit. Define the sample rate and RMS calculation.",
                   "5 deg/sを限界値にするか決定する。サンプリング周波数とRMSの計算方法を定義する。")],
        [HOLD_CONDITION], ["I-TORSION"])
    r["R-VISION"] = requirement(
        "Independent attitude measurement", "独立した姿勢計測",
        "The independent attitude measurement system must have an angular standard uncertainty of no more than 0.5 deg.",
        "独立した姿勢計測系の角度の標準不確かさは、0.5 deg以下でなければならない。",
        "cube.verification", "cube.req.verification",
        {"metric": "attitude_standard_uncertainty", "operator": "<=", "value": 0.5, "unit": "deg", "domain": "hardware"},
        "独立した姿勢計測の角度の標準不確かさを0.5 deg以下とする。", "test",
        "An independent measurement checks the attitude estimate used by the Cube.",
        "独立した計測により、Cubeが使用する姿勢推定値を確認する。",
        [bilingual("Define the attitude components, calibration method and uncertainty calculation. This draft uses standard uncertainty.",
                   "姿勢成分、校正方法、不確かさの計算方法を定義する。この草案では標準不確かさを用いる。")],
        parameters=["I-CAMERA-U"], level="verification_platform")
    r["R-SYNC"] = requirement(
        "Video and MCU time relation", "動画とMCUの時刻の対応",
        "The verification platform must calculate the time relation between video and MCU timestamps with a time uncertainty no more than 0.005 s.",
        "検証基盤は、動画とMCUのタイムスタンプ間の時刻関係を、0.005 s以下の時刻不確かさで算出しなければならない。",
        "cube.verification", "cube.req.verification",
        {"metric": "video_mcu_time_uncertainty", "operator": "<=", "value": 0.005, "unit": "s", "domain": "hardware"},
        "動画とMCUの対応時刻の不確かさを0.005 s以下とする。", "test",
        "A known time relation is necessary to compare independent measurements and controller logs.",
        "独立した計測と制御器のログを比較するには、時刻の対応を把握する必要がある。",
        [bilingual("Define the time uncertainty and calibration method. A 60 frame/s video alone does not demonstrate 0.005 s.",
                   "時刻不確かさと校正方法を定義する。60 frame/sの動画だけでは0.005 sを示せない。")],
        parameters=["I-DELAY", "I-SYNC-U"], level="verification_platform")
    r["R-MODEL"] = requirement(
        "Independent model comparison", "モデルの独立比較",
        "The verification platform must compare model results with independent physical measurements under the same test conditions.",
        "検証基盤は、対応する試験条件で、モデルの結果と独立した実測値を比較しなければならない。",
        "cube.verification", "cube.req.verification",
        {"metric": "model_error", "operator": "<=", "value": None, "unit": "defined_per_quantity", "domain": "hardware_model_comparison"},
        "対応する試験条件でモデル誤差を算出する。許容値と各量の単位は未定である。", "analysis",
        "CPU and GPU agreement checks numerical behavior. Physical measurements are necessary to assess model error.",
        "CPUとGPUの整合は数値的な挙動を確認する。モデル誤差の評価には実測値が必要である。",
        [bilingual("Define comparison quantities, units, error limits and independent physical data before a pass decision.",
                   "合否判定の前に、比較する量、単位、誤差限界、独立した実測データを定義する。")],
        level="verification_platform")
    r["R-TRACE"] = requirement(
        "Exact run references", "実行の厳密な版参照",
        "The verification platform must identify the exact revisions of requirements, KDPs, designs, conditions, and results for each run.",
        "検証基盤は、各実行について、要求、KDP、設計、条件、結果の厳密な版を特定しなければならない。",
        "cube.verification", "cube.req.verification",
        {"metric": "missing_or_ambiguous_revision_references", "operator": "==", "value": 0, "unit": "count"},
        "各実行の要求、KDP、設計、条件、結果の参照に欠落と曖昧な版を残さない。", "inspection",
        "Exact references make changes and evidence applicability visible.", "厳密な参照により変更と証拠の適用範囲が分かる。",
        parameters=["F-CONTROL-PERIOD"], level="verification_platform")
    for id, name, ja_name, statement, ja_statement, metric, parameter_ids in [
        ("R-DRIVE-TORQUE", "Motor torque limits", "モーターのトルク限界",
         "At each measured speed, each motor must have torque between its approved minimum and maximum limits.",
         "各モーターのトルクは、測定した各回転速度における承認済みの最小値と最大値の間でなければならない。",
         "motor_torque_envelope_exceeded", ["I-PEAK-TORQUE", "I-TORQUE-THRESHOLD", "I-NOLOAD-SPEED", "I-TORQUE-KT"]),
        ("R-DRIVE-SPEED", "Wheel speed limits", "ホイールの回転速度限界",
         "Each reaction wheel must have a speed magnitude no more than the approved limit for its assembly.",
         "各リアクションホイールの回転速度の大きさは、その組立体の承認済みの限界以下でなければならない。",
         "wheel_speed_limit_exceeded", ["D-SPEED-LIMIT", "D-WHEEL-RADIUS"]),
        ("R-DRIVE-TEMP", "Component temperature limits", "部品の温度限界",
         "Each motor and driver must have a temperature between its approved minimum and maximum limits.",
         "各モーターとドライバの温度は、それぞれの承認済みの最小値と最大値の間でなければならない。",
         "component_temperature_limit_exceeded", ["I-DRIVE-TEMP"]),
        ("R-DRIVE-VOLTAGE", "Bus voltage limits", "バス電圧の限界",
         "The drive system must keep the bus voltage between the approved minimum and maximum limits of each connected component.",
         "駆動系は、バス電圧を各接続部品の承認済みの最小値と最大値の間に保たなければならない。",
         "bus_voltage_limit_exceeded", ["I-BUS-V"]),
        ("R-DRIVE-CURRENT", "Bus current limits", "バス電流の限界",
         "The drive system must keep the bus current between the approved minimum and maximum limits of the bus circuit.",
         "駆動系は、バス電流をバス回路の承認済みの最小値と最大値の間に保たなければならない。",
         "bus_current_limit_exceeded", ["I-BUS-I"]),
    ]:
        r[id] = requirement(name, ja_name, statement, ja_statement, "cube.actuation", "R-DRIVE",
            {"metric": metric, "operator": "==", "value": False, "unit": "1", "limits_status": "unresolved", "domain": "hardware"},
            "対象部品の承認済みの限界を超えない。限界値と実測値は未確定である。", "test",
            "This obligation is one part of the original compound drive requirement.",
            "この要求は、元の複合的な駆動要求を構成する一項目である。",
            [RATING_OPEN], parameters=parameter_ids)
    for id, name, ja_name, statement, ja_statement, metric, params in [
        ("C-FIT-PRINT", "Printed part dimensions", "造形部品の寸法",
         "Each printed housing part must have dimensions no more than the specified build limits of the 3D printer.",
         "筐体の各造形部品の寸法は、3Dプリンタの指定された造形限界以下でなければならない。",
         "printed_parts_inside_build_volume", ["I-PRINT-X", "I-PRINT-Y", "I-PRINT-Z", "D-SIDE"]),
        ("C-FIT-MATERIAL", "Print material selection", "造形材料の選定",
         "The Cube housing must use a print material from the approved material list for the specified 3D printer.",
         "Cubeの筐体は、指定された3Dプリンタの承認済み材料一覧にある造形材料を使用しなければならない。",
         "material_on_printer_material_list", ["I-PRINT-MATERIAL"]),
        ("C-FIT-INSTALL", "Installed component dimensions", "搭載部品の寸法",
         "Each installed component must have dimensions no more than the specified dimensions of its space in the Cube housing.",
         "各搭載部品の寸法は、Cube筐体内の搭載空間に指定された寸法以下でなければならない。",
         "installed_components_inside_assigned_space", ["D-SIDE", "D-WHEEL-RADIUS"]),
    ]:
        r[id] = requirement(name, ja_name, statement, ja_statement, "cube.mechanical", "C-FIT",
            {"metric": metric, "operator": "==", "value": True, "unit": "1", "limits_status": "unresolved"},
            "指定する造形範囲、材料一覧、搭載空間の該当条件を満たす。", "inspection",
            "This obligation is one part of the original compound manufacturing requirement.",
            "この要求は、元の複合的な製作要求を構成する一項目である。",
            [bilingual("Identify printer limits, the material list, component dimensions and required movement clearance.",
                       "プリンタの限界、材料一覧、部品寸法、必要な動作間隙を特定する。")], parameters=params)
    r["R-DRIVE-CURRENT"]["unresolved"].append(bilingual(
        "Define the bus circuit ratings. Bus current does not show each motor winding current.",
        "バス回路の定格を定義する。バス電流は各モーターの巻線電流を示さない。"))
    return r


GROUPS = {
    "cube.req.system": ("System requirement set", "システム要求集合", "cube.system", "M-VERTEX", "system"),
    "cube.req.operation": ("Operational requirement set", "運用要求集合", "cube.system", "cube.req.system", "operational"),
    "cube.req.mechanical": ("Mechanical requirement set", "機械要求集合", "cube.mechanical", "cube.req.system", "subsystem"),
    "cube.req.gnc": ("Control requirement set", "制御要求集合", "cube.gnc", "cube.req.system", "subsystem"),
    "cube.req.verification": ("Verification platform requirement set", "検証基盤の要求集合", "cube.verification", "cube.req.system", "verification_platform"),
    "C-FIT": ("Manufacturing and installation requirement set", "製作と搭載の要求集合", "cube.mechanical", "cube.req.mechanical", "subsystem"),
    "R-DRIVE": ("Drive limit requirement set", "駆動限界の要求集合", "cube.actuation", "cube.req.system", "subsystem"),
}


def build_updates(history):
    # Repeated delivery always derives from the same source, not from this draft.
    by_ref = {(r["id"], r["revision"]): r for r in history}
    source_snapshot = by_ref[("cube.simulation.snapshot", "fixed-dt-mvp-2")]
    requirement_sources = {v["id"]: by_ref[(v["id"], v["revision"])] for v in source_snapshot["data"]["context_refs"]["requirements"]}
    parameter_sources = {v["id"]: by_ref[(v["id"], v["revision"])] for v in source_snapshot["data"]["context_refs"]["kdps"]}
    products = {r["id"]: r for r in history if r["kind"] == "product" and r["revision"] == "legacy-20261009"}
    catalog = json.loads((ROOT / "standards/kdp_language.json").read_text())
    terms = json.loads((ROOT / "standards/technical_terms.json").read_text())
    updates = []

    def add(id, kind, data, owner="cube.system", links=()):
        record = make_record(project_id=PROJECT, id=id, revision=REVISION, kind=kind,
            product_node=owner, created_at=CREATED_AT, actor=ACTOR,
            data=data, links=list(links))
        updates.append(record)
        return record

    def edge(type, id, revision=REVISION):
        return {"type": type, "target": ref(id, revision)}

    source_digests = {r["id"]: {**ref(r), "sha256": digest(r)} for r in [*requirement_sources.values(), *parameter_sources.values(), *products.values(), source_snapshot]}
    profile = add("cube.language.profile", "specification", {
        "name": "English requirement writing profile", "source_language": "en",
        "translation_languages": ["ja"], "normative_modal": "must",
        "requirement_standard": {"name": "ISO/IEC/IEEE 29148:2018", "url": "https://www.iso.org/standard/72089.html", "normative_text_available": False, "clause_audit": "not_performed"},
        "writing_standard": {"name": "ASD-STE100", "issue": "9", "publication_date": "2025-01-15", "url": "https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf", "sha256": "d1f4ea9e7cd6e46b47aa9057209f99e78c0e9cfc4e27a5b07895b05c1a166431", "rules_reviewed": ["1.5-1.11", "3.6", "4.1", "6.1", "6.3"], "complete_dictionary_audit": "not_performed"},
        "technical_terms": terms,
        "review_scope": "Short active sentences, one obligation per statement, defined technical names, explicit units and the approved modal must. This is not a full standards conformity certificate.",
        "translations": {"ja": {"name": "英語要求の執筆プロファイル", "review_scope": "短い能動文、文ごとに一つの義務、定義した技術名、明示的な単位、承認語mustを適用する。規格への完全な適合を認証するものではない。"}},
    })
    for id, source in {**products, **parameter_sources}.items():
        data = copy.deepcopy(source["data"])
        data.update(copy.deepcopy(catalog[id]))
        data.update(source_record=source_digests[id], source_language="en", supersedes=ref(source), language_profile_ref=ref(profile))
        owner = source["product_node"]
        if id in {"F-CONTROL-PERIOD"}: owner = "cube.gnc"
        if id in {"F-SIM-DT", "I-CAMERA-U", "I-SYNC-U"}: owner = "cube.verification"
        if id in {"I-BUS-I", "I-BUS-V", "I-DRIVE-TEMP", "I-TORQUE-KT"}: owner = "cube.actuation"
        if source["kind"] == "product":
            data["parent_product_ref"] = ref("cube.system", REVISION) if id != "cube.system" else None
            links = []
        else:
            links = [edge("allocate", owner)]
            data["requirement_refs"] = [ref(rid, REVISION) for rid in data.get("requirements", [])]
        add(id, source["kind"], data, owner, links)
    defs = definitions()
    for id in [*GROUPS, *defs]:
        source = requirement_sources.get(id)
        definition = defs.get(id)
        if definition:
            name, ja_name, owner, parent, level = (definition[k] for k in ("name", "ja_name", "owner", "parent", "level"))
        else:
            name, ja_name, owner, parent, level = GROUPS[id]
        # Source fields stay inspectable by exact reference and in original history.
        data = {"id": id, "name": name, "source_language": "en", "level": level,
                "status": "draft", "approval_state": "pending_human_review",
                "source_status": source["data"].get("status") if source else "draft",
                "status_semantics": "draft wording and trace proposal; source_status describes the unchanged source statement",
                "original_record": False, "physical_verified": None,
                "verification_status": "not_run", "language_profile_ref": ref(profile),
                "source": "Versioned English rewrite and Japanese translation of the source requirement.",
                "source_record": source_digests[id] if source else source_digests[definition["parent"]],
                "unit": source["data"].get("unit", "1") if source else "1",
                "value": source["data"].get("value") if source else None,
                "parent_ref": ref(parent, REVISION) if parent else None,
                "translations": {"ja": {"name": ja_name}}}
        if source: data["supersedes"] = ref(source)
        links = [edge("allocate", owner)] + ([edge("derive", parent)] if parent else [])
        if definition:
            translated = data["translations"]["ja"]
            data.update(record_role="requirement", obligation="requirement", statement=definition["statement"],
                        rationale=definition["rationale"], conditions=[x["en"] for x in definition["conditions"]],
                        acceptance_criteria=definition["criterion"], verification_method=definition["method"],
                        verification_case_ref=ref("cube.verify." + id, REVISION),
                        hardware_verification_required=definition["criterion"].get("domain") in {"hardware", "hardware_model_comparison"},
                        unresolved_items=[{"id": id + ".TBR." + str(i+1), "description": x["en"], "owner": owner} for i, x in enumerate(definition["unresolved"])])
            if id == "R-TRACE": data["hardware_verification_required"] = False
            translated.update(statement=definition["ja_statement"], rationale=definition["ja_rationale"],
                              conditions=[x["ja"] for x in definition["conditions"]],
                              acceptance_criteria=definition["ja_criterion"],
                              unresolved_items=[{"id": id + ".TBR." + str(i+1), "description": x["ja"], "owner": owner} for i, x in enumerate(definition["unresolved"])])
            parameters = definition["parameters"]
            if id == "M-VERTEX" or id == "R-MODEL":
                parameters = [e["target"]["id"] for e in source["links"] if e["type"] == "constrain"]
            links += [edge("constrain", p) for p in parameters]
        else:
            data.update(record_role="requirement_group", statement=None,
                rationale="This node groups requirements. It is not a separate test obligation.",
                acceptance_criteria={"applicability": "not_applicable", "reason": "Organizational container"},
                hardware_verification_required=False,
                member_refs=[ref(child, REVISION) for child in [*GROUPS, *defs] if (GROUPS.get(child, (None,)*5)[3] if child in GROUPS else defs[child]["parent"]) == id])
            data["translations"]["ja"].update(statement=None, rationale="このノードは要求をまとめる。独立した試験義務ではない。")
        add(id, "requirement", data, owner, links)
    new_requirements = [r for r in updates if r["kind"] == "requirement"]
    for req in new_requirements:
        d = req["data"]
        if d["record_role"] != "requirement": continue
        add("cube.verify." + req["id"], "verification_case", {
            "name": "Verification plan for " + req["id"], "source_language": "en",
            "status": "planned", "execution_status": "not_run", "requirement_refs": [ref(req)],
            "method": d["verification_method"], "conditions": d["conditions"],
            "acceptance_criteria": d["acceptance_criteria"], "unresolved_items": d["unresolved_items"],
            "evidence_refs": [], "physical_verified": None,
            "translations": {"ja": {"name": req["id"] + "の検証計画", "conditions": d["translations"]["ja"]["conditions"],
                                      "acceptance_criteria": d["translations"]["ja"]["acceptance_criteria"],
                                      "unresolved_items": d["translations"]["ja"]["unresolved_items"]}},
        }, "cube.verification")
    snapshot_data = copy.deepcopy(source_snapshot["data"])
    snapshot_data.update(supersedes=ref(source_snapshot),
        source_snapshot_ref=ref(source_snapshot), requirements_approval_state="pending_human_review",
        language_profile_ref=ref(profile),
        trace_correction_note="English requirement drafts, aligned Japanese translations and corrected allocations. Numerical model, controller, evaluation contract and past evidence are unchanged.")
    snapshot_data["context_refs"]["requirements"] = [ref(r) for r in new_requirements]
    snapshot_data["context_refs"]["kdps"] = [ref(v["id"], REVISION) for v in source_snapshot["data"]["context_refs"]["kdps"]]
    snapshot_data["kdps"]["entries"] = [next(r["data"] for r in updates if r["id"] == v["id"]) for v in source_snapshot["data"]["context_refs"]["kdps"]]
    snapshot_data["kdps"]["revision"] = REVISION
    snapshot_data["mission"]["requirements"] = [r["data"] for r in new_requirements]
    snapshot_data["mission"]["revision"] = REVISION
    snapshot_data["mission"]["source_revision"] = source_snapshot["data"]["mission"]["revision"]
    snapshot_data["mission"]["source_language"] = "en"
    add("cube.simulation.snapshot", "simulation_snapshot", snapshot_data,
        links=[edge("derive", source_snapshot["id"], source_snapshot["revision"])])
    add("cube.system-model.active", "system_model", {
        "scope": "Current requirement draft and model projection; not an approved baseline.",
        "simulation_snapshot_ref": ref("cube.simulation.snapshot", REVISION),
        "source_snapshot_ref": ref(source_snapshot), "language_profile_ref": ref(profile),
        "approval_state": "pending_human_review", "source_record_digests": list(source_digests.values()),
        "api_profile": "onepiece-annotation-graph-1", "api_standard": "OMG Systems Modeling API and Services 1.0",
        "graph_note": "Requirement groups are organizational nodes. Dependencies carry the five One-Piece trace names; they are not native SysML requirement metaclasses.",
        "translations": {"ja": {"scope": "現在の要求草案とモデルの表示用構成。承認済みベースラインではない。", "graph_note": "要求グループは整理用ノードである。DependencyはOne-Pieceの5種類のトレース名を保持する。SysML固有の要求メタクラスではない。"}},
    })
    return updates


def build_shall_revision(history):
    """Append shall-worded requirement revisions without changing the prior draft."""
    by_ref = {(r["id"], r["revision"]): r for r in history}
    source_snapshot = by_ref[("cube.simulation.snapshot", REVISION)]
    source_parameters = [by_ref[(v["id"], v["revision"])]
                         for v in source_snapshot["data"]["context_refs"]["kdps"]]
    parameter_ids = {r["id"] for r in source_parameters}
    source_requirements = [by_ref[(v["id"], v["revision"])]
                           for v in source_snapshot["data"]["context_refs"]["requirements"]]
    requirement_ids = {r["id"] for r in source_requirements}
    source_cases = [by_ref[("cube.verify." + r["id"], REVISION)]
                    for r in source_requirements if r["data"]["record_role"] == "requirement"]
    source_profile = by_ref[("cube.language.profile", REVISION)]
    source_model = by_ref[("cube.system-model.active", REVISION)]

    def rewrite_english(value):
        if isinstance(value, str):
            return re.sub(r"\bmust\b", "shall", value, flags=re.IGNORECASE)
        if isinstance(value, list):
            return [rewrite_english(v) for v in value]
        if isinstance(value, dict):
            return {k: (v if k == "translations" else rewrite_english(v))
                    for k, v in value.items()}
        return value

    def revised(source, data, links=None):
        record = copy.deepcopy(source)
        record.update(revision=SHALL_REVISION, created_at=SHALL_CREATED_AT,
                      actor=copy.deepcopy(SHALL_ACTOR), data=data)
        if links is not None:
            record["links"] = links
        return record

    def retarget_refs(value, ids):
        if isinstance(value, dict):
            if set(value) == {"id", "revision"} and value["id"] in ids and value["revision"] == REVISION:
                return {"id": value["id"], "revision": SHALL_REVISION}
            return {k: retarget_refs(v, ids) for k, v in value.items()}
        if isinstance(value, list):
            return [retarget_refs(v, ids) for v in value]
        return value

    updates = []
    revised_parameters = []
    for source in source_parameters:
        data = copy.deepcopy(source["data"])
        data["supersedes"] = ref(source)
        data["language_profile_ref"] = ref("cube.language.profile", SHALL_REVISION)
        data["requirement_refs"] = retarget_refs(data.get("requirement_refs", []), requirement_ids)
        links = copy.deepcopy(source["links"])
        record = revised(source, data, links)
        updates.append(record)
        revised_parameters.append(record)

    revised_requirements = []
    for source in source_requirements:
        data = rewrite_english(copy.deepcopy(source["data"]))
        data["supersedes"] = ref(source)
        data["language_profile_ref"] = ref("cube.language.profile", SHALL_REVISION)
        if data.get("record_role") == "requirement":
            data["normative_modal"] = "shall"
        else:
            data.pop("normative_modal", None)
        data["acceptance_criteria"] = retarget_refs(data["acceptance_criteria"], requirement_ids | parameter_ids)
        if (data.get("parent_ref") or {}).get("id") in requirement_ids:
            data["parent_ref"]["revision"] = SHALL_REVISION
        for member in data.get("member_refs", []):
            if member["id"] in requirement_ids:
                member["revision"] = SHALL_REVISION
        case_ref = data.get("verification_case_ref")
        if case_ref:
            case_ref["revision"] = SHALL_REVISION
        links = copy.deepcopy(source["links"])
        for edge in links:
            if edge["type"] == "derive" and edge["target"]["id"] in requirement_ids:
                edge["target"]["revision"] = SHALL_REVISION
            elif edge["type"] == "constrain" and edge["target"]["id"] in parameter_ids:
                edge["target"]["revision"] = SHALL_REVISION
        record = revised(source, data, links)
        updates.append(record)
        revised_requirements.append(record)

    for source in source_cases:
        data = copy.deepcopy(source["data"])
        data["supersedes"] = ref(source)
        for requirement in data["requirement_refs"]:
            requirement["revision"] = SHALL_REVISION
        data["acceptance_criteria"] = retarget_refs(data["acceptance_criteria"], requirement_ids | parameter_ids)
        updates.append(revised(source, data))

    profile = copy.deepcopy(source_profile["data"])
    profile["normative_modal"] = "shall"
    profile["standards_precedence"] = [
        {"rank": 1, "name": "ISO/IEC/IEEE 29148:2018",
         "url": "https://www.iso.org/standard/72089.html",
         "role": "Primary requirements engineering standard; first source for requirements."},
        {"rank": 2, "name": "NASA systems engineering standards and requirements guidance",
         "url": "https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/",
         "role": "Secondary requirements and systems engineering source; use shall for requirements."},
        {"rank": 3, "name": "ASD-STE100 Issue 9",
         "url": "https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf",
         "role": "English writing rules where compatible with the higher-priority sources."},
    ]
    profile["modal_rule"] = {
        "token": "shall",
        "basis": "NASA Appendix C identifies shall as the requirement modal. The full ISO text was unavailable for clause review.",
        "conflict_note": "ASD-STE100 Issue 9 lists shall as unapproved and must as its alternative. The stated priority applies NASA shall usage and compatible STE rules; this does not claim complete STE compliance.",
    }
    profile["review_scope"] = (
        "Use shall for normative requirements under the declared ISO, NASA, then ASD-STE100 priority. "
        "Apply compatible STE sentence, voice, term and word-count rules. This is not a full standards conformity certificate."
    )
    ja_profile = profile.setdefault("translations", {}).setdefault("ja", {})
    ja_profile.update({
        "review_scope": "ISO、NASA、ASD-STE100の優先順位に従い、要求文にはshallを使う。上位の方針と両立するSTEの文、態、用語、語数の規則を適用する。完全な規格適合認証ではない。",
        "normative_modal": "shall",
        "standards_precedence": [
            "ISO/IEC/IEEE 29148:2018（要求工学の第一参照）",
            "NASAのシステムズエンジニアリング標準と要求記述ガイド（第二参照）",
            "ASD-STE100 Issue 9（上位の出典と両立する範囲で適用）",
        ],
        "modal_conflict_note": (
            "NASA Appendix Cはshallを要求の規範語とする。ASD-STE100 Issue 9の辞書はshallを非承認語、mustを代替語とする。"
            "指定された優先順位に従いshallを使用し、STEへの完全適合は主張しない。"
        ),
    })
    profile_record = revised(source_profile, profile)
    profile_record["data"]["supersedes"] = ref(source_profile)
    updates.append(profile_record)

    snapshot_data = copy.deepcopy(source_snapshot["data"])
    snapshot_data.update(
        supersedes=ref(source_snapshot), source_snapshot_ref=ref(source_snapshot),
        language_profile_ref=ref(profile_record),
        trace_correction_note=(
            "Shall-modal requirement revisions follow the declared ISO, NASA, then ASD-STE100 priority. "
            "Numerical model, controller, evaluation contract and past evidence are unchanged."
        ),
    )
    snapshot_data["context_refs"]["requirements"] = [ref(r) for r in revised_requirements]
    snapshot_data["context_refs"]["kdps"] = [ref(r) for r in revised_parameters]
    snapshot_data["kdps"]["entries"] = [r["data"] for r in revised_parameters]
    snapshot_data["kdps"]["revision"] = SHALL_REVISION
    for binding in snapshot_data.get("parameter_bindings", []):
        if (binding.get("parameter_ref") or {}).get("id") in parameter_ids:
            binding["parameter_ref"]["revision"] = SHALL_REVISION
    snapshot_data["mission"]["requirements"] = [r["data"] for r in revised_requirements]
    snapshot_data["mission"]["revision"] = SHALL_REVISION
    snapshot_data["mission"]["source_revision"] = source_snapshot["data"]["mission"]["revision"]
    snapshot_data["mission"]["source_language"] = "en"
    snapshot = revised(source_snapshot, snapshot_data, links=[
        {"type": "derive", "target": ref(source_snapshot)}
    ])
    updates.append(snapshot)

    active = copy.deepcopy(source_model["data"])
    active.update(
        supersedes=ref(source_model),
        simulation_snapshot_ref=ref(snapshot),
        source_snapshot_ref=ref(source_snapshot),
        language_profile_ref=ref(profile_record),
        standards_precedence_ref=ref(profile_record),
        scope="Current shall-modal requirement draft and model projection; not an approved baseline.",
        translations={"ja": {
            "scope": "現在のshall形式の要求草案とモデルの表示用構成。承認済みベースラインではない。",
            "graph_note": source_model["data"].get("translations", {}).get("ja", {}).get("graph_note", ""),
        }},
    )
    updates.append(revised(source_model, active))
    return updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=ROOT / "store")
    parser.add_argument("--write-docs", action="store_true", help="generate bilingual projections after import")
    args = parser.parse_args()
    store = Store(args.store)
    initial = store.import_records(build_updates(store.records(PROJECT)))
    corrected = store.import_records(build_shall_revision(store.records(PROJECT)))
    print(json.dumps({"initial_standards_draft": initial,
                      "shall_priority_revision": corrected}, indent=2))
    if args.write_docs:
        write_documents(store.records(PROJECT))


def write_documents(records):
    """Generate human text from the imported records; do not author a second SSOT."""
    active = max((r for r in records if r["id"] == "cube.system-model.active"),
                 key=lambda r: (r["created_at"], r["revision"]))
    snapshot_ref = active["data"]["simulation_snapshot_ref"]
    by_ref = {(r["id"], r["revision"]): r for r in records}
    snapshot = by_ref[(snapshot_ref["id"], snapshot_ref["revision"])]
    requirements = [by_ref[(v["id"], v["revision"])]
                    for v in snapshot["data"]["context_refs"]["requirements"]]
    profile_ref = active["data"]["language_profile_ref"]
    profile = by_ref[(profile_ref["id"], profile_ref["revision"])]["data"]
    modal = profile["normative_modal"]
    for language in ("en", "ja"):
        english = language == "en"
        lines = (["# Balancing Cube requirement drafts", "",
                  f"This view comes from canonical JSON at `{snapshot['revision']}`. Regenerate it with `python projects/balancing-cube/migrate_standards.py --write-docs`.", "",
                  "The English text is the source. The Japanese text is its translation. All revised statements are drafts that need human review.", "",
                  "Priority: ISO/IEC/IEEE 29148:2018 first; NASA systems engineering standards and requirements guidance second; ASD-STE100 Issue 9 third where compatible.",
                  f"Normative requirement modal: `{modal}`. NASA Appendix C identifies shall as the requirement modal. ASD-STE100 Issue 9 lists shall as unapproved and must as its alternative; the declared priority governs this choice.",
                  "Apply compatible ASD-STE100 rules for active voice, defined technical names and sentence length. The full ISO text was not available for a clause audit; a complete STE dictionary audit and standards certification have not been performed.", "",
                  "The 7 organizational containers are not separate test obligations. The 22 obligations include 8 atomic children of the original compound requirements.",
                  "Verification cases are plans only. There are no new hardware results. Historical numerical evidence retains its original revision targets.", "",
                  "See [writing standards](../engineering/standards.md), [system model](system_model.md) and [API scope](sysml_api.md).", ""]
                 if english else
                 ["# Balancing Cubeの要求草案", "",
                  f"この表示は`{snapshot['revision']}`の正本JSONから生成する。`python projects/balancing-cube/migrate_standards.py --write-docs`で再生成する。", "",
                  "英語が原文であり、日本語はその翻訳である。改訂したすべての要求文は、人間による確認が必要な草案である。", "",
                  "優先順位はISO/IEC/IEEE 29148:2018、NASAのシステムズエンジニアリング標準と要求記述ガイド、ASD-STE100 Issue 9の順である。",
                  "要求文の規範語はshallとする。NASA Appendix Cはshallを要求の規範語とする。ASD-STE100 Issue 9の辞書はshallを非承認語、mustを代替語とするが、ここでは指定された優先順位に従う。",
                  "能動態、定義した技術名、文の長さなど、上位の方針と両立するSTE規則を適用する。ISO規格の全文が得られず条項単位の審査は未実施である。STE辞書の全語審査と規格適合認証も未実施である。", "",
                  "7個の整理用コンテナは独立した試験義務ではない。22個の義務には、元の複合要求から分割した8個の子要求を含む。",
                  "検証ケースは計画のみである。新しい実機結果はない。過去の数値的証拠は、元の版への参照を維持する。", "",
                  "[執筆標準](../engineering/standards.md)、[システムモデル](system_model.md)、[APIの範囲](sysml_api.md)を参照する。", ""])
        for record in requirements:
            d = record["data"]
            text = d if english else d["translations"]["ja"]
            lines.extend([f"## {record['id']}: {text['name']}", "",
                f"`{record['id']}@{record['revision']}` · `{record['product_node']}` · `draft` · `not_run`", ""])
            if d["record_role"] == "requirement_group":
                lines.extend([text["rationale"], "", ", ".join(x["id"] for x in d["member_refs"]), ""])
                continue
            lines.extend([text["statement"], "", text["rationale"], ""])
            lines.extend(("Condition: " if english else "条件：") + v for v in text["conditions"])
            criterion = json.dumps(d["acceptance_criteria"], ensure_ascii=False, sort_keys=True) if english else text["acceptance_criteria"]
            lines.extend(["", ("Acceptance: " if english else "判定基準：") + criterion, "",
                          ("Verification method: " if english else "検証方法：") + d["verification_method"], "",
                          ("Source statement status: " if english else "元の要求文の状態：") + str(d["source_status"]), ""])
            for item in text["unresolved_items"]:
                lines.extend([f"- `{item['id']}`: {item['description']}", ""])
            source = d["source_record"]
            lines.extend([f"Source: `{source['id']}@{source['revision']}`; SHA-256 `{source['sha256']}`.", ""])
        destination = ROOT.parents[1] / "docs" / language / "balancing_cube_requirements.md"
        destination.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
