# Pod Supervisor System — Finalized Design v1

## The Ask
Josh wants **truly independent worker instances** — isolated Hermes subagent processes that spin up, do focused work, report back, and die. Not cron jobs running in my context — separate agents with their own sessions, context windows, and tool access. He wants me to supervise them (review logs, catch errors, course-correct) without being on the hook for every detail of execution.

## The Architecture

```
Cron Scheduler (every 4h)
    │
    ▼
Supervisor Turn (me, ~1 LLM call)
    │  Decide: what pods to spin up, based on schedule
    │  Fire: delegate_task(background=True) for each pod
    │
    ├──► Pod A: CRM Health Check
    │    - Isolated agent with file + terminal tools
    │    - Checks: mirror integrity, blank records, stale data, misaligned flags
    │    - Writes report to /opt/data/pod-logs/crm-health/<timestamp>.json
    │
    ├──► Pod B: Cron Watch
    │    - Isolated agent with cronjob tool
    │    - Checks: all cron jobs, flags errors, stale runs, delivery failures
    │    - Writes report to /opt/data/pod-logs/cron-watch/<timestamp>.json
    │
    ├──► Pod C: (future — shell script, no LLM cost)
    │
    └──► Results flow back to me (background=True notification)
            │
            ▼
        Supervisor Turn 2 (me, ~1 LLM call)
            │  Review all pod outputs
            │  Compile summary
            │  Deliver to Josh only if something needs attention
```

## My Recommendations on the Two Open Questions

### Q1: First Pods — CRM Health + Cron Watch?

**Recommendation: YES, CRM Health first, Cron Watch second.**

Rationale:
- CRM drift has been a recurring pain point you've personally experienced (blank records, missing flags, stale mirror)
- Cron Watch surfaces silent failures you'd never know about — high ROI for zero reasoning work
- These are the two most independent, bounded tasks — perfect subagent candidates
- Starting with 2 pods keeps the first iteration lean; we add more after validation

One nuance: **Cron Watch doesn't actually need a full LLM subagent.** A Python script can list cron jobs via the Hermes CLI, parse statuses, and flag errors — that's $0/run. CRM Health needs actual reasoning (looking at anomaly patterns, deciding what matters). So:

| Pod | Cost Model | Reasoning Needed? |
|---|---|---|
| CRM Health | subagent ~$0.02/run | Yes — anomaly judgment |
| Cron Watch | shell script $0/run | No — deterministic check |
| Memory Pressure | shell script $0/run | No — size thresholds |
| Strategy Reviewer | subagent ~$0.02/run | Yes — link integrity |

This is the right split: use subagents only where reasoning adds value, scripts everywhere else.

### Q2: Pod Log Format — JSON files, SQLite, or last-N?

**Recommendation: JSON files in a directory, kept to last 20 runs per pod.**

Rationale:
- **JSON files**: simplest to write, read, grep, and archive. No schema maintenance
- **Directory per pod**: `/opt/data/pod-logs/crm-health/` — easy to find things
- **Last 20 runs**: bounded disk usage (~2MB total). Oldest auto-purged
- **Not SQLite**: overkill for write-once-read-rarely logs. Adds dependency
- **Not last-N-only**: losing history means you can't spot trending problems

Each pod writes its report as:
```json
{
  "pod": "crm-health",
  "run_at": "2026-06-23T22:00:00Z",
  "status": "ok" | "warn" | "error",
  "checks": [
    {"name": "mirror_exists", "status": "pass", "detail": "135 records"},
    {"name": "blank_records", "status": "fail", "detail": "1 blank record (Pet 1001)"}
  ],
  "summary": "1 anomaly found: blank record Pet 1001"
}
```

The supervisor reads the latest file per pod to compile the briefing.

## The Flow (exactly what happens each cycle)

1. **Cron fires** at T+4h (e.g., 2am, 6am, 10am, 2pm, 6pm, 10pm)
2. **My supervisor turn** (single LLM call):
   - Check schedule: which pods are due
   - For CRM Health: fire `delegate_task(background=True)` with the CRM health prompt
   - For Cron Watch: run the shell script directly (no subagent needed)
   - For Memory: run the shell check
3. **Pods run in parallel** — subagents are isolated, scripts are instant
4. **Results come back** via background notification
5. **Second supervisor turn** — review all outputs, write summary to pod log, decide if Josh needs an alert
6. **Silence is success** — no news is good news. Only message Josh if something's broken

## Budget Estimate

| Component | Cost/Run | Runs/Day | Daily Total |
|---|---|---|---|
| Supervisor turn | ~$0.01 | 6 | $0.06 |
| CRM Health pod | ~$0.02 | 6 | $0.12 |
| Cron Watch script | $0 | 6 | $0 |
| Memory check script | $0 | 2 | $0 |
| **Total** | | | **~$0.18/day** |

Well within the +/-$3 budget.
