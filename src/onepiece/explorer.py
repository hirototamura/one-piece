"""Build a portable requirements explorer from canonical JSON, without a server."""
from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path

from ._explorer_claims import project_claims
from ._explorer_projection import project_model, record_by_ref
from .model import RecordError, canonical_bytes, digest
from .store import Store, current_records


def build_explorer(store: Store, output: str | Path, *, project_id: str = "balancing-cube",
                   model_id: str = "cube.system-model.active", revision: str | None = None,
                   engineering_agents_root: str | Path | None = None) -> dict:
    """Render exact snapshot references; review proposals remain browser-local.

    The current UI supports the Cube model. ECLSS comparison pages are optional
    and come only from an explicitly supplied Engineering Agents checkout.
    """
    output = Path(output).resolve()
    if output == store.path or output.is_relative_to(store.path):
        raise RecordError("Explorer output must be outside the canonical store")
    all_records = store.records(project_id)
    records = {(r["id"], r["revision"]): r for r in all_records}
    if revision:
        model = record_by_ref(records, {"id": model_id, "revision": revision})
    else:
        model = next((r for r in current_records(all_records) if r["id"] == model_id), None)
    if not model or model["kind"] != "system_model":
        raise RecordError("Select an existing system_model ID and revision")
    snapshot = record_by_ref(records, model["data"].get("simulation_snapshot_ref"))
    if not snapshot or snapshot["kind"] != "simulation_snapshot":
        raise RecordError("The model must reference an exact simulation snapshot")
    projection = project_model(records, model)
    for collection in ("groups", "requirements", "kdps", "products", "functions", "verification_cases"):
        for item in projection["balancing_cube"][collection]:
            data = records[(item["id"], item["revision"])]["data"]
            for field in ("statement", "description"):
                if data.get(field):
                    item.setdefault(field, data[field])
                translated = data.get("translations", {}).get("ja", {}).get(field)
                if translated:
                    item.setdefault(field + "_ja", translated)
    provenance = {
        "schema_version": 1, "project_id": project_id,
        "model_ref": {"id": model["id"], "revision": model["revision"]},
        "snapshot_ref": {"id": snapshot["id"], "revision": snapshot["revision"]},
        "model_sha256": digest(model), "snapshot_sha256": digest(snapshot),
        "record_set_sha256": digest(sorted(all_records, key=lambda r: (r["id"], r["revision"]))),
        "record_count": len(all_records),
        "projection_source": "canonical One-Piece JSON; generated browser copies are not authoritative",
        "proposal_scope": "Browser-local drafts and exports; no canonical writes or automatic approval",
        "sysml_scope": "One-Piece annotation/Dependency profile; use onepiece sysml for the standard API boundary",
        "prototype_source": {"repository": "requirements-explorer-site (local prototype)",
                             "commit": "d5bcc0c70be1f7b190fbe8368c90e5eec4ac75bf"},
        "comparison_sources": [],
    }
    if engineering_agents_root:
        try:
            import yaml
        except ImportError as exc:
            raise RecordError("Install the explorer extra to read optional Engineering Agents YAML") from exc
        scenario_root = Path(engineering_agents_root).resolve() / "src/scenario"
        for key, name in (("eclss", "ssos_eclss_loop"), ("scrubber", "scrubber_degradation")):
            source = scenario_root / name / "scenario.yaml"
            raw = source.read_bytes()
            projection[key] = {"scenario": yaml.safe_load(raw), "source": f"engineering_agents/src/scenario/{name}/scenario.yaml",
                               "formal_requirement_count": 0,
                               "scope_note": "Scenario contract; not a reviewed One-Piece requirement baseline."}
            provenance["comparison_sources"].append({"path": projection[key]["source"],
                                                     "sha256": hashlib.sha256(raw).hexdigest()})
            if key == "eclss":
                raw_agents = (source.parent / "agents.yaml").read_bytes()
                projection[key]["agents"] = yaml.safe_load(raw_agents)
                provenance["comparison_sources"].append({"path": f"engineering_agents/src/scenario/{name}/agents.yaml",
                                                         "sha256": hashlib.sha256(raw_agents).hexdigest()})
    projection["generated_from"] = provenance
    payloads = {
        "data/models.json": canonical_bytes(projection) + b"\n",
        "data/design-claims.json": canonical_bytes(project_claims(records, projection)) + b"\n",
        "provenance.json": canonical_bytes(provenance) + b"\n",
    }
    assets = files("onepiece").joinpath("explorer_assets")
    for name in ("index.html", "app.js", "styles.css"):
        payloads[name] = assets.joinpath(name).read_bytes()
    draft = json.loads(assets.joinpath("architecture_draft.json").read_bytes())
    if draft.get("base_model_ref") != provenance["model_ref"]:
        draft = {"id": "not-configured", "revision": "none", "status": "unavailable",
                 "functions": [], "components": [], "requirement_allocations": [],
                 "parameter_allocations": [], "open_questions": []}
    payloads["data/cube-architecture-draft.json"] = canonical_bytes(draft) + b"\n"
    manifest = {"schema_version": 1, "project_id": project_id, "model_ref": provenance["model_ref"],
                "files": [{"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
                          for name, raw in sorted(payloads.items())]}
    payloads["explorer-manifest.json"] = canonical_bytes(manifest) + b"\n"
    # All model/projection validation precedes writes. Only known generated files are replaced.
    for name, raw in payloads.items():
        path = output / name
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise RecordError("Explorer output must not traverse a symlink")
    for name, raw in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return {"path": str(output / "index.html"), "model_ref": provenance["model_ref"],
            "snapshot_ref": provenance["snapshot_ref"], "counts": projection["balancing_cube"]["counts"],
            "manifest_sha256": hashlib.sha256(payloads["explorer-manifest.json"]).hexdigest()}
