#!/usr/bin/env python3
"""
Hermes Token Budget Tracker

Runs on cron (daily). Reads Hermes agent logs / state to estimate
daily token usage and flags when we're trending toward budget overrun.

Usage:
    python3 scripts/hermes-token-budget.py

Config (first-run creates ~/.hermes/token-budget.json):
    daily_budget:  max tokens to spend per day (default: 5M)
    alert_at:      utilization % to trigger warning (default: 80)
    model_cost:    cost per 1M input tokens (DeepSeek: ~$0.14)
"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

CONFIG_PATH = Path.home() / ".hermes" / "token-budget.json"
SESSION_DB = Path("/opt/data") / "state.db"  # Hermes gateway state DB
DEFAULT_BUDGET = 5_000_000  # 5M tokens/day
ALERT_AT = 0.80
MODEL_COST_PER_1M = 0.14  # DeepSeek Chat, approx

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    config = {
        "daily_budget": DEFAULT_BUDGET,
        "alert_at": ALERT_AT,
        "model_cost_per_1m": MODEL_COST_PER_1M,
        "created": datetime.now().isoformat()
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    return config

def estimate_daily_tokens(session_db_path):
    """Read state DB to get real token usage for today."""
    if not session_db_path.exists():
        return {"estimated_tokens": 0, "session_count": 0, "error": "No state DB yet"}

    today = datetime.now().date()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    try:
        conn = sqlite3.connect(f"file:{session_db_path}?mode=ro", uri=True)
        cur = conn.cursor()

        # All sessions (the started_at is a unix timestamp float)
        cur.execute("SELECT id, started_at FROM sessions")
        all_sessions = cur.fetchall()

        today_sessions = 0
        yesterday_sessions = 0
        today_input = today_output = today_cache_r = today_cache_w = 0
        yesterday_tokens = 0

        for sid, ts in all_sessions:
            s_date = datetime.fromtimestamp(ts).date()
            if s_date == today:
                today_sessions += 1
            elif s_date == yesterday:
                yesterday_sessions += 1

        # Get today's token sums from DB using unix timestamps
        today_start = datetime.combine(today, datetime.min.time()).timestamp()
        today_end = datetime.combine(today, datetime.max.time()).timestamp()
        yesterday_start = datetime.combine(yesterday, datetime.min.time()).timestamp()
        yesterday_end = datetime.combine(yesterday, datetime.max.time()).timestamp()

        cur.execute("""
            SELECT COALESCE(SUM(input_tokens), 0),
                   COALESCE(SUM(output_tokens), 0),
                   COALESCE(SUM(cache_read_tokens), 0),
                   COALESCE(SUM(cache_write_tokens), 0)
            FROM sessions WHERE started_at >= ? AND started_at <= ?
        """, (today_start, today_end))
        today_input, today_output, today_cache_r, today_cache_w = cur.fetchone()
        estimated = today_input + today_output + today_cache_r + today_cache_w

        cur.execute("""
            SELECT COALESCE(SUM(input_tokens + output_tokens + cache_read_tokens + cache_write_tokens), 0)
            FROM sessions WHERE started_at >= ? AND started_at <= ?
        """, (yesterday_start, yesterday_end))
        yesterday_tokens = cur.fetchone()[0]

        # Today's message counts
        cur.execute("""
            SELECT COUNT(*) FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE s.started_at >= ? AND s.started_at <= ? AND m.role = 'assistant'
        """, (today_start, today_end))
        today_assistant_msgs = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE s.started_at >= ? AND s.started_at <= ? AND m.role = 'user'
        """, (today_start, today_end))
        today_user_msgs = cur.fetchone()[0]

        conn.close()

        return {
            "estimated_tokens": estimated,
            "input_tokens": today_input,
            "output_tokens": today_output,
            "cache_read_tokens": today_cache_r,
            "cache_write_tokens": today_cache_w,
            "today_sessions": today_sessions,
            "today_assistant_msgs": today_assistant_msgs,
            "today_user_msgs": today_user_msgs,
            "yesterday_sessions": yesterday_sessions,
            "yesterday_tokens": yesterday_tokens,
        }

    except Exception as e:
        return {"estimated_tokens": 0, "session_count": 0, "error": str(e)}

def main():
    config = load_config()
    budget = config["daily_budget"]
    alert_at = config.get("alert_at", ALERT_AT)
    cost_per_1m = config.get("model_cost_per_1m", MODEL_COST_PER_1M)

    stats = estimate_daily_tokens(SESSION_DB)
    tokens = stats["estimated_tokens"]
    utilization = tokens / budget * 100 if budget > 0 else 0
    est_cost = (tokens / 1_000_000) * cost_per_1m

    # Build report
    report = []
    report.append("=== Hermes Token Budget Report ===")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Daily Budget: {budget:,} tokens (${cost_per_1m * (budget / 1_000_000):.2f}/day max)")
    report.append("---")
    report.append(f"Today's Usage: {tokens:,} tokens")
    report.append(f"  Input: {stats.get('input_tokens', 0):,}")
    report.append(f"  Output: {stats.get('output_tokens', 0):,}")
    report.append(f"  Cache Read: {stats.get('cache_read_tokens', 0):,}")
    report.append(f"  Cache Write: {stats.get('cache_write_tokens', 0):,}")
    report.append(f"Utilization: {utilization:.1f}%")
    report.append(f"Estimated Cost Today: ${est_cost:.4f}")
    report.append("---")

    if "error" in stats:
        report.append(f"⚠️  Session DB: {stats['error']}")
    else:
        report.append(f"Sessions Today: {stats.get('today_sessions', 0)}")
        report.append(f"Messages Today: {stats.get('today_assistant_msgs', 0)} assistant / {stats.get('today_user_msgs', 0)} user")
        report.append(f"Sessions Yesterday: {stats.get('yesterday_sessions', 0)} ({stats.get('yesterday_tokens', 0):,} tokens)")

    if utilization >= alert_at * 100:
        report.append("")
        report.append(f"⚠️  ALERT: {utilization:.0f}% of daily budget used!")
        report.append(f"⚠️  Recommend throttling or reviewing usage patterns.")
        report.append(f"⚠️  Remaining budget: {max(0, budget - tokens):,} tokens")
    elif utilization >= 50:
        report.append(f"📊 Note: {utilization:.0f}% of budget used. On track.")

    report.append("")
    report.append(f"Config: {CONFIG_PATH}")

    print("\n".join(report))

    # Update rolling log
    log_path = Path.home() / ".hermes" / "token-budget-history.csv"
    is_new = not log_path.exists()
    with open(log_path, "a") as f:
        if is_new:
            f.write("date,tokens_estimated,today_sessions,assistant_msgs,user_msgs\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')},{tokens},{stats.get('today_sessions', 0)},{stats.get('today_assistant_msgs', 0)},{stats.get('today_user_msgs', 0)}\n")

    # Alert logic for cron delivery
    if utilization >= alert_at * 100:
        print(f"\nSTATUS=ALERT")
    elif utilization > 0:
        print(f"\nSTATUS=OK")
    else:
        print(f"\nSTATUS=NO_DATA")

if __name__ == "__main__":
    main()
