"""CLI entrypoint for reverse-ingestion connectors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ssos import ingest_ssos_repo


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a seed SSOT graph from external sources.")
    parser.add_argument("--source", choices=["ssos"], required=True)
    parser.add_argument("--path", type=Path, required=True, help="Path to the source repository")
    parser.add_argument("--output", type=Path, required=True, help="Where to write graph JSON")
    args = parser.parse_args()

    if args.source != "ssos":
        raise SystemExit(f"Unsupported source: {args.source}")

    graph = ingest_ssos_repo(args.path)
    args.output.write_text(json.dumps(graph, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"Wrote {len(graph['elements'])} elements and "
        f"{len(graph['interfaceControlDocuments'])} ICDs to {args.output}"
    )


if __name__ == "__main__":
    main()
