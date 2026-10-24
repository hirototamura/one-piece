# Cube configuration catalogue and BOM reference

The catalogue separates three meanings of the earlier term “current model.” It adds a fourth configuration for the fixed BOM assessment. It does not change the ordinary Engineering Agents scenario default or establish an adopted hardware baseline.

- **CM-01 — requirements view:** `cube.simulation.snapshot@reviewed-20261019-1`. The human-reviewed 22 obligations and responsibility allocation. Its inherited numerical priors are not a new executable default.
- **CM-02 — scenario default:** `cube.simulation.snapshot@bottom-corner-000-20261017-3`. The lower-face descendant of D-000544-52890 with the saved MASS controller. Its compiled reference has a 166.235 mm side; it is distinct from its nominal controller-design plant.
- **CM-03 — historical experiment:** `cube.simulation.snapshot@fixed-dt-mvp-2`. Upper-face inputs used by the completed multi-agent study. Each candidate's saved compiled configuration and controller identify the actual experiment.
- **CM-04 — BOM reference:** `cube.simulation.snapshot@bom-reference-20261021-1`. A fixed 180 mm, 0.730 kg lower-face numerical proxy with component identities from the supplied BOM. It uses the retained controller without tuning.

The authoritative index is `cube.configuration.catalogue@bom-reference-20261021-1`. Entries `cube.configuration.cm-01` through `cm-04` pin exact snapshots, record hashes, requirement revisions, controller hashes and comparison designs. Select by role and exact revision, never by latest timestamp alone. The separate standalone ideal-pivot demonstration is catalogued as an additional preview, not equivalent to a floor-contact campaign.

## Reference parts and authority

The source workbook has 32 part lines, zero measured masses and one candidate battery mass of 49 g. Its SHA-256 is `3070a80b6d6aa3dfdd1d1a6346ceae676c5c405461adabbfb063b438dc3ddd51`. The [cell-level transcription](../../projects/balancing-cube/references/remrc_bom_20261021.json) preserves quantities, blank values, supplier candidates and source notes. `cube.bom.remrc` and 32 `component_reference` records retain the same data in the canonical store.

The source project is [remrc/Self-Balancing-Cube](https://github.com/remrc/Self-Balancing-Cube/tree/fb729c6294c7c45055f66be4568914f3d207608f), commit `fb729c6294c7c45055f66be4568914f3d207608f`. The selected firmware folder is `esp32_cube_enc`. The BOM names Nidec 24H404H160 motor/driver/encoder assemblies, an ESP32 board, MPU6050, a 3S 500 mAh LiPo battery, printed parts, passive components, fasteners and wiring. Exact motor torque curves and verified STL geometry are absent. Generic 24H or EC45 ratings are not transferred to this part.

P-005 and P-006 are alternatives. P-005 is provisional in this reference. Holder combinations remain unresolved; optional lighting is excluded. The numerical fixed aggregate already includes the battery: 0.550 kg fixed + 3 × 0.060 kg rotating = 0.730 kg. The 0.501 kg remainder after the candidate battery is an unresolved budget, not a sum of measured parts. No purchasing cost or total hardware mass is inferred from the incomplete BOM.

The user authorized explicit assumptions for this reference run. This authorization does not approve a hardware baseline or revise requirements. `cube.analysis.remrc-bom-requirements` compares all 22 reviewed obligations with parts and missing evidence. Requirement approval remains `human_reviewed`; hardware verification remains `not_run`. The existing SysML API annotation profile preserves these record revisions and references; no native SysML semantic conformance is added.

## Fixed assessment on 21 October 2026

Engineering Agents executed 34 native MuJoCo cases, with 1 ms physics, 15 ms control, one frozen K, zero LLM calls and zero design iterations:

- First 12-case development partition: 2/12 pass all gates, score −0.0252375205.
- Second 12-case development partition: 2/12 pass all gates, score −0.0325705162.
- Six heavy/delayed cases lose balance. Eighteen short cases finish six seconds. Twenty short cases exceed the uncalibrated torque-workload comparison threshold; fourteen of these complete without falling.
- Ten nominal 30 s, no-pulse trials with sensor seeds 2101–2110 complete and pass the listed numerical balance analogues. They do not establish hardware R-HOLD/R-REPEAT, independent metrology or eight-corner performance.

The 30 s diagnostic computes RMS over its full interval. The inherited six-second score still uses the final second. The approved requirements and inherited score/stop conditions are unchanged. Temperature, electrical power and hardware calibration remain unmeasured.

Run records `cube.run.remrc-bom-reference-20261021.{exploration,validation,hold30}@bom-reference-20261021-1` verify only the corresponding numerical test cases. Each carries compact results and the full evidence archive hash. There are no new `verify` links asserting hardware requirement compliance.

## Change procedure

1. Update component evidence or selections as a new BOM revision. Preserve original observations.
2. Review affected mass, geometry, inertia, motor, sensing and contact assumptions.
3. Create a new configuration/snapshot revision and pin the reviewed requirements and controller policy.
4. Run an explicit fixed assessment. Preserve failed cases and missing evidence.
5. Record results against the exact configuration and test-case revisions. Human decisions control requirement changes and adopted baselines.

The report and full telemetry are generated artifacts. Do not commit large HTML, trajectories or archives to Git. The compact store records, source transcription and runner code are versioned; evidence objects remain content-addressed.
