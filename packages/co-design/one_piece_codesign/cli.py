"""CLI entrypoint for autonomous co-design runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .orchestrator import DEFAULT_SCRIPT, run_codesign


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the one-piece autonomous co-design loop against a program JSON file.",
    )
    parser.add_argument("--program", type=Path, required=True, help="Input program JSON")
    parser.add_argument("--output", type=Path, required=True, help="Where to write the updated program JSON")
    parser.add_argument("--db", type=Path, help="Optional SQLite file for run history")
    parser.add_argument("--goal", type=str, help="Override natural-language goal text")
    parser.add_argument("--max-iter", type=int, help="Maximum number of co-design iterations")
    parser.add_argument(
        "--script",
        type=Path,
        default=DEFAULT_SCRIPT,
        help="Thermal analysis stand-in script",
    )
    args = parser.parse_args()

    program = json.loads(args.program.read_text(encoding="utf-8"))
    updated = run_codesign(
        program,
        goal_override=args.goal,
        max_iterations=args.max_iter,
        script_path=args.script,
        db_path=args.db,
    )
    args.output.write_text(json.dumps(updated, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote updated program JSON to {args.output}")


if __name__ == "__main__":
    main()
