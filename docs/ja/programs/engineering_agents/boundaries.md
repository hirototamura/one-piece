# Engineering Agents — 境界

EA サブシステム間および外部シム backend とのソフトウェア境界。  
機械可読: [model/boundaries.yaml](../../../en/programs/engineering_agents/model/boundaries.yaml)。

| ID | From | To | 注 |
|----|------|-----|----|
| `B-cli-scenario` | CLI / tools | scenario | 運用者入口・実行制御 |
| `B-scenario-agents` | scenario | agents | チーム起動・共有コンテキスト |
| `B-scenario-env` | scenario | environment | プラント／backend の step とテレメトリ取得 |
| `B-scenario-core` | scenario | core | 共有状態・提案・結果永続化 |
| `B-env-backend` | environment | 外部シム／plant backend | 統合 IF のみ—ドメイン要求ではない |

## 割当

- `allocate(B-cli-scenario, EA-SW-SUB-CLI-010)`
- `allocate(B-scenario-agents, EA-SW-SUB-AGT-010)`
- `allocate(B-scenario-env, EA-SW-SUB-SCN-010)`
- `allocate(B-scenario-core, EA-SW-SUB-CORE-010)`
- `allocate(B-env-backend, EA-SW-SUB-ENV-010)`

詳細は [system_model.md](system_model.md)。
