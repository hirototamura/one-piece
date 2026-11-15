"""Append the authorized eight-corner mission and precise KDP requirement references."""
from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from pathlib import Path

from onepiece.model import digest, make_record, ref
from onepiece.store import Store

ROOT = Path(__file__).resolve().parent
SOURCE_REVISION = "reviewed-20261019-1"
REVISION = "refined-20261115-1"
CREATED_AT = "2026-11-15T10:39:59+00:00"
PROJECT = "balancing-cube"
ACTOR = {"type": "human", "id": "hirototamura"}
POLICY_ID = "cube.change-contract.control-algorithm"


def load_records(store_path):
    records = {}
    for path in sorted(Path(store_path).glob("commits/*/records.json")):
        for record in json.loads(path.read_text()):
            if record["project_id"] != PROJECT:
                continue
            key = record["id"], record["revision"]
            if key in records and records[key] != record:
                raise ValueError(f"Conflicting source record: {key}")
            records[key] = record
    return list(records.values())


def build_refinement(records):
    by_ref = {(r["id"], r["revision"]): r for r in records}
    source = by_ref["cube.simulation.snapshot", SOURCE_REVISION]
    context = source["data"]["context_refs"]
    resolve = lambda name: [by_ref[r["id"], r["revision"]] for r in context[name]]
    requirements, parameters, cases = (resolve(n) for n in ("requirements", "kdps", "verification_cases"))
    updated_ids = {r["id"] for r in requirements + parameters + cases}
    updates = []

    def retarget(value):
        if isinstance(value, list):
            return [retarget(v) for v in value]
        if not isinstance(value, dict):
            return value
        if set(value) == {"id", "revision"} and value["id"] in updated_ids and value["revision"] == SOURCE_REVISION:
            return ref(value["id"], REVISION)
        historical = {"supersedes", "source_record", "original_record", "source_snapshot_ref"}
        return {k: copy.deepcopy(v) if k in historical else retarget(v) for k, v in value.items()}

    def add(id, kind, data, owner="cube.system", links=()):
        record = make_record(project_id=PROJECT, id=id, revision=REVISION, kind=kind,
                             product_node=owner, created_at=CREATED_AT, actor=ACTOR,
                             data=data, links=list(links))
        updates.append(record)
        return record

    decision = add("cube.review.model-refinement", "review_decision", {
        "decision": "accepted", "reviewed_on": "2026-11-15", "reviewed_timezone": "Asia/Tokyo",
        "reviewer": ACTOR,
        "authorization": "The Cube shall balance on each of its 8 corners with its 3 reaction wheels. を追加するのに合意。",
        "scope": ["eight-corner mission", "atomic requirement references for KDPs", "controller algorithm edit boundary"],
        "controller_scope_confirmation": "今回は変更可能範囲を要求・契約に明記し、コード提案・実行の拡張は次の段階にする",
        "source_model_ref": ref("cube.system-model.active", SOURCE_REVISION),
        "excluded_scope": ["controller code execution", "new score formula", "physical verification", "hardware design adoption"],
    })
    policy = add(POLICY_ID, "design_policy", {
        "name": "Controller algorithm change boundary", "status": "authorized_scope_runtime_not_implemented",
        "approval_state": "human_reviewed", "review_decision_ref": ref(decision),
        "allowed_repository": "balancing-cube-simulation", "allowed_path": "balancing_cube/control.py",
        "allowed_changes": ["control algorithm", "controller internal state", "controller gain calculation"],
        "fixed_boundaries": ["plant and contact physics", "sensor observations", "actuator limits", "trial timing",
                             "requirements", "test conditions", "screening and scoring", "evidence recording"],
        "current_runtime": "gain_parameter_proposals_only",
        "algorithm_proposal_execution_implemented": False,
        "activation": "A later implementation must map the approved controller interface into the native and requested accelerated runners, then pin source hashes per candidate.",
        "translations": {"ja": {"name": "制御アルゴリズムの変更可能範囲",
            "description": "制御アルゴリズムのコード変更は balancing-cube-simulation/balancing_cube/control.py に限定する。今回は変更範囲の契約のみを定め、提案・実行の拡張は次段階とする。"}},
    })
    mission_source = by_ref["M-VERTEX", "bottom-corner-000-20261017-3"]
    for original in requirements:
        data = retarget(original["data"])
        data["supersedes"] = ref(original)
        if original["id"] == "M-VERTEX":
            for field in ("statement", "acceptance_criteria"):
                data[field] = copy.deepcopy(mission_source["data"][field])
            for field in ("statement", "acceptance_criteria"):
                data["translations"]["ja"][field] = mission_source["data"]["translations"]["ja"][field]
            data["review_decision_ref"] = ref(decision)
        add(original["id"], "requirement", data, original["product_node"], retarget(original["links"]))

    constrained_by = defaultdict(list)
    for record in updates:
        if record["kind"] == "requirement" and record["data"].get("record_role") == "requirement":
            for edge in record["links"]:
                if edge["type"] == "constrain":
                    constrained_by[edge["target"]["id"]].append(ref(record))
    for original in parameters:
        data = retarget(original["data"])
        references = sorted(constrained_by[original["id"]], key=lambda r: r["id"])
        if not references:
            raise ValueError("Parameter has no atomic requirement relationship: " + original["id"])
        data.update(supersedes=ref(original), requirement_refs=references, requirements=[r["id"] for r in references])
        add(original["id"], "parameter", data, original["product_node"], retarget(original["links"]))
    for original in cases:
        data = retarget(original["data"])
        data["supersedes"] = ref(original)
        if original["id"] == "cube.verify.M-VERTEX":
            data["acceptance_criteria"] = copy.deepcopy(mission_source["data"]["acceptance_criteria"])
            data["translations"]["ja"]["acceptance_criteria"] = mission_source["data"]["translations"]["ja"]["acceptance_criteria"]
        add(original["id"], "verification_case", data, original["product_node"], retarget(original["links"]))

    data = retarget(source["data"])
    data.update(supersedes=ref(source), source_snapshot_ref=ref(source), review_decision_ref=ref(decision),
                change_contract_ref=ref(policy), change_contract=copy.deepcopy(policy["data"]))
    data["context_refs"]["change_contract"] = ref(policy)
    data["kdps"]["entries"] = [r["data"] for r in updates if r["kind"] == "parameter"]
    data["kdps"]["revision"] = REVISION
    data["mission"]["mission"] = mission_source["data"]["statement"]
    data["mission"]["requirements"] = [r["data"] for r in updates if r["kind"] == "requirement"]
    data["mission"]["revision"] = REVISION
    snapshot = add("cube.simulation.snapshot", "simulation_snapshot", data,
                   links=[{"type": "derive", "target": ref(source)}])
    original_model = by_ref["cube.system-model.active", SOURCE_REVISION]
    data = copy.deepcopy(original_model["data"])
    data.update(supersedes=ref(original_model), simulation_snapshot_ref=ref(snapshot),
                source_snapshot_ref=ref(source), review_decision_ref=ref(decision),
                baseline_ref=ref("cube.baseline.model-refinement", REVISION), change_contract_ref=ref(policy),
                scope="Eight-corner mission, atomic KDP requirement references and controller edit policy. Existing allocation and numerical evidence scopes are preserved.")
    data["translations"]["ja"]["scope"] = "8頂点のミッション、KDPの個別要求参照、制御コードの変更範囲。既存の割当と数値証拠の適用範囲を保持する。"
    add(original_model["id"], "system_model", data)

    # Advance the requirements-view role; executable and historical selections stay pinned.
    original_cm = by_ref["cube.configuration.cm-01", "bom-reference-20261021-1"]
    data = copy.deepcopy(original_cm["data"])
    data.update(supersedes=ref(original_cm), snapshot_ref=ref(snapshot), snapshot_record_sha256=digest(snapshot),
                requirements_refs=snapshot["data"]["context_refs"]["requirements"])
    add(original_cm["id"], original_cm["kind"], data, original_cm["product_node"])
    original_catalogue = by_ref["cube.configuration.catalogue", "bom-reference-20261021-1"]
    data = copy.deepcopy(original_catalogue["data"])
    data.update(supersedes=ref(original_catalogue), reviewed_requirements_ref=ref(original_cm["id"], REVISION))
    data["entries"] = [ref(r["id"], REVISION) if r["id"] == original_cm["id"] else r for r in data["entries"]]
    add(original_catalogue["id"], original_catalogue["kind"], data, original_catalogue["product_node"])
    add("cube.baseline.model-refinement", "baseline", {
        "name": "Eight-corner mission and KDP trace refinement", "reason": decision["data"]["authorization"],
        "review_decision_ref": ref(decision), "source_baseline_ref": original_model["data"]["baseline_ref"],
        "members": [{**ref(r), "sha256": digest(r)} for r in updates],
        "physical_verified": False, "adopted_design_baseline": False,
    })
    return updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=ROOT / "store")
    parser.add_argument("--write-docs", action="store_true")
    args = parser.parse_args()
    records = build_refinement(load_records(args.store))
    imported = Store(args.store).import_records(records)
    if args.write_docs:
        write_documents(records)
    print(json.dumps({"revision": REVISION, "records": len(records), "import": imported}, indent=2))


def write_documents(records, repository_root=None):
    root = repository_root or ROOT.parents[1]
    requirements = sorted((r for r in records if r["kind"] == "requirement"), key=lambda r: r["id"])
    for language in ("en", "ja"):
        english = language == "en"
        lines = ["# " + ("Balancing Cube requirements" if english else "Balancing Cubeの要求"), "",
                 f"`{REVISION}` · human direction: 2026-11-15 · baseline: `cube.baseline.model-refinement@{REVISION}`", "",
                 ("The eight-corner mission and atomic KDP references extend the reviewed allocation model. Verification remains separate."
                  if english else "8頂点のミッションとKDPの個別要求参照を、レビュー済みの割当モデルに反映した。検証状態は別に保持する。"), "",
                 "Regenerate: `python projects/balancing-cube/refine_model.py --write-docs`.", ""]
        for record in requirements:
            data = record["data"]
            text = data if english else data["translations"]["ja"]
            lines += [f"## {record['id']}: {text['name']}", "",
                      f"`{record['id']}@{REVISION}` · {data.get('status')} · {data.get('approval_state')} · {data.get('verification_status', 'not_applicable')}", ""]
            if text.get("statement"):
                lines += [text["statement"], ""]
            if text.get("rationale"):
                lines += [text["rationale"], ""]
            if data.get("record_role") == "requirement":
                lines += ["Acceptance / 合否基準: " + json.dumps(data["acceptance_criteria"], ensure_ascii=False), "",
                          "Allocation: " + ", ".join(e["target"]["id"] for e in record["links"] if e["type"] == "allocate"), ""]
            if data.get("unresolved_items"):
                lines += ["Open items / 未解決事項:"]
                lines += [f"- {item.get('id', '')}: {item.get('description', '')}"
                          for item in (data["unresolved_items"] if english else text.get("unresolved_items", data["unresolved_items"]))]
                lines += [""]
        (root / f"docs/{language}/balancing_cube_requirements.md").write_text("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    main()
