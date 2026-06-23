# Pod Supervisor — Trail Dog Learning System

**Status:** 🐾 Trail Dog — Active, learning every 30 min
**Phase:** Training (adaptive interval)
**Target:** 240 min (4h) stable plateau

---

## What It Does

Every supervisor run generates an **LLM-style learning report** — a structured training log with:
- Current interval, target, plateau status
- Per-pod reliability scores (liveness + anomaly counts)
- Error curve over time (compact ASCII table of last 20 steps)
- Recent lessons learned (what failed and why)
- Plateau assessment (when the system declares itself stable)

The **Trail Dog** adjusts the cron schedule based on cumulative error rates:
- **Bad streak** (≥2 consecutive alert runs) → shrink interval (get more data)
- **Clean streak** (≥6 consecutive perfect runs) → stretch interval (trust the system)
- **Plateau** (12 clean runs at target) → declare stable, recommend steady state
- **Plateau broken** (error after plateau) → immediately shrink and start over

## Trail Dog Rules

| Signal | Threshold | Action |
|---|---|---|
| Bad runs | ≥2 consecutive | Shrink by 50% (floor: 30 min) |
| Clean runs | ≥6 consecutive | Stretch by 1.5× (ceiling: 480 min) |
| At target + clean | ≥12 runs | Declare plateau |
| Plateau + error | 1 error | Break plateau, shrink |

## Cron Configuration

| Job | Schedule | Mode | Delivers To |
|---|---|---|---|
| `pod-supervisor-trail-dog` | `*/30 * * * *` (adaptive) | Script-only ($0) | local (pod-logs/) |
| `trail-dog-learning-report` | `0 */6 * * *` | LLM agent | Josh's Telegram |

## Learning State File

`pod-logs/learning-state.json` — persists:
- All training steps (auto-purged to last 100)
- Current adaptive interval
- Plateau status and golden interval
- Per-run anomaly counts, liveness, pod failure data

## Report Files

- `pod-logs/reports/latest-learning-report.md` — always the most recent
- `pod-logs/reports/report-step-<N>.md` — historical archive

## File Map

| File | Purpose |
|---|---|
| `scripts/pod/supervisor.py` | Supervisor v2 (integrated with learning engine) |
| `scripts/pod/learning_engine.py` | Learning engine + report generator + Trail Dog scheduler |
| `scripts/pod/pod_utils.py` | Shared liveness protocol (unchanged) |
| `Strategy/pod-supervisor-trail-dog.md` | This doc |
