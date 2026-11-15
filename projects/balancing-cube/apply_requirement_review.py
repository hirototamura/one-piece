"""Apply the user's requirement review without changing historical numerical trials."""
from __future__ import annotations

import argparse
import copy
import json
import runpy
from collections import defaultdict
from pathlib import Path

from onepiece.model import digest, make_record, ref
from onepiece.store import Store

ROOT = Path(__file__).resolve().parent
SOURCE = "refined-20261115-1"
REVISION = "requirements-review-20261115-3"
CREATED_AT = "2026-11-15T13:25:00+00:00"
HOLD_ID = "O-HOLD-INTERVAL"
FRAME_ID = "cube.definition.balance-frame"
CM_FUNCTION = "cube.function.manage-configuration"
PRINTER_SOURCE = "https://cdn1.bambulab.com/documentation/quick-start-a75adcb1d5d5e/Quick%20Start%20Guide%20for%20A1.pdf"


def build_review(history):
    by = {(r["id"], r["revision"]): r for r in history}
    original = by["cube.simulation.snapshot", SOURCE]
    ctx = original["data"]["context_refs"]
    collections = {key: [by[x["id"], x["revision"]] for x in ctx[key]]
                   for key in ("requirements", "kdps", "functions", "products", "verification_cases")}
    original_rows = {r["id"]: r for rows in collections.values() for r in rows}
    new_ids = set(original_rows) | {HOLD_ID, FRAME_ID, CM_FUNCTION, "R-DETECT", "cube.verify.R-DETECT"}
    updates = []

    def retarget(value):
        if isinstance(value, list):
            return [retarget(x) for x in value]
        if not isinstance(value, dict):
            return value
        if set(value) == {"id", "revision"} and value["id"] in new_ids:
            return ref(value["id"], REVISION)
        history_fields = {"supersedes", "source_record", "original_record", "source_snapshot_ref", "source_proposal_ref"}
        return {k: copy.deepcopy(v) if k in history_fields else retarget(v) for k, v in value.items()}

    def add(id, kind, data, owner="cube.system", links=()):
        r = make_record(project_id="balancing-cube", id=id, revision=REVISION, kind=kind,
                        created_at=CREATED_AT, actor={"type": "human", "id": "hirototamura"},
                        product_node=owner, data=data, links=list(links))
        updates.append(r)
        return r

    decision = add("cube.review.requirements", "review_decision", {
        "decision": "accepted", "reviewed_on": "2026-11-15", "reviewed_timezone": "Asia/Tokyo",
        "scope": ["required mission/hold/install obligations", "10 s demonstration hold interval",
                  "manufacturing and project constraints", "requirement derivation rationale",
                  "vertical yaw axis", "automatic support-corner identification", "configuration management allocation"],
        "authorization": "User requirement-by-requirement review in this chat, including automatic identification before balance starts.",
        "source_model_ref": ref("cube.system-model.active", SOURCE),
        "id_normalization": {"R-PEPEAT": "R-REPEAT", "R-TILST": "R-TILT"},
        "retired_requirement_ids": ["C-FIT-MATERIAL"],
        "reclassified_constraint_ids": ["C-BUDGET", "C-FIT-PRINT", "C-JAPAN"],
        "excluded_scope": ["unlimited-duration holding claim", "new numerical trial or score contract", "controller code implementation"],
    })
    hold = add(HOLD_ID, "parameter", {
        "name": "Demonstration hold interval", "role": "operating", "value": 10, "unit": "s",
        "origin": "human_design_decision", "standard_uncertainty": None,
        "purpose": "Acceptance interval after manual release; not an optimization variable.",
        "rationale": "The user selected 10 s for the demonstration. Continued holding beyond that interval is an unverified expectation.",
        "requirement_refs": [ref(x, REVISION) for x in ("R-HOLD", "R-REPEAT", "R-DRIFT", "R-RMS", "R-TILT", "R-YAW")],
    })
    frame = add(FRAME_ID, "definition", {
        "name": "Balance-start reference axes", "yaw_axis": "World vertical through the support vertex, fixed at balance-start time.",
        "roll_axis": "Horizontal x axis at balance start; positive body-x projected onto the horizontal plane.",
        "pitch_axis": "Horizontal y axis completing a right-handed frame: y = z cross x.",
        "angle_zero": "The balance-start orientation sets the yaw reference; no fixed yaw heading is required.",
        "yaw_rate": "Angular velocity projected on the fixed vertical axis, not on a tilted body-z axis.",
        "implementation_note": "Existing tilt_x/tilt_y slope angles are not relabelled as finite Euler roll/pitch angles.",
        "horizontal_axis_status": "Explicit engineering convention for review; the user's specified yaw axis is fixed vertical.",
        "translations": {"ja": {"name": "バランス保持開始時の基準軸", "description": "yaw軸は支持頂点を通る開始時の鉛直軸。roll軸は開始時の機体+xを水平面へ投影したx軸、pitch軸は右手系を成すy軸とする。yaw角速度は固定した鉛直軸への角速度の射影であり、傾いた機体z軸周りの角速度ではない。"}},
    })
    condition = "Use the first 10 s after manual release, as defined by O-HOLD-INTERVAL, as the hold interval."
    condition_ja = "手動解放後の最初の10 sを、O-HOLD-INTERVALで定義する保持区間とする。"
    constraint_ids = {"C-BUDGET", "C-FIT-PRINT", "C-JAPAN"}
    support = {x: ["R-TILT", "R-RMS"] for x in ("R-DRIVE-CURRENT", "R-DRIVE-SPEED", "R-DRIVE-TEMP", "R-DRIVE-TORQUE", "R-DRIVE-VOLTAGE", "R-MODEL", "R-SYNC", "R-VISION")}
    support.update({x: ["M-VERTEX"] for x in ("R-DRIFT", "R-RMS", "R-TILT", "R-HOLD")})
    support.update({"R-REPEAT": ["R-HOLD"], "R-TRACE": ["R-MODEL", "R-REPEAT"]})
    for old in collections["requirements"]:
        id = old["id"]
        d, links = retarget(old["data"]), retarget(old["links"])
        d.update(supersedes=ref(old), review_decision_ref=ref(decision))
        if id == "C-FIT-MATERIAL":
            d.update(status="retired", retirement_reason="Material choice belongs to the manufacturing design, not a separate system requirement.")
            d["verification_case_ref"] = old["data"]["verification_case_ref"]
            add(id, "requirement", d, old["product_node"])
            continue
        if d.get("member_refs"):
            d["member_refs"] = [x for x in d["member_refs"] if x["id"] != "C-FIT-MATERIAL"]
        if id == "cube.req.gnc":
            d["member_refs"].append(ref("R-DETECT", REVISION))
        if id in constraint_ids:
            d.update(record_role="constraint", obligation="constraint", constraint_scope="project" if id == "C-BUDGET" else "manufacturing")
            d["level"] = d["constraint_scope"] + "_constraint"
            links = [e for e in links if e["type"] == "constrain"]
            if id == "C-FIT-PRINT":
                links = [e for e in links if e["target"]["id"] != "D-SIDE"]
                d["conditions"] = ["Check each printed part in its planned print orientation against the printer build volume; do not limit the assembled Cube envelope."]
                d["translations"]["ja"]["conditions"] = ["各造形部品の造形姿勢で寸法を確認する。組立後のCube全体に造形範囲を適用しない。"]
                d["acceptance_criteria"].pop("limits_status", None)
                d["unresolved_items"] = [{"id": "C-FIT-PRINT.TBR.1", "description": "Check actual part geometry, print orientation and process clearance on Bambu Lab A1.", "owner": "cube.mechanical"}]
                d["translations"]["ja"]["unresolved_items"] = [{"id": "C-FIT-PRINT.TBR.1", "description": "Bambu Lab A1で各部品の形状、造形姿勢、工程上の余白を確認する。", "owner": "cube.mechanical"}]
            if id == "C-JAPAN":
                links += [{"type": "constrain", "target": e["target"], "scope": "Manufacturing procurement constraint"} for e in retarget(old["links"]) if e["type"] == "allocate"]
            add(id, "constraint", d, old["product_node"], links)
            continue
        if id in support:
            links = [e for e in links if e["type"] != "derive"]
            for parent in support[id]:
                links.append({"type": "derive", "target": ref(parent, REVISION), "rationale": "Drive capability supports balance performance." if id.startswith("R-DRIVE-") else "Enables or verifies the parent obligation under the stated hold conditions."})
        if any("30 s" in x for x in d.get("conditions", [])) or id == "R-REPEAT":
            d["conditions"] = [condition if "30 s" in x else x for x in d.get("conditions", [])]
            d["translations"]["ja"]["conditions"] = [condition_ja if "30 s" in x else x for x in d["translations"]["ja"].get("conditions", [])]
            d["hold_interval_ref"] = ref(hold)
            if id == "R-REPEAT":
                d["conditions"].append(condition)
                d["translations"]["ja"]["conditions"].append(condition_ja)
        if id == "R-HOLD":
            d["statement"] = "After manual placement and release, the Cube shall hold its vertex position for at least 10 s without external support."
            d["translations"]["ja"]["statement"] = "手動で設置して解放した後、Cubeは外部支持なしで頂点姿勢を10 s以上保持しなければならない。"
            d["acceptance_criteria"].update(value=10, limit_ref=ref(hold))
            d["translations"]["ja"]["acceptance_criteria"] = "O-HOLD-INTERVALで定める10 s以上、実機で外部支持なしに保持する。"
        if id == "R-YAW":
            d["coordinate_frame_ref"] = ref(frame)
            d["conditions"].append(frame["data"]["yaw_rate"])
            d["translations"]["ja"]["conditions"].append("yawは保持開始時の支持頂点を通る鉛直軸周りとする。機体z軸周りの回転とは区別する。")
        if id == "C-PRINT":
            d["unresolved_items"] = [{"id": "C-PRINT.TBR.1", "description": "Confirm the print recipe and demonstrate manufacture on the specified Bambu Lab A1. Material remains a design choice.", "owner": "cube.mechanical"}]
            d["translations"]["ja"]["unresolved_items"] = [{"id": "C-PRINT.TBR.1", "description": "Bambu Lab A1の造形条件を決め、製作可能性を確認する。材料は設計上の選択として扱う。", "owner": "cube.mechanical"}]
        if id == "R-TRACE":
            links = [e for e in links if e["type"] != "allocate"] + [{"type": "allocate", "target": ref(CM_FUNCTION, REVISION)}]
            d.update(allocation_scope="local", allocation_rationale="Configuration management owns exact revisions and run provenance.")
        add(id, "requirement", d, old["product_node"], links)

    template = copy.deepcopy(original_rows["R-YAW"]["data"])
    template.update(id="R-DETECT", name="Support-corner identification", statement="Before starting balance control, the control system shall automatically identify the target support corner from the Cube's 8 corners.",
                    acceptance_criteria={"metric": "correctly_identified_support_corners", "operator": "==", "value": 8, "unit": "count", "domain": "hardware"},
                    conditions=["Identify the support corner using attitude/sensor information before enabling balance control."],
                    rationale="The eight-corner mission requires the appropriate support-corner frame before balance control starts.",
                    parent_ref=ref("cube.req.gnc", REVISION), verification_case_ref=ref("cube.verify.R-DETECT", REVISION),
                    review_decision_ref=ref(decision), allocation_scope="local", allocation_rationale="Attitude estimation identifies the support corner.",
                    unresolved_items=[{"id": "R-DETECT.TBR.1", "description": "Define the valid initial attitude/sensor conditions and handling of an ambiguous corner. No new numeric tolerance is assumed.", "owner": "cube.gnc"}])
    for key in ("supersedes", "source_record", "source_status", "original_record"):
        template.pop(key, None)
    template["hardware_verification_required"] = True
    template["source"] = "User requirement review and automatic-identification clarification, 2026-11-15."
    template["translations"] = {"ja": {"name": "支持頂点の自動識別", "statement": "制御系はバランス保持を開始する前に、Cubeの8頂点から対象の支持頂点を自動識別しなければならない。", "conditions": ["保持制御を有効にする前に、姿勢・センサ情報から支持頂点を識別する。"], "acceptance_criteria": "8頂点それぞれについて、制御開始前に正しい支持頂点を識別する。", "rationale": "8頂点のミッションでは、保持制御の前に支持頂点に対応する座標系を選ぶ必要がある。", "unresolved_items": [{"id": "R-DETECT.TBR.1", "description": "有効な初期姿勢・センサ条件と、頂点を一意に識別できない場合の扱いを定義する。数値許容差は追加しない。", "owner": "cube.gnc"}]}}
    add("R-DETECT", "requirement", template, "cube.component.controller", [
        {"type": "derive", "target": ref("M-VERTEX", REVISION)},
        {"type": "allocate", "target": ref("cube.function.estimate-attitude", REVISION)}])

    active = {r["id"]: r for r in updates if r["kind"] in {"requirement", "constraint"} and r["data"].get("status") != "retired"}
    for old in collections["functions"]:
        d = retarget(old["data"])
        d.update(supersedes=ref(old), review_decision_ref=ref(decision))
        d["requirement_ids"] = [x for x in d.get("requirement_ids", []) if x in active and x != "R-TRACE"]
        if old["id"] == "cube.function.estimate-attitude":
            d["requirement_ids"].append("R-DETECT")
            d["outputs"].append("Identified support corner before balance control")
        add(old["id"], "function", d, old["product_node"], retarget(old["links"]))
    d = retarget(original_rows["cube.function.evaluate-trace"]["data"])
    d.update(name="Manage configuration and run provenance", description="Identify and retain exact requirements, KDP, design, condition and result revisions for each run.",
             requirement_ids=["R-TRACE"], inputs=["Versioned engineering records", "Run configuration"], outputs=["Exact configuration identity", "Version-linked evidence"], review_decision_ref=ref(decision))
    d.pop("source_proposal_ref", None)
    add(CM_FUNCTION, "function", d, "cube.verification", retarget(original_rows["cube.function.evaluate-trace"]["links"]))
    for old in collections["products"]:
        d = retarget(old["data"])
        d["supersedes"] = ref(old)
        if old["id"] == "cube.verification":
            d["function_refs"].append(ref(CM_FUNCTION, REVISION))
        add(old["id"], "product", d, old["product_node"], retarget(old["links"]))

    inverse = defaultdict(list)
    for r in active.values():
        for e in r["links"]:
            if e["type"] == "constrain":
                inverse[e["target"]["id"]].append(ref(r))
    for old in collections["kdps"]:
        d = retarget(old["data"])
        refs = sorted(inverse[old["id"]], key=lambda x: x["id"])
        d.update(supersedes=ref(old), requirement_refs=refs, requirements=[x["id"] for x in refs])
        if old["id"] in {"I-PRINT-X", "I-PRINT-Y", "I-PRINT-Z"}:
            d.update(value=256, origin="manufacturer_specification", source=PRINTER_SOURCE,
                     method="Bambu Lab A1 published build volume; validate usable process clearance for the chosen print.")
        add(old["id"], "parameter", d, old["product_node"], retarget(old["links"]))
    old_cases = {r["id"]: r for r in collections["verification_cases"]}
    for r in active.values():
        if r["data"].get("record_role") == "requirement_group":
            continue
        id = "cube.verify." + r["id"]
        old = old_cases.get(id)
        d = retarget(old["data"]) if old else copy.deepcopy(retarget(old_cases["cube.verify.R-YAW"]["data"]))
        d.update(name="Verification plan for " + r["id"], acceptance_criteria=copy.deepcopy(r["data"]["acceptance_criteria"]),
                 conditions=copy.deepcopy(r["data"].get("conditions", [])), execution_status="not_run", evidence_refs=[],
                 status="planned", physical_verified=None, unresolved_items=copy.deepcopy(r["data"].get("unresolved_items", [])))
        d.pop("requirement_refs", None)
        d["constraint_refs" if r["kind"] == "constraint" else "requirement_refs"] = [ref(r)]
        if old:
            d["supersedes"] = ref(old)
        else:
            d.pop("supersedes", None)
        d["translations"]["ja"].update(name=r["data"]["translations"]["ja"]["name"] + "の検証計画", conditions=r["data"]["translations"]["ja"].get("conditions", []), acceptance_criteria=r["data"]["translations"]["ja"].get("acceptance_criteria"))
        d["translations"]["ja"]["unresolved_items"] = copy.deepcopy(r["data"]["translations"]["ja"].get("unresolved_items", []))
        add(id, "verification_case", d, "cube.verification")

    s = retarget(original["data"])
    s.update(supersedes=ref(original), source_snapshot_ref=ref(original), review_decision_ref=ref(decision))
    for key, kind in (("requirements", "requirement"), ("constraints", "constraint"), ("kdps", "parameter"), ("functions", "function"), ("products", "product"), ("verification_cases", "verification_case")):
        rows = [r for r in updates if r["kind"] == kind and r["data"].get("status") != "retired" and r["id"] != HOLD_ID]
        s["context_refs"][key] = [ref(r) for r in rows]
    s["context_refs"]["operating_parameters"] = [ref(hold)]
    s["context_refs"]["definitions"] = [ref(frame)]
    s["operating_parameters"] = {"hold_interval_s": 10, "hold_interval_ref": ref(hold)}
    s["reference_frames"] = copy.deepcopy(frame["data"])
    s["kdps"]["entries"] = [r["data"] for r in updates if r["kind"] == "parameter" and r["id"] != HOLD_ID]
    s["kdps"]["revision"] = REVISION
    s["mission"].update(revision=REVISION, requirements=[r["data"] for r in active.values() if r["kind"] == "requirement"],
                         constraints=[r["data"] for r in active.values() if r["kind"] == "constraint"])
    s["mission"]["owned"]["printer"].update(model="Bambu Lab A1", build_volume_mm=[256, 256, 256], specification_source=PRINTER_SOURCE)
    snapshot = add("cube.simulation.snapshot", "simulation_snapshot", s, links=[{"type": "derive", "target": ref(original)}])
    old_model = by["cube.system-model.active", SOURCE]
    d = copy.deepcopy(old_model["data"])
    d.update(supersedes=ref(old_model), simulation_snapshot_ref=ref(snapshot), review_decision_ref=ref(decision), architecture_ref=ref(decision),
             baseline_ref=ref("cube.baseline.requirement-review", REVISION), scope="User-reviewed system requirements, separate project/manufacturing constraints, 10 s demonstration interval and automatic corner detection.")
    previous_review = by.get(("cube.system-model.active", "requirements-review-20261115-2"))
    if previous_review:
        d["supersedes"] = ref(previous_review)
    add(old_model["id"], "system_model", d)
    for id in ("cube.configuration.cm-01", "cube.configuration.catalogue"):
        old = by[id, SOURCE]
        d = copy.deepcopy(old["data"])
        d["supersedes"] = ref(old)
        if id.endswith("cm-01"):
            d.update(snapshot_ref=ref(snapshot), snapshot_record_sha256=digest(snapshot), requirements_refs=s["context_refs"]["requirements"], constraint_refs=s["context_refs"]["constraints"])
        else:
            d["reviewed_requirements_ref"] = ref("cube.configuration.cm-01", REVISION)
            d["entries"] = [ref(x["id"], REVISION) if x["id"] == "cube.configuration.cm-01" else x for x in d["entries"]]
        add(id, old["kind"], d, old["product_node"])
    add("cube.baseline.requirement-review", "baseline", {"name": "User requirement review", "reason": "Apply the user's requirement-by-requirement comments and automatic corner detection clarification.", "source_baseline_ref": old_model["data"]["baseline_ref"], "review_decision_ref": ref(decision), "members": [{**ref(r), "sha256": digest(r)} for r in updates], "physical_verified": False, "adopted_design_baseline": False})
    return updates


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--store", type=Path, default=ROOT / "store")
    p.add_argument("--write-docs", action="store_true")
    args = p.parse_args()
    loader = runpy.run_path(str(ROOT / "refine_model.py"))["load_records"]
    rows = build_review(loader(args.store))
    imported = Store(args.store).import_records(rows)
    if args.write_docs:
        write_documents(rows)
    print(json.dumps({"revision": REVISION, "records": len(rows), "import": imported}, indent=2))


def write_documents(rows, repository_root=None):
    root = repository_root or ROOT.parents[1]
    for lang in ("en", "ja"):
        en = lang == "en"
        lines = ["# " + ("Balancing Cube requirements and constraints" if en else "Balancing Cubeの要求と制約"), "",
                 f"`{REVISION}` · 2026-11-15", "",
                 ("19 requirements, 7 classification groups, 3 separate constraints. Checks remain planned/not run."
                  if en else "要求19件、分類グループ7件、別枠の制約3件。検証は計画段階・未実行。"), "",
                 "`O-HOLD-INTERVAL = 10 s` · [Review / 改訂の根拠](cube_requirements_review.md)", "",
                 "Regenerate: `python projects/balancing-cube/apply_requirement_review.py --write-docs`.", ""]
        for r in sorted(rows, key=lambda r: r["id"]):
            d = r["data"]
            if r["kind"] not in {"requirement", "constraint"} or d.get("status") == "retired":
                continue
            t = d if en else d.get("translations", {}).get("ja", {})
            lines += [f"## {r['id']}: {t.get('name', d.get('name'))}", "",
                      f"`{r['id']}@{REVISION}` · {d.get('record_role')} · {d.get('constraint_scope', d.get('level'))} · {d.get('verification_status', 'not_applicable')}", ""]
            if t.get("statement"):
                lines += [t["statement"], ""]
            if d.get("acceptance_criteria"):
                lines += ["Acceptance / 合否基準: " + json.dumps(d["acceptance_criteria"], ensure_ascii=False), ""]
            conditions = t.get("conditions", d.get("conditions", []))
            if conditions:
                lines += ["Conditions / 条件:"] + ["- " + x for x in conditions] + [""]
            if d.get("rationale"):
                lines += [t.get("rationale", d["rationale"]), ""]
            for relation, label in (("derive", "Derived from"), ("allocate", "Allocation")):
                ids = [e["target"]["id"] for e in r["links"] if e["type"] == relation]
                if ids:
                    lines += [label + ": " + ", ".join(ids), ""]
            if d.get("verification_method"):
                lines += ["Verification method: " + d["verification_method"], ""]
            unresolved = t.get("unresolved_items", d.get("unresolved_items", []))
            if unresolved:
                lines += ["Open items / 未解決事項:"] + [f"- {x.get('id', '')}: {x.get('description', '')}" for x in unresolved] + [""]
        (root / f"docs/{lang}/balancing_cube_requirements.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
