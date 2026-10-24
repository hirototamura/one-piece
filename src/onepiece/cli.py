"""Local CLI. Import and report operations never establish engineering baselines."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from .model import RecordError, canonical_bytes
from .store import Store


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="onepiece", description="Versioned system model and engineering evidence")
    p.add_argument("--store", default=".onepiece", help="local JSON record store (default .onepiece)")
    sub = p.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import", help="atomically import records or a SHA-256-checked ZIP bundle")
    imp.add_argument("source", type=Path)
    imp.add_argument("--artifacts-root", type=Path)
    imp.add_argument("--sha256", help="required for ZIP imports")
    ctx = sub.add_parser("context", help="export agent context retaining all requirements and parameter units")
    ctx.add_argument("--project", required=True)
    ctx.add_argument("--product-node")
    ctx.add_argument("--kind", action="append", dest="kinds")
    ctx.add_argument("--max-designs", type=int, default=20)
    ctx.add_argument("--max-evidence", type=int, default=50)
    ctx.add_argument("--output", type=Path)
    ctx.add_argument("--snapshot-id")
    ctx.add_argument("--snapshot-revision")
    check = sub.add_parser("check", help="verify canonical commits, references, artifact hashes and claim scopes")
    check.add_argument("--project")
    bundle = sub.add_parser("bundle", help="create a portable content-addressed evidence ZIP")
    bundle.add_argument("output", type=Path)
    bundle.add_argument("--project")
    fetch = sub.add_parser("fetch", help="fetch and atomically import a bundle with a mandatory expected hash")
    fetch.add_argument("url")
    fetch.add_argument("--sha256", required=True)
    report = sub.add_parser("report", help="render the system graph and evidence from canonical records")
    report.add_argument("output", type=Path)
    report.add_argument("--project")
    explorer = sub.add_parser("explorer", help="build the requirements explorer from a pinned canonical model")
    explorer_ops = explorer.add_subparsers(dest="explorer_command", required=True)
    explorer_build = explorer_ops.add_parser("build", help="write a portable static view; proposals remain browser-local")
    explorer_build.add_argument("output", type=Path)
    explorer_build.add_argument("--project", default="balancing-cube")
    explorer_build.add_argument("--model-id", default="cube.system-model.active")
    explorer_build.add_argument("--model-revision", help="exact revision; omit to select the latest source model")
    explorer_build.add_argument("--engineering-agents-root", type=Path, help="optional ECLSS/scrubber comparison checkout")
    datasets = sub.add_parser("datasets", help="catalog and retrieve immutable run evidence from private GitHub Releases")
    dataset_ops = datasets.add_subparsers(dest="dataset_command", required=True)
    pack = dataset_ops.add_parser("pack", help="prepare an indexed archive collection; never publishes or deletes inputs")
    pack.add_argument("source", type=Path)
    pack.add_argument("output", type=Path)
    pack.add_argument("--repository", required=True)
    pack.add_argument("--release", required=True)
    pack.add_argument("--catalog-id", required=True)
    listing = dataset_ops.add_parser("list", help="search the local catalog without downloading data")
    listing.add_argument("catalog", type=Path)
    listing.add_argument("--query", default="")
    for operation in ("fetch", "verify"):
        ds = dataset_ops.add_parser(operation, help="retrieve or check selected dataset files with mandatory manifest hashes")
        ds.add_argument("catalog", type=Path)
        ds.add_argument("--id", action="append", required=operation == "fetch", dest="ids")
        ds.add_argument("--destination", type=Path, required=True)
        if operation == "fetch":
            ds.add_argument("--cache", type=Path, default=Path.home() / ".cache/onepiece/datasets")
            ds.add_argument("--assets-dir", type=Path, help="read already-downloaded assets for offline restoration")
            ds.add_argument("--path", dest="path_prefix", help="restore only this logical path or directory prefix")
    baseline = sub.add_parser("baseline", help="record a separate, explicit human configuration-baseline action")
    baseline.add_argument("--project", required=True)
    baseline.add_argument("--id", required=True)
    baseline.add_argument("--revision", default="1")
    baseline.add_argument("--human-actor", required=True, help="human identity; never use for automatic agent decisions")
    baseline.add_argument("--reason", required=True)
    sysml = sub.add_parser("sysml", help="OMG Systems Modeling API 1.0 read and exchange boundary")
    operations = sysml.add_subparsers(dest="sysml_command", required=True)
    export = operations.add_parser("export", help="export a frozen graph and a standard CommitRequest")
    export.add_argument("output", type=Path)
    export.add_argument("--project", required=True)
    validate = operations.add_parser("check", help="check official schemas and exact annotation/graph consistency")
    validate.add_argument("source", type=Path)
    restore = operations.add_parser("import", help="restore this adapter's exchange profile; artifacts still require verified bytes")
    restore.add_argument("source", type=Path)
    restore.add_argument("--sha256", required=True)
    restore.add_argument("--artifacts-root", type=Path)
    serve = operations.add_parser("serve", help="explicitly start a local read-only API; never runs in the background")
    serve.add_argument("--port", type=int, default=9000)
    sub.add_parser("reindex", help="rebuild disposable SQLite from canonical versioned JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "datasets":
            from .datasets import fetch_datasets, load_catalog, pack_datasets, select_datasets, verify_datasets
            if args.dataset_command == "pack":
                result = pack_datasets(args.source, args.output, repository=args.repository,
                                       release=args.release, catalog_id=args.catalog_id)
            else:
                catalog = load_catalog(args.catalog)
                if args.dataset_command == "list":
                    result = {"catalog_id": catalog["id"], "visibility": catalog.get("visibility"),
                              "datasets": [{"id": d["id"], "tags": d.get("tags", []), "files": len(d["files"]),
                                            "download_bytes": d["size_bytes"], "sha256": d["sha256"]}
                                           for d in select_datasets(catalog, query=args.query)]}
                elif args.dataset_command == "verify":
                    result = verify_datasets(catalog, args.destination, ids=args.ids)
                else:
                    result = fetch_datasets(catalog, args.destination, ids=args.ids, cache=args.cache,
                                            assets_dir=args.assets_dir, path_prefix=args.path_prefix)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("ok", True) else 1
        store = Store(args.store)
        if args.command == "import":
            if args.source.suffix.lower() == ".zip":
                if not args.sha256:
                    raise RecordError("ZIP imports require --sha256")
                result = store.import_bundle(args.source, expected_sha256=args.sha256)
            else:
                value = json.loads(args.source.read_text())
                records = value.get("records") if isinstance(value, dict) and "records" in value else [value] if isinstance(value, dict) else value
                if not isinstance(records, list):
                    raise RecordError("Import JSON must be an envelope, an array, or an object containing records")
                result = store.import_records(records, artifacts_root=args.artifacts_root)
        elif args.command == "context":
            if bool(args.snapshot_id) != bool(args.snapshot_revision):
                raise RecordError("Pass both --snapshot-id and --snapshot-revision")
            snapshot = {"id": args.snapshot_id, "revision": args.snapshot_revision} if args.snapshot_id else None
            result = store.context(args.project, product_node=args.product_node, kinds=args.kinds, max_designs=args.max_designs, max_evidence=args.max_evidence, snapshot_ref=snapshot)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_bytes(canonical_bytes(result) + b"\n")
                result = {"path": str(args.output.resolve()), **result["counts"]}
        elif args.command == "check":
            result = store.check(args.project)
        elif args.command == "bundle":
            result = store.bundle(args.output, args.project)
        elif args.command == "fetch":
            result = store.fetch(args.url, expected_sha256=args.sha256)
        elif args.command == "report":
            from .report import report
            result = {"path": str(report(store, args.output, project_id=args.project))}
        elif args.command == "explorer":
            from .explorer import build_explorer
            result = build_explorer(store, args.output, project_id=args.project, model_id=args.model_id,
                                    revision=args.model_revision, engineering_agents_root=args.engineering_agents_root)
        elif args.command == "baseline":
            result = store.baseline(args.project, id=args.id, revision=args.revision, actor={"type": "human", "id": args.human_actor}, reason=args.reason)
        elif args.command == "sysml":
            from .sysml import ReadProvider, export_view, records_from_view
            if args.sysml_command == "export":
                view = export_view(store, args.project)
                # Validate before publication, including round-trip graph equality.
                records_from_view(view)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                payload = canonical_bytes(view) + b"\n"
                args.output.write_bytes(payload)
                result = {"path": str(args.output.resolve()), "sha256": hashlib.sha256(payload).hexdigest(),
                          "project_id": view["project"]["@id"], "commit_id": view["commit"]["@id"],
                          "records": sum(e["@type"] == "Comment" for e in view["elements"]), "elements": len(view["elements"])}
            elif args.sysml_command in {"check", "import"}:
                raw = args.source.read_bytes()
                if args.sysml_command == "import":
                    if hashlib.sha256(raw).hexdigest() != args.sha256:
                        raise RecordError("Exchange SHA-256 mismatch")
                records = records_from_view(json.loads(raw))
                result = store.import_records(records, artifacts_root=args.artifacts_root) if args.sysml_command == "import" else {"ok": True, "records": len(records)}
            else:
                from wsgiref.simple_server import make_server
                if not 1 <= args.port <= 65535:
                    raise RecordError("Port must be between 1 and 65535")
                with make_server("127.0.0.1", args.port, ReadProvider(store.records())) as server:
                    print(json.dumps({"url": f"http://127.0.0.1:{args.port}/projects", "read_only": True}), flush=True)
                    server.serve_forever()
                return 0
        elif args.command == "reindex":
            result = store.rebuild_index()
        else:
            raise RecordError("Unknown command")
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if args.command != "check" or result["ok"] else 1
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
