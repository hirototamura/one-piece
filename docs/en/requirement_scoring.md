# Requirement shortfall scoring

The human-approved method is `requirement_max_deficit_v1`. Its canonical contract is
`cube.evaluation.requirement-shortfall@requirement-scoring-20261115-2`.
Run `PYTHONPATH=src python projects/balancing-cube/adopt_requirement_scoring.py` to
import its immutable records into this checkout's Cube store. The script is idempotent.

`onepiece.scoring.evaluate_requirements(contract, measurements, domain=...)` returns
each requirement's exact reference, measured value, limit, unit, status and deficit.
It accepts `hardware` or `simulation` as the evidence domain. The caller owns the
provenance and validity of supplied measurements; this calculation does not execute
hardware tests or adopt a design. Only the four declared numerical proxies can be
judged from simulation. All other requirements and constraints remain unjudged.

For an upper bound, deficit is `max(0, x/L - 1)`; for a lower bound it is
`max(0, 1 - x/L)`. A Boolean violation has deficit 1. Numeric equality uses absolute
relative difference, or 0/1 for a zero target. Missing/nonfinite data, unresolved
limits and invalid types are unjudged, with null deficit. A repeatability result
must also supply `successful_hold_trials_sample_count: 10`; ten trials are not
inferred from an unrelated numerical case matrix.

A mandatory failure makes the overall result fail regardless of other values.
Unjudged requirements prevent an overall pass. The search scope has its own status.
Its objective is the maximum deficit across independent requirements and all cases,
with `score = -max_deficit` for existing higher-is-better clients. Smaller deficit
is better; all sufficient performances tie at zero. The selector orders an in-scope
pass before a fail. There are no weights, KDP rewards, margin bonuses or extra
recovery objectives. Hierarchical mission/repeatability checks are not summed into
their child performance checks.

`onepiece.cube_scoring.evaluate_cube_records(records, snapshot)` uses the first
10 seconds, including release. Peaks come from existing trajectory samples. RMS
uses trapezoidal integration of squared tilt, interpolating the endpoint at 10 s.
This differs from the legacy final-one-second sample RMS. Missing, nonfinite,
nonmonotonic or gapped series cannot establish a pass. Early termination returns
known duration/peak shortfalls; an unavailable whole-interval RMS remains unjudged.
`max_known_deficit` retains useful feedback, while `max_deficit` and the scalar
score remain null if any required search deficit is unavailable. Such a candidate
is not ranked as a complete scored candidate. An empty/incomplete/duplicate trial
matrix is rejected by the scenario aggregator before scoring.

The executable child `cube.simulation.snapshot@requirement-scoring-20261115-2`
preserves the lower-face corner-000 plant/controller from
`bottom-corner-000-20261017-3`. It takes the reviewed requirements/KDPs from
`requirements-review-20261115-3` and changes the duration and scoring contract.
The existing domain/release/seed matrices remain development conditions; they are
neither an eight-corner demonstration nor the R-REPEAT hardware protocol. Current
simulation proxies cover R-HOLD, R-TILT, R-RMS and R-DRIFT. Electrical, thermal,
manufacturing, identification and other unavailable evidence remains unknown.
Simulation `physical_status` is always `unjudged`.

Engineering Agents freezes both scoring modules' source digests, persists complete
requirement results, passes the worst cases and unknown references to agents, and selects episodic best scores only within the same
scoring-contract reference. Historical contracts retain their original formula
and recorded results. No experiment is automatically rescored by this migration.

[Japanese](../ja/requirement_scoring.md)
