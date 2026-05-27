from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from one_piece_codesign.orchestrator import DEFAULT_SCRIPT, run_codesign


def make_program() -> dict:
    return {
        "id": "p1",
        "name": "demo",
        "configurations": [],
        "activeConfigurationId": "cfg",
        "model": {
            "requirements": [],
            "elements": [],
            "traces": [],
            "interfaceControlDocuments": [],
            "interfaceParameters": [],
            "designParameters": [
                {
                    "id": "param-rad-area",
                    "key": "P-RAD-AREA",
                    "name": "Radiator area",
                    "value": 6.8,
                    "discipline": "thermal",
                    "state": "baseline",
                },
                {
                    "id": "param-rad-mass",
                    "key": "P-RAD-MASS",
                    "name": "Radiator mass",
                    "value": 18.5,
                    "discipline": "thermal",
                    "state": "baseline",
                },
                {
                    "id": "param-heat-load",
                    "key": "P-HEAT-LOAD",
                    "name": "Heat load",
                    "value": 15.2,
                    "discipline": "thermal",
                    "state": "baseline",
                },
                {
                    "id": "param-coolant-flow",
                    "key": "P-COOLANT-FLOW",
                    "name": "Coolant flow",
                    "value": 0.72,
                    "discipline": "thermal",
                    "state": "baseline",
                },
            ],
            "designConstraints": [],
            "cadModels": [],
            "designArtifacts": [],
            "cellCodeBindings": [],
        },
        "verificationActivities": [],
        "matrixCells": [
            {"requirementId": "req-s3", "activityId": "va-6", "status": "planned"},
            {"requirementId": "req-sub4", "activityId": "va-6", "status": "planned"},
            {"requirementId": "dc-2", "activityId": "va-6", "status": "planned"},
        ],
        "agentScopePolicy": {
            "allowedFraction": 1,
            "blockedCriticalityTiers": ["critical"],
            "allowedNodeKinds": ["design_parameter", "design_constraint", "requirement"],
            "requireProvenanceDisclosure": True,
            "autonomousCoDesign": True,
        },
        "provenanceRecords": [],
        "integrationRuns": [],
        "coDesignRuns": [
            {
                "id": "cdr-demo",
                "title": "demo",
                "status": "ready",
                "actorMode": "autonomous_ai",
                "goal": {
                    "id": "g1",
                    "title": "goal",
                    "objective": "reduce mass",
                    "sourceRequirementIds": ["req-s3"],
                    "targetMetrics": [
                        {
                            "key": "radiatorMassKg",
                            "label": "Radiator mass",
                            "direction": "at_most",
                            "targetValue": 15.7,
                        },
                        {
                            "key": "rejectionEfficiency",
                            "label": "Rejection efficiency",
                            "direction": "at_least",
                            "targetValue": 0.94,
                        },
                        {
                            "key": "heatBalanceMarginKw",
                            "label": "Heat balance margin",
                            "direction": "at_least",
                            "targetValue": 0.0,
                        },
                    ],
                    "maxIterations": 3,
                },
                "startedAt": "2026-05-26T00:00:00Z",
                "iterations": [],
            }
        ],
    }


class OrchestratorTest(unittest.TestCase):
    def test_run_codesign_generates_iterations_and_persistence(self) -> None:
        program = make_program()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            script_copy = tmpdir_path / "thermal_rejection.py"
            db_path = tmpdir_path / "codesign.db"
            shutil.copy(DEFAULT_SCRIPT, script_copy)

            updated = run_codesign(
                program,
                max_iterations=2,
                script_path=script_copy,
                db_path=db_path,
            )

            self.assertTrue(db_path.exists())
            self.assertGreaterEqual(len(updated["integrationRuns"]), 1)
            self.assertGreaterEqual(len(updated["provenanceRecords"]), 1)
            self.assertEqual(updated["coDesignRuns"][-1]["status"], "max_iterations")
            self.assertEqual(len(updated["coDesignRuns"][-1]["iterations"]), 2)


if __name__ == "__main__":
    unittest.main()
