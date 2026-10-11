"""Selected OMG Annex A read-service cases and migration contract tests."""
import copy
import hashlib
import json
from urllib.parse import urlsplit
from uuid import uuid4
from wsgiref.util import setup_testing_defaults

import pytest

from onepiece import Store, RecordError, make_record, ref
from onepiece.cli import main
from onepiece.sysml import (APIError, ReadProvider, commit_request, export_view,
                            openapi, project_view, records_from_view, uid, validate_payload)


def record(id, kind, project_id="cube", **kwargs):
    return make_record(id=id, kind=kind, project_id=project_id, created_at="2026-10-11T00:00:00Z", **kwargs)


@pytest.fixture
def records():
    product = record("P", "product")
    parameter = record("K", "kdp", data={"value": 0.15, "unit": "m", "uncertainty": None})
    mission = record("R", "requirement", data={"text": "The cube shall hold for 30 s.", "physical_verified": None})
    updated = {**copy.deepcopy(mission), "revision": "2", "data": {**mission["data"], "approval_state": "draft"}}
    child = record("R2", "requirement", links=[{"type": "derive", "target": ref(mission)},
                                             {"type": "allocate", "target": ref(product)},
                                             {"type": "constrain", "target": ref(parameter)}])
    design = record("D", "design", links=[{"type": "satisfy", "target": ref(child)}])
    case = record("T", "test_case", data={"duration_s": 6})
    run = record("E", "evaluation", data={"physical_verified": None, "numeric_cpu_verified": True},
                 links=[{"type": "verify", "target": ref(case), "note": "Numerical development evidence only"}])
    other = record("OTHER", "requirement", project_id="other")
    return [product, parameter, mission, updated, child, design, case, run, other]


@pytest.fixture
def api(records):
    return ReadProvider(records)


def identifiers(api, project="cube"):
    pid = uid("project", project)
    commit = api.dispatch(f"/projects/{pid}/commits", {})[0]["@id"]
    return pid, commit


def request(api, path, method="GET"):
    url = urlsplit(path)
    environ = {}
    setup_testing_defaults(environ)
    environ.update(REQUEST_METHOD=method, PATH_INFO=url.path, QUERY_STRING=url.query, HTTP_HOST="localhost:9000")
    response = {}
    def start(status, headers):
        response.update(status=int(status.split()[0]), headers=dict(headers))
    response["body"] = json.loads(b"".join(api(environ, start)))
    if response["status"] != 200:
        validate_payload(response["body"], "Error")
    return response


def test_official_documents_and_schema_payloads(api):
    """Official concrete types, UUID formats, and CommitRequest POST body."""
    assert openapi()["info"]["version"] == "1.0"
    for project in api.get_projects():
        validate_payload(project)
        pid, cid = identifiers(api, project["name"])
        for key in ["branches", "commits"]:
            for value in api.dispatch(f"/projects/{pid}/{key}", {}):
                validate_payload(value)
        for e in api.get_elements(pid, cid):
            validate_payload(e)
            validate_payload(e, "Data")
        view = api._views[pid]
        validate_payload(commit_request(view), "CommitRequest")
    payload = api.get_elements(*identifiers(api))[0]
    payload["@id"] = "invalid"
    with pytest.raises(RecordError, match="Invalid OMG"):
        validate_payload(payload)


def test_PIM_PS_002_003_004(api):
    projects = api.get_projects()
    assert {p["name"] for p in projects} == {"cube", "other"}
    for p in projects:
        assert api.get_project_by_id(p["@id"]) == p
    with pytest.raises(APIError) as error:
        api.get_project_by_id(str(uuid4()))
    assert error.value.status == 404


def test_PIM_EN_001_002_003_and_roots(api, records):
    pid, cid = identifiers(api)
    elements = api.get_elements(pid, cid)
    assert len(elements) == 1 + 2 * 8 + 5
    assert len({e["@id"] for e in elements}) == len(elements)
    for e in elements:
        assert api.get_element_by_id(pid, cid, e["@id"]) == e
    assert api.get_root_elements(pid, cid) == [e for e in elements if e["owner"] is None]
    with pytest.raises(APIError) as error:
        api.get_element_by_id(pid, cid, str(uuid4()))
    assert error.value.status == 404
    # A revision-pinned derive edge must keep R@1, even when R@2 exists.
    edge = next(e for e in elements if e["@type"] == "Dependency" and e["name"] == "derive")
    assert edge["target"] == [{"@id": uid("record", "cube", "R", "1")}]


@pytest.mark.parametrize("direction,keys", [("out", ["source"]), ("in", ["target"]), ("both", ["source", "target"])])
def test_PIM_EN_004_005_relationship_directions(api, direction, keys):
    pid, cid = identifiers(api)
    elements = api.get_elements(pid, cid)
    for element in elements:
        expected = [e for e in elements if any({"@id": element["@id"]} in e.get(k, []) for k in keys)]
        assert api.get_relationships_by_related_element(pid, cid, element["@id"], direction) == expected


INVALID_INPUTS = [
    ("project", None, 400), ("commit", None, 400),
    ("project", str(uuid4()), 404), ("commit", str(uuid4()), 404),
    ("commit", "foreign", 400), ("element", None, 400),
]


@pytest.mark.parametrize("field,value,status,operation", [
    (*case, operation) for case in INVALID_INPUTS
    for operation in ["get_element_by_id", "get_elements", "get_root_elements", "get_relationships_by_related_element"]
    if not (case[0] == "element" and operation in {"get_elements", "get_root_elements"})
])
def test_PIM_CC_001_to_005_and_007(api, field, value, status, operation):
    pid, cid = identifiers(api)
    if value == "foreign":
        value = identifiers(api, "other")[1]
    args = {"project": pid, "commit": cid, "element": uid("record", "cube", "R", "1")}
    args[field] = value
    with pytest.raises(APIError) as error:
        call_args = [args["project"], args["commit"]]
        if operation in {"get_element_by_id", "get_relationships_by_related_element"}:
            call_args.append(args["element"])
        getattr(api, operation)(*call_args)
    assert error.value.status == status


def test_required_project_uuid_empty_provider_and_uuid_case(api):
    with pytest.raises(APIError) as error:
        api.get_project_by_id(None)
    assert error.value.status == 400
    assert request(ReadProvider([]), "/projects")["body"] == []
    pid, cid = identifiers(api)
    eid = uid("record", "cube", "R", "1")
    assert api.get_project_by_id(pid.upper()) == api.get_project_by_id(pid)
    assert api.get_element_by_id(pid.upper(), cid.upper(), eid.upper()) == api.get_element_by_id(pid, cid, eid)
    assert api.get_relationships_by_related_element(pid.upper(), cid.upper(), eid.upper()) == api.get_relationships_by_related_element(pid, cid, eid)


def test_rest_contract_pagination_and_discovery(api):
    projects = request(api, "/projects")["body"]
    project = next(p for p in projects if p["name"] == "cube")
    pid = project["@id"]
    branch = request(api, f"/projects/{pid}/branches/{project['defaultBranch']['@id']}")["body"]
    cid = branch["head"]["@id"]
    assert request(api, f"/projects/{pid}/commits/{cid}")["status"] == 200
    path = f"/projects/{pid}/commits/{cid}/elements"
    result = request(api, path + "?page[size]=3")
    elements = list(result["body"])
    second = None
    while 'rel="next"' in result["headers"].get("Link", ""):
        next_url = next(link.split(">")[0][1:] for link in result["headers"]["Link"].split(", ") if 'rel="next"' in link)
        result = request(api, next_url)
        if second is None:
            second = result
        elements.extend(result["body"])
    assert elements == api.get_elements(pid, cid)
    previous_url = next(link.split(">")[0][1:] for link in second["headers"]["Link"].split(", ") if 'rel="prev"' in link)
    assert request(api, previous_url)["body"] == elements[:3]
    assert request(api, f"/projects/{pid}/commits/{cid}/roots")["body"] == api.get_root_elements(pid, cid)
    related = uid("record", "cube", "R", "1")
    assert request(api, path + f"/{related}/relationships?direction=in")["body"] == api.get_relationships_by_related_element(pid, cid, related, "in")
    assert request(api, path + "?excludeUsed=true")["body"] == elements


@pytest.mark.parametrize("suffix,status", [
    ("?page[size]=0", 400), ("?page[size]=oops", 400), ("?page[size]=1001", 400),
    ("?page[after]=missing", 400), ("?page[before]=x&page[after]=y", 400),
    ("?page[size]=2&page[size]=3", 400), ("?excludeUsed=maybe", 400),
    ("/missing", 400),
])
def test_rest_errors(api, suffix, status):
    pid, cid = identifiers(api)
    response = request(api, f"/projects/{pid}/commits/{cid}/elements" + suffix)
    assert response["status"] == status


def test_rest_unknown_routes_invalid_direction_and_write_denial(api):
    pid, cid = identifiers(api)
    assert request(api, "/absent")["status"] == 404
    assert request(api, f"/projects/{uuid4()}")["status"] == 404
    related = uid("record", "cube", "R", "1")
    assert request(api, f"/projects/{pid}/commits/{cid}/elements/{related}/relationships?direction=sideways")["status"] == 400
    before = api.get_elements(pid, cid)
    response = request(api, "/projects", "POST")
    assert response["status"] == 405 and response["headers"]["Allow"] == "GET"
    assert api.get_elements(pid, cid) == before


def test_publication_commit_is_frozen_and_values_are_not_mutable(api, records):
    pid, cid = identifiers(api)
    elements = api.get_elements(pid, cid)
    elements[0]["aliasIds"].append("mutate")
    assert elements != api.get_elements(pid, cid)
    new_records = copy.deepcopy(records)
    new_records.append(record("NEW", "requirement"))
    newer = ReadProvider(new_records)
    assert identifiers(newer)[1] != cid
    assert identifiers(api)[1] == cid
    assert uid("record", "cube", "R", "1") in {e["@id"] for e in newer.get_elements(*identifiers(newer))}


def test_exchange_round_trip_preserves_values_approval_and_exact_revisions(tmp_path, records):
    store = Store(tmp_path / "original")
    store.import_records(records)
    view = export_view(store, "cube")
    decoded = records_from_view(view)
    restored = Store(tmp_path / "restored")
    assert restored.import_records(decoded)["imported"] == 8
    assert restored.import_records(decoded)["unchanged"] == 8
    assert restored.records() == store.records("cube")
    assert restored.check()["ok"]
    assert next(r for r in decoded if r["id"] == "K")["data"]["unit"] == "m"
    assert next(r for r in decoded if r["id"] == "E")["data"]["physical_verified"] is None
    tampered = copy.deepcopy(view)
    edge = next(e for e in tampered["elements"] if e["@type"] == "Dependency")
    edge["declaredName"] = "fake"
    with pytest.raises(RecordError, match="differs"):
        records_from_view(tampered)
    missing = copy.deepcopy(view)
    missing["elements"].pop()
    with pytest.raises(RecordError):
        records_from_view(missing)
    with pytest.raises(RecordError):
        records_from_view({"elements": []})


def test_cli_export_check_import_requires_hash_and_artifact_bytes(tmp_path, records, capsys):
    original = tmp_path / "original"
    store = Store(original)
    store.import_records(records)
    output = tmp_path / "exchange.json"
    assert main(["--store", str(original), "sysml", "export", str(output), "--project", "cube"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert main(["--store", str(original), "sysml", "check", str(output)]) == 0
    restored = tmp_path / "restored"
    assert main(["--store", str(restored), "sysml", "import", str(output), "--sha256", "0" * 64]) == 2
    assert Store(restored).records() == []
    assert main(["--store", str(restored), "sysml", "import", str(output), "--sha256", result["sha256"]]) == 0
    assert Store(restored).records() == store.records("cube")
    artifact_record = record("WITH-BYTES", "evidence", artifacts=[{"path": "test.txt", "sha256": hashlib.sha256(b"proof").hexdigest()}])
    view = project_view("cube", [artifact_record])
    view["commit_request"] = commit_request(view)
    with pytest.raises(RecordError):
        Store(tmp_path / "no-artifacts").import_records(records_from_view(view))
