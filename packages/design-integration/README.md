# 設計連携（design-integration）

Excel ↔ Python の SSOT バインディングとロジック自動化ランナー。AI エージェントはここでは実行しない。

```bash
cd packages/design-integration
uv sync
uv run python examples/create_workbook.py
uv run one-piece-sync \
  --workbook examples/propulsion_budget.xlsx \
  --script examples/thrust_margin.py \
  --bind "Inputs!B2:P-VBUS:P-VBUS:VBUS" \
  --bind "Inputs!B3:P-M-MOTOR:P-M-MOTOR:MOTOR_MASS_KG"
```
