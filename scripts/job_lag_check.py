#!/usr/bin/env python3
"""
job_lag_check.py — per-job liveness watchdog (silent unless a cron goes stale).

For every ENABLED cron job: if its last successful run is more than
~2.5x its own schedule interval in the past, the job has silently died —
emit one alert line per stale job. Silent (exit 0, no output) when healthy.

Data: /opt/data/cron/jobs.json (has next_run_at / last_run_at per job).
Scheduled via no_agent cron, deliver origin.
"""
import json, datetime, sys

JOBS = "/opt/data/cron/jobs.json"

def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None

def main():
    data = json.load(open(JOBS))
    jobs = data if isinstance(data, list) else data.get("jobs", [])
    now = datetime.datetime.now(datetime.timezone.utc)
    stale = []
    for j in jobs:
        if not j.get("enabled", True):
            continue
        name = j.get("name") or j.get("job_id", "?")
        last = parse_ts(j.get("last_run_at"))
        nxt = parse_ts(j.get("next_run_at"))
        if last is None:
            continue  # never ran yet — not a staleness signal
        if nxt is None or nxt <= last:
            interval = datetime.timedelta(hours=12)  # fallback for odd schedules
        else:
            interval = nxt - last
        if interval <= datetime.timedelta(0):
            continue
        age = now - last
        if age > interval * 2.5:
            hrs = round(age.total_seconds() / 3600, 1)
            int_h = round(interval.total_seconds() / 3600, 1)
            stale.append((name, hrs, int_h))
    if stale:
        print("⚠️  *Cron staleness alert* — these jobs haven't run in >2.5x their schedule:")
        for name, hrs, int_h in sorted(stale, key=lambda x: -x[1]):
            print(f"• **{name}** — last ran {hrs}h ago (schedule ~{int_h}h)")

if __name__ == "__main__":
    main()
