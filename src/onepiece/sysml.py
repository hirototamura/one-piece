"""OMG Systems Modeling API 1.0 read boundary for immutable engineering records.

This is an annotation/Dependency exchange profile, not a SysML language compiler.
A provider freezes its publication commits at construction; it never writes a store.
"""
from __future__ import annotations

import copy
import hashlib
import json
from functools import lru_cache
from http import HTTPStatus
from importlib.resources import files
from urllib.parse import parse_qs, urlencode
from uuid import UUID, NAMESPACE_URL, uuid5

from .model import RecordError, canonical_bytes, digest, validate_record

PROFILE = "onepiece-annotation-graph-1"
STANDARD = "https://www.omg.org/spec/SystemsModelingAPI/1.0/"
VENDOR = "standards/omg/SystemsModelingAPI/1.0"


def uid(*parts) -> str:
    return str(uuid5(NAMESPACE_URL, "https://onepiece.engineering/sysml/" + canonical_bytes(parts).decode()))


def identified(value: str) -> dict:
    return {"@id": value}


@lru_cache(maxsize=1)
def openapi() -> dict:
    root = files("onepiece").joinpath(VENDOR)
    manifest = json.loads(root.joinpath("sources.json").read_text())
    for document in manifest["documents"]:
        raw = root.joinpath(document["file"]).read_bytes()
        if len(raw) != document["size_bytes"] or hashlib.sha256(raw).hexdigest() != document["sha256"]:
            raise RecordError("OMG specification digest mismatch: " + document["file"])
    return json.loads(root.joinpath("OpenAPI.json").read_text())


def concrete_schema(name: str) -> dict:
    schema = openapi()["components"]["schemas"][name]
    # The OpenAPI inheritance union includes all concrete descendants. Select the
    # branch for the actual metaclass, retaining every official field constraint.
    return next((s for s in schema.get("anyOf", []) if s.get("properties", {}).get("@type", {}).get("const") == name), schema)


def _without_resource_ids(value):
    # OpenAPI component refs are document-relative, even inside Schema Objects
    # with absolute $id values. Embed the objects under one validation document.
    if isinstance(value, dict):
        result = {k: _without_resource_ids(v) for k, v in value.items() if k != "$id"}
        reference = result.get("$ref", "")
        if reference and not reference.startswith("#"):
            name = reference.rsplit("/", 1)[-1]
            if name not in openapi()["components"]["schemas"]:
                raise RecordError("Unmapped official schema reference: " + reference)
            result["$ref"] = "#/components/schemas/" + name
        return result
    if isinstance(value, list):
        return [_without_resource_ids(v) for v in value]
    return value


@lru_cache(maxsize=None)
def validator(name: str):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = _without_resource_ids(concrete_schema(name))
    schema["components"] = _validation_components()
    return Draft202012Validator(schema, format_checker=FormatChecker())


@lru_cache(maxsize=1)
def _validation_components():
    return _without_resource_ids(openapi()["components"])


def validate_payload(value: dict, name: str | None = None) -> None:
    from jsonschema import ValidationError
    try:
        validator(name or value["@type"]).validate(value)
    except (ValidationError, KeyError) as exc:
        raise RecordError("Invalid OMG payload: " + str(exc).split("\n")[0]) from exc


def element(name: str, id: str, label: str, **fields) -> dict:
    properties = concrete_schema(name)["properties"]
    result = {}
    for key in concrete_schema(name)["required"]:
        prop = properties[key]
        if prop.get("type") == "array":
            result[key] = []
        elif any(p.get("type") == "null" for p in prop.get("oneOf", [])):
            result[key] = None
        elif "const" in prop:
            result[key] = prop["const"]
        else:
            # Nonnullable references and strings must be explicitly supplied.
            if key not in fields and key not in {"@id"}:
                raise RecordError("Missing required OMG field: " + name + "." + key)
    result.update({"@id": id, "@type": name, "elementId": id,
                   "declaredName": label, "name": label, "qualifiedName": label,
                   "isImpliedIncluded": False, "isLibraryElement": False})
    result.update(fields)
    return result


def project_view(project_id: str, records: list[dict]) -> dict:
    records = sorted(copy.deepcopy(records), key=lambda r: (r["id"], r["revision"]))
    by_ref = {}
    for record in records:
        validate_record(record)
        key = record["id"], record["revision"]
        if record["project_id"] != project_id or key in by_ref:
            raise RecordError("Mixed project or duplicate record revision in API view")
        by_ref[key] = record
    project_uuid = uid("project", project_id)
    branch_uuid = uid("branch", project_id, PROFILE)
    commit_uuid = uid("commit", project_id, PROFILE, digest(records))
    created = max((r["created_at"] for r in records), default="1970-01-01T00:00:00Z")
    project = {"@id": project_uuid, "@type": "Project", "alias": [project_id],
               "created": min((r["created_at"] for r in records), default=created),
               "defaultBranch": identified(branch_uuid), "description": PROFILE, "name": project_id}
    commit = {"@id": commit_uuid, "@type": "Commit", "alias": [], "created": created,
              "description": "Frozen publication of all canonical record revisions; " + PROFILE,
              "name": digest(records), "owningProject": identified(project_uuid), "previousCommit": []}
    branch = {"@id": branch_uuid, "@type": "Branch", "alias": [], "created": project["created"],
              "deleted": None, "description": PROFILE, "head": identified(commit_uuid),
              "name": "publication", "owningProject": identified(project_uuid), "referencedCommit": identified(commit_uuid)}
    root_uuid = uid("root", project_id)
    elements = [element("Package", root_uuid, project_id)]
    for record in records:
        record_uuid = uid("record", project_id, record["id"], record["revision"])
        annotation_uuid = uid("annotation", record_uuid)
        label = record["id"] + "@" + record["revision"]
        elements.append(element("Comment", record_uuid, label,
                                aliasIds=[project_id + ":" + label, "onepiece-kind:" + record["kind"]],
                                body=canonical_bytes(record).decode(), locale=None,
                                annotatedElement=[identified(root_uuid)], annotation=[identified(annotation_uuid)]))
        elements.append(element("Annotation", annotation_uuid, "record annotation",
                                annotatedElement=identified(root_uuid), annotatingElement=identified(record_uuid),
                                source=[identified(record_uuid)], target=[identified(root_uuid)],
                                relatedElement=[identified(record_uuid), identified(root_uuid)], isImplied=False))
        for index, edge in enumerate(record["links"]):
            target_key = edge["target"]["id"], edge["target"]["revision"]
            if target_key not in by_ref:
                raise RecordError("Missing exact graph target: " + str(target_key))
            target = identified(uid("record", project_id, *target_key))
            source = identified(record_uuid)
            elements.append(element("Dependency", uid("edge", record_uuid, index, digest(edge)), edge["type"],
                                    aliasIds=["onepiece-relation:" + edge["type"]],
                                    source=[source], client=[source], target=[target], supplier=[target],
                                    relatedElement=[source, target], isImplied=False))
    elements.sort(key=lambda e: e["@id"])
    return {"profile": PROFILE, "standard": STANDARD, "project": project, "branch": branch,
            "commit": commit, "elements": elements}


def commit_request(view: dict) -> dict:
    return {"@type": "Commit", "name": view["commit"]["name"], "description": PROFILE,
            "change": [{"@type": "DataVersion", "identity": {"@id": e["@id"], "@type": "DataIdentity"},
                        "payload": copy.deepcopy(e)} for e in view["elements"]]}


def export_view(store, project_id: str) -> dict:
    records = store.records(project_id)
    if not records:
        raise RecordError("Project has no records: " + project_id)
    result = project_view(project_id, records)
    result["commit_request"] = commit_request(result)
    return result


def records_from_view(view: dict) -> list[dict]:
    if not isinstance(view, dict) or set(view) != {"profile", "standard", "project", "branch", "commit", "elements", "commit_request"}:
        raise RecordError("Malformed One-Piece API exchange envelope")
    if view.get("profile") != PROFILE or view.get("standard") != STANDARD:
        raise RecordError("Unsupported exchange profile; arbitrary SysML models are not One-Piece records")
    if not isinstance(view["elements"], list):
        raise RecordError("Exchange elements must be an array")
    for name, key in [("Project", "project"), ("Commit", "commit"), ("Branch", "branch")]:
        validate_payload(view[key], name)
    records = []
    for payload in view["elements"]:
        if not isinstance(payload, dict):
            raise RecordError("Exchange elements must be objects")
        validate_payload(payload)
        if payload["@type"] == "Comment":
            records.append(validate_record(json.loads(payload["body"])))
    if not records:
        raise RecordError("Exchange has no One-Piece record annotations")
    expected = project_view(view["project"]["name"], records)
    expected["commit_request"] = commit_request(expected)
    # Check exact graph, IDs, metadata, source revision links and POST payload.
    # An edited annotation must not silently disagree with its published graph.
    if canonical_bytes(expected) != canonical_bytes(view):
        raise RecordError("Exchange graph differs from its canonical record annotations")
    return records


class APIError(RecordError):
    def __init__(self, status: int, description: str):
        super().__init__(description)
        self.status = status


def _uuid(value, label):
    if not value:
        raise APIError(400, label + " is required")
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise APIError(400, label + " must be a UUID") from exc


class ReadProvider:
    """ProjectService Read and ElementNavigationService; immutable per instance."""
    def __init__(self, records):
        grouped = {}
        for record in records:
            grouped.setdefault(record["project_id"], []).append(record)
        self._views = {v["project"]["@id"]: v for key, rs in grouped.items() for v in [project_view(key, rs)]}
        self._elements = {key: {e["@id"]: e for e in v["elements"]} for key, v in self._views.items()}

    def get_projects(self):
        return copy.deepcopy(sorted((v["project"] for v in self._views.values()), key=lambda p: p["@id"]))

    def get_project_by_id(self, project_id):
        return copy.deepcopy(self._project(project_id)["project"])

    def _project(self, project_id):
        project_id = _uuid(project_id, "projectId")
        if project_id not in self._views:
            raise APIError(404, "Project does not exist")
        return self._views[project_id]

    def _view(self, project_id, commit_id):
        view = self._project(project_id)
        commit_id = _uuid(commit_id, "commitId")
        if view["commit"]["@id"] != commit_id:
            if any(v["commit"]["@id"] == commit_id for v in self._views.values()):
                raise APIError(400, "Commit does not belong to Project")
            raise APIError(404, "Commit does not exist")
        return view

    def get_elements(self, project_id, commit_id):
        return copy.deepcopy(self._view(project_id, commit_id)["elements"])

    def get_element_by_id(self, project_id, commit_id, element_id):
        project_id = self._view(project_id, commit_id)["project"]["@id"]
        element_id = _uuid(element_id, "elementId")
        if element_id not in self._elements[project_id]:
            raise APIError(404, "Element does not exist at Commit")
        return copy.deepcopy(self._elements[project_id][element_id])

    def get_root_elements(self, project_id, commit_id):
        return [e for e in self.get_elements(project_id, commit_id) if e["owner"] is None]

    def get_relationships_by_related_element(self, project_id, commit_id, element_id, direction="both"):
        element_id = self.get_element_by_id(project_id, commit_id, element_id)["@id"]
        if direction not in {"in", "out", "both"}:
            raise APIError(400, "direction must be in, out or both")
        return [e for e in self.get_elements(project_id, commit_id)
                if (direction in {"out", "both"} and identified(element_id) in e.get("source", []))
                or (direction in {"in", "both"} and identified(element_id) in e.get("target", []))]

    def dispatch(self, path: str, query: dict):
        parts = path.strip("/").split("/")
        if parts == ["projects"]:
            return self.get_projects()
        if len(parts) < 2 or parts[0] != "projects":
            raise APIError(404, "Endpoint does not exist")
        pid = parts[1]
        view = self._project(pid)
        pid = view["project"]["@id"]
        if len(parts) == 2:
            return self.get_project_by_id(pid)
        # Discovery helpers are standard endpoints, but do not implement the
        # complete ProjectDataVersioningService Read conformance point.
        if parts[2:] == ["branches"]:
            return [copy.deepcopy(view["branch"])]
        if parts[2:] == ["branches", view["branch"]["@id"]]:
            return copy.deepcopy(view["branch"])
        if parts[2:] == ["commits"]:
            return [copy.deepcopy(view["commit"])]
        if len(parts) < 4 or parts[2] != "commits":
            raise APIError(404, "Endpoint does not exist")
        cid = parts[3]
        self._view(pid, cid)
        if len(parts) == 4:
            return copy.deepcopy(view["commit"])
        if parts[4:] == ["elements"]:
            return self.get_elements(pid, cid)
        if parts[4:] == ["roots"]:
            return self.get_root_elements(pid, cid)
        if len(parts) == 6 and parts[4] == "elements":
            return self.get_element_by_id(pid, cid, parts[5])
        if len(parts) == 7 and parts[4] == "elements" and parts[6] == "relationships":
            return self.get_relationships_by_related_element(pid, cid, parts[5], query.get("direction", "both"))
        raise APIError(404, "Endpoint does not exist")

    def __call__(self, environ, start_response):
        headers = [("Content-Type", "application/json")]
        try:
            if environ.get("REQUEST_METHOD") != "GET":
                raise APIError(405, "Read provider supports GET only")
            query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
            if any(len(v) != 1 for v in query.values()):
                raise APIError(400, "Query parameters must not repeat")
            query = {k: v[0] for k, v in query.items()}
            if query.get("excludeUsed", "false") not in {"true", "false"}:
                raise APIError(400, "excludeUsed must be true or false")
            # There are no ProjectUsages in this profile; excludeUsed is a no-op.
            value = self.dispatch(environ.get("PATH_INFO", ""), query)
            if isinstance(value, list):
                value, links = paginate(value, query, environ)
                if links:
                    headers.append(("Link", links))
            status = 200
        except APIError as exc:
            status, value = exc.status, {"@type": "Error", "description": str(exc)}
            if status == 405:
                headers.append(("Allow", "GET"))
        body = canonical_bytes(value)
        headers.append(("Content-Length", str(len(body))))
        start_response(str(status) + " " + HTTPStatus(status).phrase, headers)
        return [body]


def paginate(values: list, query: dict, environ: dict):
    try:
        size = int(query.get("page[size]", "100"))
    except ValueError as exc:
        raise APIError(400, "page[size] must be an integer") from exc
    if not 1 <= size <= 1000 or ("page[before]" in query and "page[after]" in query):
        raise APIError(400, "Invalid pagination parameters")
    ids = [v["@id"] for v in values]
    start, end = 0, len(values)
    for key in ["page[after]", "page[before]"]:
        if key in query:
            if query[key] not in ids:
                raise APIError(400, "Cursor does not belong to this collection")
            if key == "page[after]":
                start = ids.index(query[key]) + 1
            else:
                end = ids.index(query[key])
                start = max(0, end - size)
    page = values[start:min(end, start + size)]
    base = environ.get("wsgi.url_scheme", "http") + "://" + environ.get("HTTP_HOST", "localhost")
    base += environ.get("SCRIPT_NAME", "") + environ.get("PATH_INFO", "")
    links = []
    for key, cursor, rel, condition in [("page[before]", page[0]["@id"] if page else "", "prev", start > 0),
                                        ("page[after]", page[-1]["@id"] if page else "", "next", start + len(page) < len(values))]:
        if page and condition:
            params = {k: v for k, v in query.items() if k not in {"page[after]", "page[before]"}}
            params.update({key: cursor, "page[size]": str(size)})
            links.append("<" + base + "?" + urlencode(params) + '>; rel="' + rel + '"')
    return page, ", ".join(links)
