"""Test the curated migration without evidence downloads or source-store writes."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import runpy

import pytest

from onepiece.model import canonical_bytes, digest, ref
from onepiece.store import Store, current_records


PROJECT_ROOT = Path(__file__).resolve().parents[1] / "projects/balancing-cube"


@pytest.fixture(scope="module")
def migration():
    return runpy.run_path(str(PROJECT_ROOT / "migrate_standards.py"))


@pytest.fixture(scope="module")
def history():
    # Do not construct a Store for the tracked project: that could rebuild its
    # local index and would make CI depend on downloaded artifact objects.
    records = {}
    for path in sorted((PROJECT_ROOT / "store/commits").glob("*/records.json")):
        for record in json.loads(path.read_text(encoding="utf-8")):
            key = record["project_id"], record["id"], record["revision"]
            if key in records:
                assert canonical_bytes(records[key]) == canonical_bytes(record)
            records[key] = record
    assert records, "The tracked historical source records are required"
    return list(records.values())


@pytest.fixture(scope="module")
def updates(migration, history):
    before = canonical_bytes(history)
    result = migration["build_updates"](history)
    assert canonical_bytes(history) == before
    return result


@pytest.fixture(scope="module")
def shall_updates(migration, history, updates):
    before = canonical_bytes(history)
    result = migration["build_shall_revision"]([*history, *updates])
    assert canonical_bytes(history) == before
    return result


def by_ref(records):
    return {(r["id"], r["revision"]): r for r in records}


def by_id(records):
    return {r["id"]: r for r in records}


def data_refs(value):
    if isinstance(value, dict):
        if isinstance(value.get("id"), str) and isinstance(value.get("revision"), str):
            yield value["id"], value["revision"]
        else:
            for child in value.values():
                yield from data_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from data_refs(child)


def test_migration_resolves_exact_graph_and_embedded_references(history, updates):
    combined = [*history, *updates]
    Store._check_references(combined)
    available = by_ref(combined)
    for record in updates:
        for reference in data_refs(record["data"]):
            assert reference in available, (record["id"], reference)


def test_builder_is_idempotent_and_does_not_rewrite_history(migration, history, updates):
    before = canonical_bytes(history)
    assert canonical_bytes(migration["build_updates"](copy.deepcopy(history))) == canonical_bytes(updates)
    assert canonical_bytes(migration["build_updates"]([*history, *updates])) == canonical_bytes(updates)
    assert canonical_bytes(history) == before
    assert len(by_ref(updates)) == len(updates)
    for record in updates:
        previous = by_ref(history).get((record["id"], record["revision"]))
        # A later checkout may already contain the published migration. Its
        # deterministic builder must produce the same immutable revisions.
        if previous is not None:
            assert canonical_bytes(previous) == canonical_bytes(record)


def test_numerical_configuration_and_parameter_values_are_unchanged(history, updates):
    old = by_ref(history)[("cube.simulation.snapshot", "fixed-dt-mvp-2")]
    new = by_id(updates)["cube.simulation.snapshot"]
    for field in (
        "model", "controller", "controller_design_plant", "contract", "plan",
        "families", "design_bounds", "parameter_bindings", "comparison_design_ref",
        "physical_fidelity", "new_run_policy",
    ):
        assert canonical_bytes(new["data"][field]) == canonical_bytes(old["data"][field]), field
    for field, value in old["data"]["context_refs"].items():
        if field not in {"requirements", "kdps"}:
            assert new["data"]["context_refs"][field] == value
    previous = by_ref(history)
    new_records = by_id(updates)
    sources = old["data"]["context_refs"]["kdps"]
    parameters = [previous[(r["id"], r["revision"])] for r in sources]
    assert len(parameters) == 37
    language_metadata = {"name", "method", "note", "source", "translations"}
    for source in parameters:
        revised = new_records[source["id"]]
        assert revised["kind"] == source["kind"] == "parameter"
        for field, value in source["data"].items():
            if field not in language_metadata:
                assert revised["data"][field] == value, (source["id"], field)
    assert new["data"]["kdps"]["entries"] == [new_records[r["id"]]["data"] for r in sources]
    assert new["data"]["context_refs"]["kdps"] == [ref(new_records[r["id"]]) for r in sources]


def test_revised_requirements_remain_drafts_with_historical_source_status(history, updates):
    historical = by_ref(history)
    old = historical[("cube.simulation.snapshot", "fixed-dt-mvp-2")]
    sources = {r["id"]: historical[(r["id"], r["revision"])]
               for r in old["data"]["context_refs"]["requirements"]}
    requirements = [r for r in updates if r["kind"] == "requirement"]
    assert len(sources) == 21
    assert len(requirements) == 29  # Eight atomic children split two compound sources.
    for record in requirements:
        data = record["data"]
        assert data["status"] == "draft"
        assert data["approval_state"] == "pending_human_review"
        assert data["physical_verified"] is None
        assert data["verification_status"] == "not_run"
        assert data["original_record"] is False
        if record["id"] in sources:
            source = sources[record["id"]]
            assert data["source_status"] == source["data"]["status"]
            assert data["supersedes"] == ref(source)
            assert data["source_record"]["sha256"] == digest(source)
            assert data["value"] == source["data"].get("value")
            assert data["unit"] == source["data"].get("unit", "1")
    assert not any(r["kind"] == "baseline" for r in updates)


def test_english_obligations_and_japanese_translation_alignment(migration, updates):
    definitions = migration["definitions"]()
    requirements = [r for r in updates
                    if r["kind"] == "requirement" and r["data"]["record_role"] == "requirement"]
    assert {r["id"] for r in requirements} == set(definitions)
    for record in requirements:
        data = record["data"]
        translated = data["translations"]["ja"]
        statement = data["statement"]
        assert data["source_language"] == "en"
        assert re.findall(r"\bmust\b", statement) == ["must"]
        assert not re.search(r"\b(?:shall|should|may)\b", statement, re.IGNORECASE)
        assert len(statement.split()) <= 25, (record["id"], statement)
        assert not re.search(r"[\u3040-\u30ff\u3400-\u9fff]", statement)
        assert statement == definitions[record["id"]]["statement"]
        assert translated["statement"] == definitions[record["id"]]["ja_statement"]
        assert re.search(r"[\u3040-\u30ff\u3400-\u9fff]", translated["statement"])
        assert len(data["conditions"]) == len(translated["conditions"])
        assert [x["id"] for x in data["unresolved_items"]] == [x["id"] for x in translated["unresolved_items"]]
        assert [x["owner"] for x in data["unresolved_items"]] == [x["owner"] for x in translated["unresolved_items"]]
        assert translated["acceptance_criteria"]
        for sentence in data["conditions"]:
            assert len(sentence.split()) <= 25
    profile = by_id(updates)["cube.language.profile"]["data"]
    assert profile["normative_modal"] == "must"
    assert profile["requirement_standard"]["normative_text_available"] is False
    assert profile["requirement_standard"]["clause_audit"] == "not_performed"
    assert profile["writing_standard"]["complete_dictionary_audit"] == "not_performed"


def test_requirement_groups_add_no_test_obligation(migration, updates):
    records = by_id(updates)
    for id in migration["GROUPS"]:
        record = records[id]
        data = record["data"]
        assert data["record_role"] == "requirement_group"
        assert data["statement"] is None
        assert data["translations"]["ja"]["statement"] is None
        assert data["acceptance_criteria"]["applicability"] == "not_applicable"
        assert data["hardware_verification_required"] is False
        assert "verification_case_ref" not in data
        assert "cube.verify." + id not in records
        assert data["member_refs"]
        for member in data["member_refs"]:
            assert records[member["id"]]["data"]["parent_ref"] == ref(record)


def test_corrected_allocations_and_parent_traces(migration, updates):
    records = by_id(updates)
    expected = {
        "M-VERTEX": "cube.system", "R-TILT": "cube.system",
        "R-RMS": "cube.system", "R-DRIFT": "cube.system",
        "R-DRIVE": "cube.actuation", "R-VISION": "cube.verification",
        "R-SYNC": "cube.verification", "F-CONTROL-PERIOD": "cube.gnc",
        "F-SIM-DT": "cube.verification", "I-BUS-I": "cube.actuation",
        "I-BUS-V": "cube.actuation", "I-DRIVE-TEMP": "cube.actuation",
    }
    expected.update({id: "cube.actuation" for id in migration["definitions"]() if id.startswith("R-DRIVE-")})
    for id, owner in expected.items():
        record = records[id]
        assert record["product_node"] == owner
        assert [e["target"] for e in record["links"] if e["type"] == "allocate"] == [ref(records[owner])]
    for record in updates:
        if record["kind"] != "requirement":
            continue
        parent = record["data"]["parent_ref"]
        assert [e["target"] for e in record["links"] if e["type"] == "derive"] == ([parent] if parent else [])
        if parent:
            assert parent["revision"] == migration["REVISION"]


def test_new_verification_cases_are_plans_without_inherited_pass_evidence(updates):
    records = by_id(updates)
    requirements = [r for r in updates
                    if r["kind"] == "requirement" and r["data"]["record_role"] == "requirement"]
    plans = [r for r in updates if r["kind"] == "verification_case"]
    assert len(plans) == len(requirements)
    for requirement in requirements:
        case_ref = requirement["data"]["verification_case_ref"]
        plan = records[case_ref["id"]]
        assert ref(plan) == case_ref
        data = plan["data"]
        assert data["status"] == "planned"
        assert data["execution_status"] == "not_run"
        assert data["requirement_refs"] == [ref(requirement)]
        assert data["acceptance_criteria"] == requirement["data"]["acceptance_criteria"]
        assert data["physical_verified"] is None
        assert data["evidence_refs"] == []
    assert not any(e["type"] == "verify" for r in updates for e in r["links"])
    assert not {r["kind"] for r in updates} & {
        "evaluation", "simulation_run", "verification", "evidence", "design", "design_candidate", "artifact",
    }


def test_active_context_pins_new_drafts_and_retains_exact_comparison(tmp_path, monkeypatch, migration, history, updates):
    # Exercise production context selection while keeping historical artifacts
    # out of the test. Canonical record publication is covered in test_core.py.
    deduplicated = by_ref([r for r in [*history, *updates]
                           if r["revision"] != migration["SHALL_REVISION"]])
    records = list(deduplicated.values())
    store = Store(tmp_path / "isolated-store")
    monkeypatch.setattr(store, "records", lambda project_id=None, kinds=None: [r for r in records
        if (project_id is None or r["project_id"] == project_id) and (not kinds or r["kind"] in kinds)])
    context = store.context("balancing-cube", max_designs=0, max_evidence=0)
    revision = migration["REVISION"]
    assert context["snapshot_ref"] == {"id": "cube.simulation.snapshot", "revision": revision}
    returned = by_id(context["records"])
    snapshot = returned["cube.simulation.snapshot"]
    assert {tuple(sorted(ref(r).items())) for r in context["records"] if r["kind"] == "requirement"} == {
        tuple(sorted(reference.items())) for reference in snapshot["data"]["context_refs"]["requirements"]
    }
    assert all(r["revision"] == revision for r in context["records"] if r["kind"] in {"requirement", "parameter"})
    assert ref(returned["D-000544-52890"]) == {"id": "D-000544-52890", "revision": "legacy-20261009"}
    assert returned["cube.campaign.summary"]["revision"] == "legacy-20261009"
    assert returned["cube.campaign.summary"]["data"]["prior46"]["status_counts"] == {
        "confirmed_numerical_pass": 31,
        "confirmed_numerical_fail": 9,
        "inconclusive_numerical_agreement": 6,
    }
    assert context["counts"]["bounded_designs"] == 0
    assert context["counts"]["pinned_designs"] == 1
    assert by_id(current_records(records))["cube.system-model.active"]["data"]["simulation_snapshot_ref"] == context["snapshot_ref"]


def test_shall_revision_preserves_old_draft_and_versions_exact_traces(history, updates, shall_updates, migration):
    combined = [*history, *updates, *shall_updates]
    Store._check_references(combined)
    available = by_ref(combined)
    assert len(shall_updates) == 91  # 37 KDPs, 29 requirements, 22 plans and 3 model/profile records.
    requirements = [r for r in shall_updates if r["kind"] == "requirement"]
    obligations = [r for r in requirements if r["data"]["record_role"] == "requirement"]
    assert len(requirements) == 29 and len(obligations) == 22
    for record in obligations:
        data = record["data"]
        assert len(re.findall(r"\bshall\b", data["statement"], re.IGNORECASE)) == 1
        assert not re.search(r"\bmust\b", data["statement"], re.IGNORECASE)
        assert data["normative_modal"] == "shall"
        assert data["approval_state"] == "pending_human_review"
        previous = available[(record["id"], migration["REVISION"])]
        assert data["supersedes"] == ref(previous)
        assert data["translations"]["ja"]["statement"] == previous["data"]["translations"]["ja"]["statement"]
    old_statements = {r["id"]: r["data"].get("statement") for r in updates if r["kind"] == "requirement"}
    new_statements = {r["id"]: r["data"].get("statement") for r in requirements}
    assert old_statements["M-VERTEX"].find(" must ") > 0
    assert new_statements["M-VERTEX"].find(" shall ") > 0
    assert len([r for r in shall_updates if r["kind"] == "verification_case"]) == 22
    for record in shall_updates:
        for reference in data_refs(record["data"]):
            assert reference in available, (record["id"], reference)
    for record in shall_updates:
        previous = by_ref([*history, *updates]).get((record["id"], migration["SHALL_REVISION"]))
        if previous is not None:
            assert canonical_bytes(previous) == canonical_bytes(record)


def test_shall_revision_updates_kdp_and_snapshot_pointers_without_changing_values(history, updates, shall_updates, migration):
    records = by_ref([*history, *updates, *shall_updates])
    original = records[("cube.simulation.snapshot", "standards-draft-20261011-1")]
    corrected = by_ref(shall_updates)[("cube.simulation.snapshot", migration["SHALL_REVISION"])]
    assert len(corrected["data"]["context_refs"]["kdps"]) == 37
    assert len(corrected["data"]["context_refs"]["requirements"]) == 29
    for field in ("model", "controller", "controller_design_plant", "contract", "plan", "families",
                  "design_bounds", "physical_fidelity", "new_run_policy", "comparison_design_ref"):
        assert canonical_bytes(corrected["data"][field]) == canonical_bytes(original["data"][field]), field
    old_parameters = {r["id"]: r for r in updates if r["kind"] == "parameter"}
    new_parameters = {r["id"]: r for r in shall_updates if r["kind"] == "parameter"}
    assert len(new_parameters) == 37
    excluded = {"requirement_refs", "language_profile_ref", "supersedes"}
    for id, revised in new_parameters.items():
        for field, value in old_parameters[id]["data"].items():
            if field not in excluded:
                assert canonical_bytes(revised["data"].get(field)) == canonical_bytes(value), (id, field)
        assert all(ref_value["revision"] == migration["SHALL_REVISION"]
                   for ref_value in revised["data"].get("requirement_refs", []))
    for binding in corrected["data"]["parameter_bindings"]:
        assert binding["parameter_ref"]["revision"] == migration["SHALL_REVISION"]


def test_shall_priority_context_is_current_and_retains_31_9_6_summary(tmp_path, monkeypatch, history, updates, shall_updates, migration):
    records = list(by_ref([*history, *updates, *shall_updates]).values())
    store = Store(tmp_path / "shall-store")
    monkeypatch.setattr(store, "records", lambda project_id=None, kinds=None: [r for r in records
        if (project_id is None or r["project_id"] == project_id) and (not kinds or r["kind"] in kinds)])
    context = store.context("balancing-cube", max_designs=0, max_evidence=0)
    assert context["snapshot_ref"] == {"id": "cube.simulation.snapshot", "revision": migration["SHALL_REVISION"]}
    returned = by_ref(context["records"])
    snapshot = returned[("cube.simulation.snapshot", migration["SHALL_REVISION"])]
    for field in ("requirements", "kdps"):
        assert snapshot["data"]["context_refs"][field]
        assert all(r["revision"] == migration["SHALL_REVISION"] for r in snapshot["data"]["context_refs"][field])
    assert returned[("cube.campaign.summary", "legacy-20261009")]["data"]["prior46"]["status_counts"] == {
        "confirmed_numerical_pass": 31,
        "confirmed_numerical_fail": 9,
        "inconclusive_numerical_agreement": 6,
    }
    active = returned[("cube.system-model.active", migration["SHALL_REVISION"])]
    assert active["data"]["language_profile_ref"]["revision"] == migration["SHALL_REVISION"]
    profile = returned[("cube.language.profile", migration["SHALL_REVISION"])]["data"]
    assert profile["normative_modal"] == "shall"
    assert [x["rank"] for x in profile["standards_precedence"]] == [1, 2, 3]
    filtered_context = store.context("balancing-cube", max_designs=0, max_evidence=0,
        kinds=["design", "design_candidate", "simulation_run"], snapshot_ref=context["snapshot_ref"])
    filtered = by_ref(filtered_context["records"])
    assert ("cube.language.profile", migration["SHALL_REVISION"]) in filtered
