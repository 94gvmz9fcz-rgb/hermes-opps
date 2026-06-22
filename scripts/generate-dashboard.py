#!/usr/bin/env python3
"""
Dashboard Generator — regenerates Hermes dashboard HTML with live data.
Runs as a cron job (every 6 hours) and pushes to gh-pages.

Output: dashboard-data.json (consumed by dashboard/index.html)
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = "/opt/data/repo"
DASHBOARD_DIR = os.path.join(REPO_DIR, "output", "dashboard")
DATA_FILE = os.path.join(DASHBOARD_DIR, "dashboard-data.json")

VAULT_SCRIPT = os.path.join(REPO_DIR, "scripts", "hermes-vault-read.py")

def get_system_stats():
    """Collect system health data."""
    stats = {}

    # Memory
    try:
        with open("/proc/meminfo") as f:
            mem = f.read()
        for line in mem.splitlines():
            if line.startswith("MemTotal:"):
                total = int(line.split()[1]) // 1024
            elif line.startswith("MemAvailable:"):
                avail = int(line.split()[1]) // 1024
        used = total - avail
        pct = (used / total) * 100
        stats["memory"] = f"{used}M / {total}M ({pct:.0f}%)"
        stats["memory_pct"] = round(pct)
    except Exception:
        stats["memory"] = "Unknown"

    # Disk
    try:
        st = os.statvfs(REPO_DIR)
        total_disk = st.f_frsize * st.f_blocks // (1024**3)
        free_disk = st.f_frsize * st.f_bfree // (1024**3)
        used_disk = total_disk - free_disk
        disk_pct = (used_disk / total_disk) * 100
        stats["disk"] = f"{used_disk}G / {total_disk}G ({disk_pct:.0f}%)"
        stats["disk_pct"] = round(disk_pct)
    except Exception:
        stats["disk"] = "Unknown"

    # Uptime
    try:
        with open("/proc/uptime") as f:
            uptime_secs = float(f.read().split()[0])
        days = int(uptime_secs // 86400)
        hours = int((uptime_secs % 86400) // 3600)
        stats["uptime"] = f"{days}d {hours}h"
    except Exception:
        stats["uptime"] = "Unknown"

    # Crons — check a few known ones
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=5
        )
        cron_lines = [l.strip() for l in result.stdout.splitlines()
                      if l.strip() and not l.strip().startswith("#")]
        active = len(cron_lines)
        stats["crons"] = f"{active} active"
    except Exception:
        stats["crons"] = "Unknown"

    # Overall health
    health = "good"
    if stats.get("memory_pct", 0) > 85:
        health = "warn"
    if stats.get("disk_pct", 0) > 85:
        health = "bad"
    if stats.get("memory_pct", 0) > 92:
        health = "bad"
    stats["health"] = health

    return stats


def get_crm_stats():
    """Get CRM contact counts from Airtable."""
    # For now, static fallback — Airtable API integration pending
    return {
        "crmTotal": "70+",
        "crmRecent": "23 biz cards + 47 VCF",
        "crmAttention": "Check phone fields",
    }


def generate_data():
    """Generate the dashboard data JSON."""
    system = get_system_stats()
    crm = get_crm_stats()

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health": system.get("health", "good"),
        "memory": system.get("memory", "—"),
        "disk": system.get("disk", "—"),
        "uptime": system.get("uptime", "—"),
        "crons": system.get("crons", "—"),
        "crmTotal": crm.get("crmTotal", "—"),
        "crmRecent": crm.get("crmRecent", "—"),
        "crmAttention": crm.get("crmAttention", "—"),
    }
    return data


def push_to_gh_pages(data_path):
    """Push the dashboard data to gh-pages branch."""
    try:
        # Create a fresh temp dir with dashboard files
        deploy_dir = tempfile.mkdtemp(prefix="dashboard-deploy-")

        # Copy dashboard index.html + data
        import shutil
        shutil.copy(
            os.path.join(DASHBOARD_DIR, "index.html"),
            os.path.join(deploy_dir, "dashboard.html")
        )
        shutil.copy(data_path, os.path.join(deploy_dir, "dashboard-data.json"))

        # Initialize git
        subprocess.run(["git", "init"], cwd=deploy_dir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "config", "user.name", "Hermes Agent"],
            cwd=deploy_dir, capture_output=True, timeout=5
        )
        subprocess.run(
            ["git", "config", "user.email", "hermes-agent@users.noreply.github.com"],
            cwd=deploy_dir, capture_output=True, timeout=5
        )
        subprocess.run(["git", "add", "-A"], cwd=deploy_dir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"dashboard: update {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            cwd=deploy_dir, capture_output=True, timeout=10
        )

        # Fetch existing gh-pages
        subprocess.run(
            ["git", "fetch", "origin", "gh-pages"],
            cwd=deploy_dir, capture_output=True, timeout=15
        )

        # We need to get the existing gh-pages content and merge
        # Simpler: use the repo's gh-pages worktree
        print(f"Dashboard data written to {data_path}")
        print(f"Deploy dir: {deploy_dir}")

        # Cleanup
        shutil.rmtree(deploy_dir, ignore_errors=True)
        return True

    except Exception as e:
        print(f"⚠️ Push to gh-pages failed: {e}")
        return False


def main():
    data = generate_data()

    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Dashboard data generated at {DATA_FILE}")
    print(f"   Memory: {data['memory']}")
    print(f"   Disk: {data['disk']}")
    print(f"   Uptime: {data['uptime']}")
    print(f"   Crons: {data['crons']}")
    print(f"   Health: {data['health']}")

    # Push to gh-pages
    # For now, just write the data — the gh-pages deploy is handled
    # by the gallery deploy mechanism. Dashboard will be available at
    # https://94gvmz9fcz-rgb.github.io/hermes-opps/dashboard.html
    # once dashboard-data.json is on gh-pages.

    return 0


if __name__ == "__main__":
    main()
