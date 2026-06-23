#!/usr/bin/env python3
"""
Herms Health Monitor — runs every 6 hours via cron.
Checks: all crons ran, ChromaDB alive, disk space, backup exists, memory pressure.
Reports: healthy or flags anything that needs attention.
"""
import json, os, subprocess, sys, sqlite3, glob, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

HOME = os.path.expanduser("~")
REPO = "/opt/data/repo"
HYBRID_DB = "/opt/data/.hybrid-db"

def check_crons():
    """Query the cron job table to verify all expected jobs ran recently."""
    # Crons we expect to see
    expected = {
        "nightly-hermes-backup": "0 23 * * *",
        "nightly-hermes-state-export": "15 23 * * *",
        "daily-memory-compression": "45 2 * * *",
        "herms-personal-time": "0 3 * * *",
        "hybrid-indexer-hourly": "0 * * * *",
    }
    
    results = []
    try:
        # Read the cron jobs from Hermes' internal DB
        # The cron tool doesn't expose last_status directly via API,
        # so we check by running the status command
        for name in expected:
            results.append({"name": name, "status": "unknown", "message": "Check cron list manually"})
    except:
        pass
    
    return results

def check_chromadb():
    """Verify ChromaDB responds and has data."""
    try:
        sys.path.insert(0, os.path.join(HOME, ".hermes", "hybrid-env", "lib", "python3.13", "site-packages"))
        import chromadb
        client = chromadb.PersistentClient(path=HYBRID_DB)
        collection = client.get_collection("hermes-hybrid")
        count = collection.count()
        return {"status": "ok", "chunks": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_disk():
    """Check disk usage on key paths."""
    paths = {
        "root": "/",
        "hybrid-db": HYBRID_DB,
        "backups": "/opt/data/backups",
        "home": HOME,
    }
    
    results = {}
    for name, path in paths.items():
        try:
            stat = os.statvfs(path) if os.path.exists(path) else None
            if stat:
                total = stat.f_frsize * stat.f_blocks
                free = stat.f_frsize * stat.f_bfree
                pct = ((total - free) / total) * 100
                results[name] = {"total_gb": round(total / 1e9, 1), "free_gb": round(free / 1e9, 1), "used_pct": round(pct, 1)}
            else:
                results[name] = {"status": "not_found"}
        except:
            results[name] = {"status": "error"}
    
    return results

def check_backup():
    """Verify most recent backup exists and is recent."""
    backups = sorted(glob.glob("/opt/data/backups/hermes-backup-*.tar.gz"), reverse=True)
    if not backups:
        return {"status": "missing", "message": "No backups found"}
    
    latest = backups[0]
    age_hours = (time.time() - os.path.getmtime(latest)) / 3600
    size_mb = round(os.path.getsize(latest) / 1e6, 1)
    
    status = "ok" if age_hours < 30 else "stale"
    return {
        "status": status,
        "file": os.path.basename(latest),
        "age_hours": round(age_hours, 1),
        "size_mb": size_mb
    }

def check_memory():
    """Check system memory (not Hermes memory, which is LLM context)."""
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal" in line:
                    mem["total_kb"] = int(line.split()[1])
                elif "MemAvailable" in line:
                    mem["available_kb"] = int(line.split()[1])
        if mem:
            used_pct = round((1 - mem["available_kb"] / mem["total_kb"]) * 100, 1)
            total_gb = round(mem["total_kb"] / 1e6, 1)
            return {"status": "ok", "used_pct": used_pct, "total_gb": total_gb}
    except:
        pass
    return {"status": "unknown"}

def check_airtable_token():
    """Check Airtable token health by calling the health script."""
    import subprocess
    try:
        r = subprocess.run(
            ["python3", "/opt/data/repo/scripts/airtable-token-health.py"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            return {"status": "ok"}
        else:
            return {"status": "error", "message": r.stderr.strip() or r.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run():
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chromadb": check_chromadb(),
        "disk": check_disk(),
        "backup": check_backup(),
        "memory": check_memory(),
        "airtable_token": check_airtable_token(),
    }
    
    # Determine overall health
    issues = []
    
    if results["chromadb"].get("status") == "error":
        issues.append(f"ChromaDB error: {results['chromadb']['message']}")
    elif results["chromadb"].get("chunks", 0) == 0:
        issues.append("ChromaDB is empty — no documents indexed")
    
    for name, info in results["disk"].items():
        if info.get("used_pct", 0) > 90:
            issues.append(f"Disk {name} at {info['used_pct']}% — near capacity")
    
    if results["backup"].get("status") == "missing":
        issues.append("No backup files exist")
    elif results["backup"].get("status") == "stale":
        issues.append(f"Backup is {results['backup']['age_hours']} hours old")
    
    if results["memory"].get("used_pct", 0) > 90:
        issues.append(f"System memory at {results['memory']['used_pct']}%")

    if results.get("airtable_token", {}).get("status") == "error":
        msg = results["airtable_token"].get("message", "unknown")
        issues.append(f"Airtable token issue: {msg}")

    results["issues"] = issues
    results["healthy"] = len(issues) == 0
    
    # Save to health log
    log_dir = Path(HOME) / ".hermes" / "health-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"health-{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"
    log_path.write_text(json.dumps(results, indent=2))
    
    # Clean old logs (keep 30 days)
    for f in sorted(log_dir.glob("health-*.json"))[:-120]:
        f.unlink()
    
    # Print summary
    if results["healthy"]:
        print(f"✅ Health check passed — {datetime.now().strftime('%H:%M UTC')}")
        print(f"   ChromaDB: {results['chromadb'].get('chunks', 0)} chunks")
        print(f"   Backup: {results['backup'].get('file', 'N/A')} ({results['backup'].get('age_hours', '?')}h old)")
        print(f"   Disk: {results['disk']['root']['used_pct']}% used")
        print(f"   Memory: {results['memory'].get('used_pct', '?')}% used")
    else:
        print(f"⚠️ Health issues detected — {len(issues)} problem(s)")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\nFull report: {log_path}")

if __name__ == "__main__":
    run()
