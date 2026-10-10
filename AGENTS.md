# One-Piece engineering record core

Read [CORE](docs/en/CORE.md), [system model](docs/en/SYSTEM_MODEL.md), and the NASA/SpaceX agent references before engineering changes.

Versioned JSON is the source of truth; the SQLite index is disposable. Keep the system graph minimal and traceable. Preserve requirements, KDPs, detailed parameters, evidence provenance and human decisions. Relations are derive/satisfy/verify/allocate/constrain; this is a SysML v2-inspired graph, not a SysML language implementation.

Agents draft and run bounded development experiments. Humans establish requirements, evaluation contracts and adopted baselines. A numerical simulation result does not demonstrate physical-world validity.

Run `python -m pytest` before submitting changes. Keep artifact objects, indexes, generated reports and virtual environments out of Git; publish content-addressed evidence bundles as Release assets.
