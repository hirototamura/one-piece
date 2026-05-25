"""Execute Python design scripts after SSOT sync (logic automation)."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int


def run_python_script(script_path: Path, *, timeout_seconds: int = 60) -> RunResult:
    """Run a design script deterministically; no AI involved."""
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return RunResult(
        success=proc.returncode == 0,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        exit_code=proc.returncode,
    )
