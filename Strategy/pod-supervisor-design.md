# Hermes Pod Supervisor — Architecture Design

## Core Idea

Replace the "everything runs through AStew" pattern with lightweight **pods** — small,
focused agents or scripts that run autonomously on a schedule, each owning one job.
A central **Supervisor** routes work, monitors health, and surfaces only what needs
human attention.

## No Kubernetes — Just Cron + Scripts + Delegation

| Component | What | Runs On |
|---|---|---|
| **Supervisor** | Heartbeat + dispatch + alerting | `hermes cron` every 30m |
| **Diagnostic pods** | Check one thing, report anomalies | Shell scripts (no-cost) |
| **Curation pods** | Fix/enrich CRM, notes, files | Hermes subagent (`delegate_task`) |
| **Alerting pod** | Watch cron output, surface failures | Hermes subagent |
| **Dashboard** | Status page generated from pod output | Shell script → local file |

## Pod Definitions

### 1. CRM Health Check (Diagnostic)
**Schedule:** Every 60m (piggyback on existing CRM sync)
**Script:** `python3 /opt/data/scripts/pod/crm-health.py`
**Checks:**
- Mirror file exists and is non-empty
- Airtable API responds (basic ping)
- No records with missing Name + Full Name (blank records)
- Report count of records with Notes that lack Has Notes flag
- Flag any records with stale/expired data patterns

### 2. Cron Health Watch (Alerting)
**Schedule:** Every 60m
**Script:** `python3 /opt/data/scripts/pod/cron-watch.py`
**Checks:**
- Query cronjob(action='list')
- Flag any job with `last_status='error'` that's still enabled
- Report which jobs haven't run in >24h
- Surface delivery errors

### 3. Memory Pressure Monitor (Diagnostic)
**Schedule:** Every 4h
**Script:** No-cost shell + Python
**Checks:**
- Memory file size (warn >50KB)
- User profile size (warn >20KB)
- Recent duplicate entries

### 4. Mirror Sync Watchdog (Diagnostic)
**Schedule:** Every 30m
**Script:** `python3 /opt/data/scripts/pod/mirror-watch.py`
**Checks:**
- `crm_lookup --count` for expected record count
- Compare local mirror timestamp vs last cron-run timestamp
- Flag if sync is stale (>2h since last pull)

### 5. Strategy File Reviewer (Curation)
**Schedule:** Daily
**Agent:** Hermes subagent loaded with file tools
**Work:**
- Scan `/opt/data/repo/Strategy/people-of-interest/` for orphaned/broken links
- Check cross-reference integrity
- Flag stale notes

## Data Flow

```
Schedule ticks (cron)
    │
    ▼
Supervisor wakes → runs pod scripts
    │
    ├─ Diagnostic script → stdout → captured → parsed
    │   If anomalies → write to /var/hermes/pod-log/<pod-name>.json
    │   
    ├─ Curation agent → delegate_task → summary → saved
    │
    └─ Alerting → check all pod logs
        If any pod has errors → compile brief → deliver to user
```

## Cost Model

- **Diagnostic pods:** Pure Python/shell — $0 in LLM costs per run
- **Curation pods:** 1-2 delegate_task calls per day — ~$0.02-0.05/day
- **Alerting pod:** 1 LLM call per run (only when there's something to report) — ~$0.01/day
- **Supervisor itself:** 1 single LLM turn to compile report — ~$0.01 per 30m tick

Target: **<$0.15/day in LLM costs** for the whole system.

## Implementation Order

1. ✅ Build pod scripts directory
2. Create CRM Health Check pod
3. Create Cron Health Watch pod
4. Wire Supervisor cron
5. Add Mirror Watchdog
6. Add curation pods
7. Add alerting
8. Build simple status dashboard
