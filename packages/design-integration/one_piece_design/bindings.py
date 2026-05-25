"""Excel cell ↔ Python marker bindings — minimum SSOT integration unit."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

MARKER_PATTERN = re.compile(
    r"^(?P<prefix>#?\s*)SSOT:(?P<kind>PARAM|REQ):(?P<key>[A-Z0-9_-]+)\s*=\s*(?P<value>.+)$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class BindingSpec:
    excel_cell_ref: str
    python_marker: str
    design_parameter_key: str


def read_excel_cell(workbook_path: Path, cell_ref: str) -> str | float | bool:
    """Read a single cell value from an Excel workbook (e.g. 'Inputs!B4')."""
    if "!" in cell_ref:
        sheet_name, coord = cell_ref.split("!", 1)
    else:
        sheet_name, coord = None, cell_ref

    wb = load_workbook(workbook_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active
    value = ws[coord].value
    if value is None:
        return ""
    return value


def parse_python_markers(script_path: Path) -> dict[str, str]:
    """Return marker key → current literal value in the Python script."""
    text = script_path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for match in MARKER_PATTERN.finditer(text):
        key = match.group("key")
        result[key] = match.group("value").strip()
    return result


def _format_literal(raw: str | float | bool | int) -> str:
    if isinstance(raw, bool):
        return "True" if raw else "False"
    if isinstance(raw, (int, float)):
        if isinstance(raw, float) and raw != int(raw):
            return repr(raw)
        return str(int(raw))
    return repr(str(raw))


def _literals_equivalent(old: str, new: str) -> bool:
    """Best-effort compare of Python literal strings."""
    if old == new:
        return True
    try:
        return eval(old, {"__builtins__": {}}, {}) == eval(new, {"__builtins__": {}}, {})  # noqa: S307
    except Exception:
        return False


def sync_python_from_excel(
    workbook_path: Path,
    script_path: Path,
    bindings: list[BindingSpec],
) -> list[str]:
    """
    Propagate Excel cell values into Python SSOT markers.
    Returns list of human-readable change summaries.
    """
    text = script_path.read_text(encoding="utf-8")
    changes: list[str] = []

    for binding in bindings:
        raw = read_excel_cell(workbook_path, binding.excel_cell_ref)
        new_literal = _format_literal(raw)

        marker_key = binding.design_parameter_key
        pattern = re.compile(
            rf"^(\s*#?\s*SSOT:PARAM:{re.escape(marker_key)}\s*=\s*).+$",
            re.MULTILINE,
        )
        match = pattern.search(text)
        if not match:
            raise ValueError(
                f"Marker SSOT:PARAM:{marker_key} not found in {script_path}",
            )

        old = match.group(0).split("=", 1)[1].strip()
        if _literals_equivalent(old, new_literal):
            continue

        def replacer(m: re.Match[str]) -> str:
            return f"{m.group(1)}{new_literal}"

        text = pattern.sub(replacer, text, count=1)
        changes.append(
            f"{binding.excel_cell_ref} → SSOT:PARAM:{marker_key}: {old} → {new_literal}",
        )

    if changes:
        script_path.write_text(text, encoding="utf-8")

    return changes
