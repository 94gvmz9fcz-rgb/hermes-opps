#!/usr/bin/env python3
"""
Hermes Follow-Up Scheduler
==========================
A self-contained, SQLite-backed reminder system that runs server-side.
No macOS dependency. Josh can create follow-ups via voice or text,
and I deliver them when the time comes.

Usage:
  # Create a reminder
  python3 hermes-followup.py create --when "tomorrow at 3pm" --what "Call Sarah about the contract"
  python3 hermes-followup.py create --when "in 30 minutes" --what "Check the oven"
  
  # List pending reminders
  python3 hermes-followup.py list
  
  # Cancel a reminder
  python3 hermes-followup.py cancel --id 3
  
  # Fire due reminders (called by cron job every 5 minutes)
  python3 hermes-followup.py fire
  
  # Get count of pending
  python3 hermes-followup.py count

Database: ~/.hermes/reminders/followups.db
"""

import sqlite3
import json
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Config ───────────────────────────────────────────────────

DB_PATH = Path.home() / ".hermes" / "reminders" / "followups.db"
STATE_PATH = Path.home() / ".hermes" / "reminders" / "state.json"

# Josh's timezone
LOCAL_TZ = "America/Los_Angeles"

# ── Helpers ──────────────────────────────────────────────────

def local_now():
    """Get current datetime in Josh's timezone."""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(LOCAL_TZ))

def utc_now():
    """Get current datetime in UTC."""
    return datetime.now(timezone.utc)

# ── Database ─────────────────────────────────────────────────

def get_db():
    """Get or create the SQLite database."""
    db_path = str(DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            due_at TEXT NOT NULL,         -- ISO 8601 with timezone
            status TEXT NOT NULL DEFAULT 'pending',  -- pending, fired, cancelled
            fired_at TEXT,
            source TEXT DEFAULT 'voice',  -- voice, telegram, text
            tag TEXT DEFAULT ''           -- optional category tag
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_reminders_due 
        ON reminders(status, due_at)
    """)
    
    conn.commit()
    return conn


# ── Time Parsing ─────────────────────────────────────────────

def parse_when(when_str: str) -> str:
    """Parse a human time specification into an ISO 8601 datetime string.
    
    Supports:
      - "tomorrow at 3pm" / "tomorrow at 3:00pm"
      - "in 30 minutes" / "in 2 hours"
      - "at 3pm" / "at 15:00" (today, or tomorrow if past)
      - "next Monday at 9am"
      - "Friday at 6PM"
      - ISO timestamps like "2026-06-27T15:00:00"
      - "today at 6pm"
    """
    now = local_now()
    text = when_str.lower().strip()
    
    # If it's already ISO-ish, return it
    try:
        datetime.fromisoformat(text)
        return text
    except:
        pass
    
    # ── Relative: "in N minutes" / "in N hours" / "in an hour" ──
    m = re.match(r'in\s+(?:(\d+)|an?)\s+(min(?:ute)?s?|hour(?:s)?)\s*$', text)
    if m:
        amount = int(m.group(1)) if m.group(1) else 1
        unit = m.group(2)
        if unit.startswith('min'):
            target = now + timedelta(minutes=amount)
        else:
            target = now + timedelta(hours=amount)
        return target.isoformat()
    
    # ── Day name with or without time: "next Monday at 10am", "Friday at 6PM" ──
    days = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6}
    
    day_match = re.search(r'(?:next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
    if day_match:
        target_day = days[day_match.group(1)]
        days_until = (target_day - now.weekday()) % 7
        if 'next' in text and days_until == 0:
            days_until = 7  # next week, not today
        if days_until == 0 and 'next' not in text and 'this' not in text:
            # "Monday" on Monday — ambiguous, but default to today
            pass
        elif days_until == 0:
            days_until = 7  # "next Monday" on Monday means next week
        
        target = (now + timedelta(days=days_until)).replace(hour=9, minute=0, second=0, microsecond=0)
        
        # If a time was given too, use it
        time_match = re.search(r'(?:at|by)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
        if time_match:
            h = int(time_match.group(1))
            m = int(time_match.group(2) or 0)
            ap = time_match.group(3)
            if ap == 'pm' and h != 12: h += 12
            elif ap == 'am' and h == 12: h = 0
            target = target.replace(hour=h, minute=m)
        
        return target.isoformat()
    
    # ── "tomorrow at X" / "today at X" / "at X" / "by X" ──
    time_match = re.search(r'(?:at|by)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    
    if time_match:
        is_tomorrow = 'tomorrow' in text
        is_today = 'today' in text or 'tonight' in text
        
        h = int(time_match.group(1))
        m = int(time_match.group(2) or 0)
        ap = time_match.group(3)
        
        if ap:
            if ap == 'pm' and h != 12:
                h += 12
            elif ap == 'am' and h == 12:
                h = 0
        elif 'tonight' in text and h < 12:
            h += 12  # assume PM for "tonight at 8"
        
        days_ahead = 1 if is_tomorrow else 0
        target = now.replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(days=days_ahead)
        
        # If no day specified and target is in the past, assume tomorrow
        if not is_tomorrow and not is_today and target < now:
            target += timedelta(days=1)
        
        return target.isoformat()
    
    # ── No time spec — default to tomorrow 9am ──
    target = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    return target.isoformat()


# ── Commands ─────────────────────────────────────────────────

def cmd_create(when: str, what: str, notes: str = "", tag: str = "", source: str = "voice"):
    """Create a new follow-up reminder."""
    conn = get_db()
    try:
        due_local = parse_when(when)  # returns ISO string in local time
        # Convert to UTC for storage
        from zoneinfo import ZoneInfo
        local_dt = datetime.fromisoformat(due_local)
        due_utc = local_dt.astimezone(timezone.utc).isoformat()
        now_utc = utc_now().isoformat()
        
        conn.execute(
            "INSERT INTO reminders (title, notes, created_at, due_at, source, tag) VALUES (?, ?, ?, ?, ?, ?)",
            (what.strip(), notes, now_utc, due_utc, source, tag)
        )
        conn.commit()
        
        # Display in local time
        time_str = local_dt.strftime("%A, %b %d at %I:%M %p")
        
        reminder_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        return {
            "success": True,
            "id": reminder_id,
            "title": what.strip(),
            "due_at": due_utc,
            "display_time": time_str,
            "message": f"✅ Follow-up #{reminder_id} set for {time_str}: {what.strip()}"
        }
    finally:
        conn.close()


def cmd_list(status: str = "pending"):
    """List reminders by status."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, title, notes, due_at, created_at, status, source, tag FROM reminders WHERE status = ? ORDER BY due_at ASC",
            (status,)
        ).fetchall()
        
        if not rows:
            return {"success": True, "reminders": [], "message": "No pending follow-ups."}
        
        results = []
        for r in rows:
            try:
                from zoneinfo import ZoneInfo
                dt = datetime.fromisoformat(r["due_at"])
                la = ZoneInfo(LOCAL_TZ)
                local_dt = dt.astimezone(la)
                time_str = local_dt.strftime("%a, %b %d at %I:%M %p")
            except:
                time_str = r["due_at"]
            
            results.append({
                "id": r["id"],
                "title": r["title"],
                "due_at": time_str,
                "status": r["status"],
                "tag": r["tag"],
                "source": r["source"],
            })
        
        return {"success": True, "reminders": results, "count": len(results)}
    finally:
        conn.close()


def cmd_cancel(reminder_id: int):
    """Cancel a pending reminder."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, title, status FROM reminders WHERE id = ?", (reminder_id,)
        ).fetchone()
        
        if not row:
            return {"success": False, "message": f"❌ Follow-up #{reminder_id} not found."}
        
        if row["status"] == "fired":
            return {"success": False, "message": f"❌ Follow-up #{reminder_id} ('{row['title']}') already fired."}
        
        if row["status"] == "cancelled":
            return {"success": False, "message": f"❌ Follow-up #{reminder_id} ('{row['title']}') already cancelled."}
        
        conn.execute(
            "UPDATE reminders SET status = 'cancelled' WHERE id = ?", (reminder_id,)
        )
        conn.commit()
        
        return {"success": True, "message": f"✅ Cancelled follow-up #{reminder_id}: '{row['title']}'"}
    finally:
        conn.close()


def cmd_fire(dry_run: bool = False):
    """Check for due reminders and fire them.
    
    This is what the cron job calls every 5 minutes.
    Returns the list of reminders that fired.
    """
    conn = get_db()
    try:
        now_iso = utc_now().isoformat()
        
        # Fetch ALL pending reminders with due_at <= now (including past-due)
        # The .isoformat() has microseconds which can cause near-miss issues
        # during creation-firing race. To handle this, also include a small
        # lookahead so reminders created "in 1 minute" don't slip through
        # when the cron fires while they're still 0.5 seconds out.
        lookahead = (utc_now() + timedelta(seconds=30)).isoformat()
        
        due_reminders = conn.execute(
            "SELECT id, title, notes, due_at, tag, source FROM reminders WHERE status = 'pending' AND due_at <= ?",
            (lookahead,)
        ).fetchall()
        
        if not due_reminders:
            return {"success": True, "fired": [], "count": 0, "message": "No follow-ups due."}
        
        fired = []
        for r in due_reminders:
            if not dry_run:
                conn.execute(
                    "UPDATE reminders SET status = 'fired', fired_at = ? WHERE id = ?",
                    (now_iso, r["id"])
                )
            
            try:
                from zoneinfo import ZoneInfo
                dt = datetime.fromisoformat(r["due_at"])
                time_str = dt.astimezone(ZoneInfo(LOCAL_TZ)).strftime("%I:%M %p")
            except:
                time_str = r["due_at"]
            
            fired.append({
                "id": r["id"],
                "title": r["title"],
                "notes": r["notes"],
                "due_at": time_str,
                "tag": r["tag"],
                "source": r["source"],
            })
        
        if not dry_run:
            conn.commit()
        
        return {
            "success": True,
            "fired": fired,
            "count": len(fired),
            "message": f"🔥 {len(fired)} follow-up(s) due: {'; '.join(f['title'] for f in fired)}"
        }
    finally:
        conn.close()


def cmd_count():
    """Get count of pending reminders."""
    conn = get_db()
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE status = 'pending'"
        ).fetchone()[0]
        return {"success": True, "count": count}
    finally:
        conn.close()


def cmd_pending_since(tag: str = ""):
    """Get reminders due in the next N hours (for morning briefing)."""
    conn = get_db()
    try:
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(hours=24)).isoformat()
        
        if tag:
            rows = conn.execute(
                "SELECT id, title, due_at, tag FROM reminders WHERE status = 'pending' AND due_at <= ? AND tag = ? ORDER BY due_at ASC",
                (tomorrow, tag)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, due_at, tag FROM reminders WHERE status = 'pending' AND due_at <= ? ORDER BY due_at ASC",
                (tomorrow,)
            ).fetchall()
        
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── CLI Entry Point ──────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        when = ""
        what = ""
        notes = ""
        tag = ""
        source = "voice"
        
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--when" and i + 1 < len(args):
                when = args[i + 1]
                i += 2
            elif args[i] == "--what" and i + 1 < len(args):
                what = args[i + 1]
                i += 2
            elif args[i] == "--notes" and i + 1 < len(args):
                notes = args[i + 1]
                i += 2
            elif args[i] == "--tag" and i + 1 < len(args):
                tag = args[i + 1]
                i += 2
            elif args[i] == "--source" and i + 1 < len(args):
                source = args[i + 1]
                i += 2
            else:
                i += 1
        
        if not when or not what:
            print("Usage: hermes-followup.py create --when 'tomorrow at 3pm' --what 'Call Sarah'")
            sys.exit(1)
        
        result = cmd_create(when, what, notes, tag, source)
        print(result["message"])
    
    elif command == "list":
        status = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--status" else "pending"
        result = cmd_list(status)
        
        if result.get("reminders"):
            print(f"\n📋 Pending Follow-ups ({result['count']}):\n")
            for r in result["reminders"]:
                tag_str = f" [{r['tag']}]" if r.get('tag') else ""
                print(f"  #{r['id']}: {r['title']}{tag_str}")
                print(f"       Due: {r['due_at']}")
                print()
        else:
            print(result.get("message", "No reminders."))
    
    elif command == "cancel":
        rid = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--id" else None
        if not rid:
            print("Usage: hermes-followup.py cancel --id 3")
            sys.exit(1)
        result = cmd_cancel(rid)
        print(result["message"])
    
    elif command == "fire":
        dry_run = "--dry-run" in sys.argv
        result = cmd_fire(dry_run)
        if result["count"] > 0:
            print(f"🔥 {result['count']} follow-up(s) firing:")
            for r in result["fired"]:
                print(f"  #{r['id']}: {r['title']} (was due {r['due_at']})")
        else:
            print(result["message"])
    
    elif command == "count":
        result = cmd_count()
        print(result["count"])
    
    elif command == "pending-today":
        tag = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--tag" else ""
        reminders = cmd_pending_since(tag)
        print(json.dumps(reminders, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Commands: create, list, cancel, fire, count, pending-today")
        sys.exit(1)


if __name__ == "__main__":
    main()
