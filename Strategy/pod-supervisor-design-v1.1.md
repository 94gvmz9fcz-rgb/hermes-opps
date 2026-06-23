# Pod Supervisor — v1.1 (Post-Review)

## Changes from v1

| Issue | v1 | v1.1 |
|---|---|---|
| Silent pod failures | Trusted `background=True` to report | **Pod liveness markers** — `{pod}.started` + `{pod}.completed` files |
| Cost estimate | $0.18/day | **$0.42/day** (realistic) — still well under $3 |
| CRM Health cost | Agent every run | **Dual-mode**: shell collects data, agent only on anomaly |
| No heartbeat | Silence = success | 24h summary to pod log (no Josh ping) |

## Architecture v1.1

```
Cron (every 4h)
    │
    ▼
Supervisor Turn 1 (~$0.02)
    │  Write .tick marker
    │  Fire pods:
    │
    ├── CRM Health Data Collector (shell, $0)
    │   → Write .started → run checks → write .completed with raw data
    │   → If anomalies found → trigger CRM Health Analyzer (agent, ~$0.03)
    │
    ├── Cron Watch (shell, $0)
    │   → Write .started → list cron jobs → parse statuses → write .completed
    │
    └── Memory Pressure (shell, $0)
        → Write .started → check sizes → write .completed
    │
    ▼
Results back to Supervisor
    │
Supervisor Turn 2 (~$0.02)
    │  Check: did all .started + .completed exist?
    │  Check: any anomalies from pods that ran analysis?
    │  Every 24h: write pod-health-summary.json
    │  If anomalies → alert Josh
    │  If missing markers → alert Josh (pod failure)
```

## Pod Liveness Protocol

Every pod run leaves exactly 2 markers:

1. `{pod-name}/2026-06-23T22:00:00Z.started` — written immediately on pod init
   ```json
   {"pod": "crm-health", "run_at": "...", "status": "started"}
   ```
2. `{pod-name}/2026-06-23T22:00:00Z.completed` — written on successful completion
   ```json
   {"pod": "crm-health", "run_at": "...", "status": "ok|warn|error", "checks": [...], "summary": "..."}
   ```

Supervisor checks at each turn:
- For every pod on the schedule: does a `.completed` exist for this tick?
- If `.started` exists but no `.completed` → **POD FAILURE** → alert Josh
- If neither exists → pod never launched → **SCHEDULER FAILURE** → alert Josh
