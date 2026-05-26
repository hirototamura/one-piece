"""CLI: sync Excel → Python and re-run design script."""

from __future__ import annotations

import argparse
from pathlib import Path

from one_piece_design.bindings import BindingSpec, sync_python_from_excel
from one_piece_design.runner import run_python_script


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Excel cells into Python SSOT markers and re-run script.",
    )
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument(
        "--bind",
        action="append",
        default=[],
        metavar="CELL:MARKER:KEY[:VAR]",
        help="Binding e.g. Inputs!B4:P-VBUS:P-VBUS:VBUS",
    )
    parser.add_argument("--no-run", action="store_true", help="Sync only, do not execute")
    args = parser.parse_args()

    bindings: list[BindingSpec] = []
    for raw in args.bind:
        parts = raw.split(":")
        if len(parts) not in (3, 4):
            raise SystemExit(f"Invalid --bind format: {raw}")
        cell, marker, key = parts[0], parts[1], parts[2]
        assignment = parts[3] if len(parts) == 4 else None
        bindings.append(
            BindingSpec(
                excel_cell_ref=cell,
                python_marker=f"SSOT:PARAM:{marker}",
                design_parameter_key=key,
                python_assignment_name=assignment,
            ),
        )

    changes = sync_python_from_excel(args.workbook, args.script, bindings)
    if changes:
        print("SSOT sync (logic automation):")
        for line in changes:
            print(f"  • {line}")
    else:
        print("No cell changes detected.")

    if not args.no_run:
        result = run_python_script(args.script)
        if result.stdout:
            print(result.stdout)
        if not result.success:
            print(result.stderr or f"Exit code {result.exit_code}", file=__import__("sys").stderr)
            raise SystemExit(result.exit_code)


if __name__ == "__main__":
    main()
