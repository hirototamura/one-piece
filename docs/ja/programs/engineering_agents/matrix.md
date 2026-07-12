# Engineering Agents — コンプライアンスマトリクス（草案）

要求 × verification case。証拠欄は実行／テスト記録時に埋める。

| 要求 | VC-ea-loop-2run | VC-ea-pytest | 状態 | 証拠 |
|------|-----------------|--------------|------|------|
| `EA-SW-MIS-001` | （SYS 経由） | — | planned | — |
| `EA-SW-SYS-010` | verify | — | planned | E-run1, E-run2 |
| `EA-SW-SYS-020` | verify | — | planned | E-run1, E-run2 |
| `EA-SW-OPS-010` | （手段として行使） | — | planned | E-run1, E-run2 |
| `EA-SW-OPS-020` | — | — | planned | （介入経路；自動化しない） |
| `EA-SW-SUB-CLI-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-SCN-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-AGT-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-ENV-010` | — | verify | planned | E-pytest |
| `EA-SW-SUB-CORE-010` | — | verify | planned | E-pytest |

関係は動詞基本形: `verify(verification_case, requirement)`。  
全体グラフ: [system_graph.md](system_graph.md)。
