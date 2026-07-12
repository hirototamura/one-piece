# Engineering Agents — 妥当性確認計画

妥当性確認の問い: *ConOps に対して正しいソフトウェアを作っているか？*  
shall への検証: [verification.md](verification.md)。

## ConOps 参照

[conops.md](conops.md): 運用者指定 N で L1↔L2 → Final Design or Plan Change。真偽は決定論シム／制約／証拠。人間介入は可能だが時間コストあり。

## ミニマムサクセス（初期 Validation ゲート）

| 段階 | 期待 |
|------|------|
| Cycle 1 | L1↔L2（N ≥ 1）実行；非空の設計／パラメータ提案 |
| Cycle 2 | 提案適用後の再実行で Cycle 1 と **結果が異なる** |

ソフトウェア検証ケース `VC-ea-loop-2run` に対応（`EA-SW-SYS-010` / `EA-SW-SYS-020` を `verify`）。

## より広い妥当性の意図

- CLI から N と提案適用を制御してループ実行できる（`EA-SW-OPS-010`）。
- LLM のみの合格を認めない（`EA-SW-SYS-020`, `C-truth-gate`）。
- ドメイン／プラントの結果はシナリオ内容であり、ソフトウェア ConOps の代替にはしない。
