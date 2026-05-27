"""Autonomous co-design loop orchestrator."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agents.design import propose_parameter_updates
from .agents.requirements import evaluate_requirements
from .persistence import connect_db, store_graph_snapshot, store_iteration, store_run

REPO_ROOT = Path(__file__).resolve().parents[3]
DESIGN_INTEGRATION_ROOT = REPO_ROOT / "packages" / "design-integration"
DEFAULT_SCRIPT = DESIGN_INTEGRATION_ROOT / "examples" / "thermal_rejection.py"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_repo_imports() -> None:
    if str(DESIGN_INTEGRATION_ROOT) not in sys.path:
        sys.path.insert(0, str(DESIGN_INTEGRATION_ROOT))


def _parameter_map(program: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in program["model"]["designParameters"]:
        if isinstance(item["value"], (int, float)):
            result[item["key"]] = float(item["value"])
    return result


def _apply_parameter_values(program: dict[str, Any], values: dict[str, float]) -> None:
    for item in program["model"]["designParameters"]:
        key = item["key"]
        if key in values:
            item["value"] = values[key]


def _parse_metrics(stdout: str) -> dict[str, float]:
    for line in stdout.splitlines():
        if line.startswith("METRICS:"):
            payload = json.loads(line.removeprefix("METRICS:"))
            return {key: float(value) for key, value in payload.items()}
    raise ValueError("Simulation output did not contain a METRICS line.")


def _run_simulation(script_path: Path, parameters: dict[str, float]) -> tuple[dict[str, float], str]:
    _ensure_repo_imports()
    from one_piece_design.bindings import ValueBindingSpec, sync_python_from_values
    from one_piece_design.runner import run_python_script

    sync_python_from_values(
        script_path,
        [
            ValueBindingSpec("P-RAD-AREA", parameters["P-RAD-AREA"], "RADIATOR_AREA_M2"),
            ValueBindingSpec("P-RAD-MASS", parameters["P-RAD-MASS"], "RADIATOR_MASS_KG"),
            ValueBindingSpec("P-HEAT-LOAD", parameters["P-HEAT-LOAD"], "HEAT_LOAD_KW"),
            ValueBindingSpec(
                "P-COOLANT-FLOW",
                parameters["P-COOLANT-FLOW"],
                "COOLANT_FLOW_KGPS",
            ),
        ],
    )
    result = run_python_script(script_path)
    if not result.success:
        raise RuntimeError(result.stderr or f"Simulation failed with exit code {result.exit_code}")
    return _parse_metrics(result.stdout), result.stdout.strip()


def _metric_rows(metrics: dict[str, float]) -> list[dict[str, Any]]:
    return [
        {
            "key": "radiatorMassKg",
            "label": "Radiator mass",
            "value": round(metrics["radiatorMassKg"], 3),
            "unit": "kg",
            "status": "met" if metrics["radiatorMassKg"] <= 15.7 else "improved",
        },
        {
            "key": "rejectionEfficiency",
            "label": "Rejection efficiency",
            "value": round(metrics["rejectionEfficiency"], 3),
            "status": "met" if metrics["rejectionEfficiency"] >= 0.94 else "unmet",
        },
        {
            "key": "heatBalanceMarginKw",
            "label": "Heat balance margin",
            "value": round(metrics["heatBalanceMarginKw"], 3),
            "unit": "kW",
            "status": "met" if metrics["heatBalanceMarginKw"] >= 0 else "unmet",
        },
    ]


def _integration_run(run_id: str, stdout: str, metrics: dict[str, float], at: str) -> dict[str, Any]:
    return {
        "id": run_id,
        "startedAt": at,
        "completedAt": at,
        "status": "success",
        "triggeredBy": "logic_automation",
        "bindingIds": [],
        "outputSummary": stdout.splitlines()[0],
        "metrics": {
            "radiatorMassKg": round(metrics["radiatorMassKg"], 3),
            "rejectionEfficiency": round(metrics["rejectionEfficiency"], 3),
            "heatBalanceMarginKw": round(metrics["heatBalanceMarginKw"], 3),
        },
        "evidenceRef": run_id.replace("run-", "AN-"),
    }


def _provenance_records(
    iteration_id: str,
    mutations: list[dict[str, str]],
    occurred_at: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, mutation in enumerate(mutations):
        records.append(
            {
                "id": f"prov-{iteration_id}-{index}",
                "occurredAt": occurred_at,
                "actorKind": "ai_agent",
                "actorLabel": "Co-design design agent",
                "nodeKind": mutation["nodeKind"],
                "nodeId": mutation["nodeId"],
                "nodeKey": mutation["nodeKey"],
                "fieldPath": mutation["fieldPath"],
                "previousValue": mutation.get("previousValue"),
                "newValue": mutation["newValue"],
                "criticalityTier": mutation["criticalityTier"],
                "aiTouchInHumanDomain": True,
                "rationale": mutation.get("rationale"),
            }
        )
    return records


def _update_matrix(
    program: dict[str, Any],
    checks: list[dict[str, str]],
    evidence_ref: str | None,
) -> None:
    for cell in program["matrixCells"]:
        for check in checks:
            if cell["requirementId"] != check["requirementId"] or cell["activityId"] != "va-6":
                continue
            cell["status"] = {
                "pass": "pass",
                "fail": "fail",
                "blocked": "gap",
            }.get(check["status"], "planned")
            cell["note"] = check.get("note")
            if evidence_ref:
                cell["evidenceRef"] = evidence_ref


def _goal_from_program(
    program: dict[str, Any],
    *,
    goal_override: str | None,
    max_iterations: int | None,
) -> dict[str, Any]:
    existing = next(iter(program.get("coDesignRuns", [])), None)
    if existing:
        goal = deepcopy(existing["goal"])
        if goal_override:
            goal["objective"] = goal_override
        if max_iterations is not None:
            goal["maxIterations"] = max_iterations
        return goal
    return {
        "id": "goal-cli",
        "title": "Autonomous thermal trade",
        "objective": goal_override or "Reduce radiator mass while preserving thermal closure.",
        "sourceRequirementIds": ["req-s3", "req-sub4", "dc-2"],
        "targetMetrics": [
            {"key": "radiatorMassKg", "label": "Radiator mass", "direction": "at_most", "targetValue": 15.7, "unit": "kg"},
            {"key": "rejectionEfficiency", "label": "Rejection efficiency", "direction": "at_least", "targetValue": 0.94},
            {"key": "heatBalanceMarginKw", "label": "Heat balance margin", "direction": "at_least", "targetValue": 0.0, "unit": "kW"},
        ],
        "maxIterations": max_iterations or 8,
    }


def run_codesign(
    program: dict[str, Any],
    *,
    goal_override: str | None = None,
    max_iterations: int | None = None,
    script_path: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    working_program = deepcopy(program)
    goal = _goal_from_program(
        working_program,
        goal_override=goal_override,
        max_iterations=max_iterations,
    )
    run = {
        "id": "cdr-cli",
        "title": "CLI autonomous co-design run",
        "status": "running",
        "actorMode": "autonomous_ai",
        "goal": goal,
        "startedAt": _iso_now(),
        "iterations": [],
        "latestSummary": "CLI run started.",
    }
    working_program.setdefault("coDesignRuns", []).append(run)
    conn = connect_db(db_path) if db_path else None

    parameters = _parameter_map(working_program)
    metrics, stdout = _run_simulation(script_path or DEFAULT_SCRIPT, parameters)
    run["latestSummary"] = stdout.splitlines()[0]
    if conn:
        store_run(conn, run)
        store_graph_snapshot(conn, run["id"], working_program, created_at=run["startedAt"])

    for index in range(1, int(goal["maxIterations"]) + 1):
        next_values, mutations = propose_parameter_updates(parameters, metrics, goal["targetMetrics"])
        if not mutations:
            run["status"] = "converged"
            run["completedAt"] = _iso_now()
            run["latestSummary"] = "Design agent proposed no further changes."
            if conn:
                store_run(conn, run)
            break

        parameters = next_values
        _apply_parameter_values(working_program, parameters)
        at = _iso_now()
        metrics, stdout = _run_simulation(script_path or DEFAULT_SCRIPT, parameters)
        checks, converged, summary = evaluate_requirements(metrics, goal["targetMetrics"])
        integration_run_id = f"run-codesign-{index}"
        integration_run = _integration_run(integration_run_id, stdout, metrics, at)
        provenance = _provenance_records(f"cdi-cli-{index}", mutations, at)

        iteration = {
            "id": f"cdi-cli-{index}",
            "index": index,
            "startedAt": at,
            "completedAt": at,
            "summary": summary,
            "objectiveScore": round(index / int(goal["maxIterations"]), 3),
            "mutations": mutations,
            "metrics": _metric_rows(metrics),
            "requirementChecks": checks,
            "integrationRunIds": [integration_run_id],
            "generatedIntegrationRuns": [integration_run],
            "generatedProvenanceRecords": provenance,
        }
        run["iterations"].append(iteration)
        working_program.setdefault("integrationRuns", []).append(integration_run)
        working_program.setdefault("provenanceRecords", []).extend(provenance)
        _update_matrix(working_program, checks, integration_run.get("evidenceRef"))

        if conn:
            store_iteration(conn, run["id"], iteration)
            store_graph_snapshot(
                conn,
                run["id"],
                working_program,
                created_at=at,
                iteration_id=iteration["id"],
            )
            store_run(conn, run)

        if converged:
            run["status"] = "converged"
            run["completedAt"] = at
            run["latestSummary"] = summary
            if conn:
                store_run(conn, run)
            break
    else:
        run["status"] = "max_iterations"
        run["completedAt"] = _iso_now()
        run["latestSummary"] = "Maximum iterations reached before convergence."
        if conn:
            store_run(conn, run)

    if conn:
        conn.close()
    return working_program
