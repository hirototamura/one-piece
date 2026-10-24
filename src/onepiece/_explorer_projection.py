"""Browser projection of exact One-Piece model revisions; never writes canonical records."""
from __future__ import annotations

from typing import Any

from .model import RecordError


def record_by_ref(records, reference):
    if not reference:
        return None
    key = reference.get("id"), reference.get("revision")
    if key not in records:
        raise RecordError(f"Missing explorer model reference: {key}")
    return records[key]


def project_model(records, model):
    model_data = model["data"]
    snapshot_ref = model_data["simulation_snapshot_ref"]
    snapshot = record_by_ref(records, snapshot_ref)
    context_refs = snapshot["data"]["context_refs"]
    functions = []
    for reference in context_refs.get("functions", []):
        record = record_by_ref(records, reference)
        functions.append({**record["data"], "id": record["id"], "revision": record["revision"], "kind": "function", "links": record.get("links", [])})

    current_requirements = [record_by_ref(records, reference)
                            for reference in context_refs["requirements"]]
    groups = [r for r in current_requirements if r["data"].get("record_role") == "requirement_group"]
    obligations = [r for r in current_requirements if r["data"].get("record_role") != "requirement_group"]

    group_by_id = {r["id"]: r for r in groups}
    kdp_refs = {(r["id"], r["revision"]): r for r in context_refs.get("kdps", [])}
    for requirement in obligations:
        for link in requirement.get("links", []):
            if link.get("type") == "constrain":
                target = link.get("target", {})
                kdp_refs[(target.get("id", ""), target.get("revision", ""))] = target

    kdps = []
    for key in sorted(kdp_refs):
        kdp = records.get(key)
        if not kdp:
            kdps.append({"id": key[0], "revision": key[1], "missing": True})
            continue
        kd = kdp.get("data", {})
        kdps.append({
            "id": kdp["id"], "revision": kdp["revision"],
            "name": kd.get("name", kd.get("label", kdp["id"])),
            "symbol": kd.get("symbol"), "quantity": kd.get("quantity"),
            "value": kd.get("value"), "unit": kd.get("unit"),
            "uncertainty": kd.get("uncertainty"),
            "role": kd.get("role"), "origin": kd.get("origin"),
            "source": kd.get("source"), "source_language": kd.get("source_language"),
            "method": kd.get("method"), "model_path": kd.get("model_path"),
            "bounds": kd.get("bounds"), "standard_uncertainty": kd.get("standard_uncertainty"),
            "priority": kd.get("priority"), "note": kd.get("note"),
            "requirements": kd.get("requirements", []),
            "product_node": kdp.get("product_node"), "links": kdp.get("links", []),
        })
    kdp_by_key = {(x["id"], x["revision"]): x for x in kdps}

    cases: dict[tuple[str, str], dict[str, Any]] = {}
    normalized_obligations = []
    for record in sorted(obligations, key=lambda r: r["id"]):
        data = record["data"]
        parent = data.get("parent_ref") or {}
        parent_id = parent.get("id", "")
        group_record = group_by_id.get(parent_id)
        group_name = group_record["data"].get("name") if group_record else "Mission"
        case_ref = data.get("verification_case_ref")
        case = record_by_ref(records, case_ref)
        if case and case_ref:
            cases[(case_ref["id"], case_ref["revision"])] = case
        related_kdps = []
        for link in record.get("links", []):
            if link.get("type") == "constrain":
                target = link.get("target", {})
                related_kdps.append(kdp_by_key.get((target.get("id"), target.get("revision")), {
                    "id": target.get("id"), "revision": target.get("revision"), "missing": True
                }))
        translations = data.get("translations", {}).get("ja", {})
        normalized_obligations.append({
            "id": record["id"], "revision": record["revision"],
            "name": data.get("name", record["id"]),
            "group_id": parent_id or "M-VERTEX", "group": group_name,
            "level": data.get("level"), "statement": data.get("statement"),
            "statement_ja": translations.get("statement"),
            "name_ja": translations.get("name"),
            "rationale": data.get("rationale"),
            "rationale_ja": translations.get("rationale"),
            "conditions": data.get("conditions", []),
            "conditions_ja": translations.get("conditions", []),
            "acceptance": data.get("acceptance_criteria"),
            "acceptance_ja": translations.get("acceptance_criteria"),
            "verification_method": data.get("verification_method"),
            "verification_status": data.get("verification_status"),
            "hardware_verification_required": data.get("hardware_verification_required"),
            "physical_verified": data.get("physical_verified"),
            "status": data.get("status"),
            "source_status": data.get("source_status"),
            "approval_state": data.get("approval_state"),
            "review_decision_ref": data.get("review_decision_ref"),
            "allocation_scope": data.get("allocation_scope"),
            "allocation_rationale": data.get("allocation_rationale"),
            "previous_allocations": [l["target"] for l in (record_by_ref(records, data.get("supersedes")) or {}).get("links", []) if l["type"] == "allocate"],
            "unresolved_items": data.get("unresolved_items", []),
            "unresolved_items_ja": translations.get("unresolved_items", []),
            "verification_case_ref": case_ref,
            "verification_case": (case or {}).get("data", {}),
            "source_record": data.get("source_record"),
            "product_node": record.get("product_node"),
            "links": record.get("links", []),
            "kdps": related_kdps,
        })

    normalized_groups = []
    for record in sorted(groups, key=lambda r: (r["data"].get("level", ""), r["id"])):
        data = record["data"]
        members = data.get("member_refs", [])
        normalized_groups.append({
            "id": record["id"], "revision": record["revision"],
            "name": data.get("name", record["id"]),
            "name_ja": data.get("translations", {}).get("ja", {}).get("name"),
            "level": data.get("level"),
            "parent_ref": data.get("parent_ref"),
            "members": [m.get("id") for m in members],
            "record_role": data.get("record_role", "requirement_group"),
            "status": data.get("status"), "approval_state": data.get("approval_state"),
            "physical_verified": data.get("physical_verified"),
            "product_node": record.get("product_node"), "links": record.get("links", []),
            "rationale": data.get("rationale"),
            "rationale_ja": data.get("translations", {}).get("ja", {}).get("rationale"),
        })

    verification_cases = []
    for key, case in sorted(cases.items()):
        verification_cases.append({
            "id": case["id"], "revision": case["revision"],
            "data": case.get("data", {}), "links": case.get("links", []),
            "product_node": case.get("product_node"),
        })

    product_refs: dict[tuple[str, str], dict[str, str]] = {}
    for reference in context_refs.get("products", []):
        product_refs[(reference["id"], reference["revision"])] = reference
    graph_records = [*groups, *obligations]
    graph_records.extend(records[key] for key in kdp_refs if key in records)
    graph_records.extend(cases.values())
    for record in graph_records:
        for link in record.get("links", []):
            target = link.get("target", {})
            target_record = records.get((target.get("id", ""), target.get("revision", "")))
            if link.get("type") == "allocate" and target_record and target_record.get("kind") == "product":
                product_refs[(target_record["id"], target_record["revision"])] = target

    products = []
    for key, product_ref in sorted(product_refs.items()):
        record = records.get(key)
        if not record:
            continue
        data = record.get("data", {})
        translations = data.get("translations", {}).get("ja", {})
        products.append({
            **data,
            "id": record["id"], "revision": record["revision"],
            "name": data.get("name", record["id"]), "name_ja": translations.get("name"),
            "role": "product", "status": data.get("status"),
            "physical_verified": data.get("physical_verified"),
            "parent_product_ref": data.get("parent_product_ref"),
            "method": data.get("method"), "note": data.get("note"),
            "source": data.get("source"), "source_language": data.get("source_language"),
            "product_node": record.get("product_node"), "links": record.get("links", []),
        })


    result = {
        "balancing_cube": {
            "model": {**model_data, "id": model["id"], "revision": model["revision"],
                      "created_at": model["created_at"]},
            "groups": normalized_groups, "requirements": normalized_obligations,
            "kdps": kdps, "verification_cases": verification_cases,
            "products": products, "functions": functions,
            "counts": {"obligations": len(normalized_obligations), "groups": len(normalized_groups),
                       "verification_cases": len(verification_cases), "linked_kdps": len(kdps)},
        },
        "eclss": None, "scrubber": None,
    }
    architecture_ref = model_data.get("architecture_ref")
    decision = record_by_ref(records, architecture_ref) if architecture_ref else None
    if (decision and decision["kind"] == "review_decision"
            and decision["data"].get("decision") == "accepted"
            and model_data.get("approval_state") == "human_reviewed"):
        result["balancing_cube"]["reviewed_architecture"] = {
            **architecture_ref, "status": model_data.get("status"),
            "approval_state": model_data.get("approval_state"),
            "reviewed_on": decision["data"].get("reviewed_on"),
            "functions": functions,
            "components": [{**p, "kind": "component"} for p in products if p.get("record_role") == "component"],
            "requirement_allocations": [{"source": r["id"], "targets": [l["target"]["id"] for l in r["links"] if l["type"] == "allocate"],
                                         "scope": r["allocation_scope"], "rationale": r["allocation_rationale"]} for r in normalized_obligations],
            "parameter_allocations": [{"source": p["id"], "targets": [l["target"]["id"] for l in p["links"] if l["type"] == "allocate"]} for p in kdps],
        }
    return result
