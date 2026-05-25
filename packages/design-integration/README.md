# Design integration

Excel ↔ Python SSOT bindings and logic-automation runner. AI agents do not execute here.

```bash
cd packages/design-integration
uv sync
uv run python examples/create_workbook.py
uv run one-piece-sync \
  --workbook examples/propulsion_budget.xlsx \
  --script examples/thrust_margin.py \
  --bind "Inputs!B2:P-VBUS:P-VBUS" \
  --bind "Inputs!B3:P-M-MOTOR:P-M-MOTOR"
```
