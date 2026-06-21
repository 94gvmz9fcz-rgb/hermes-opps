#!/usr/bin/env python3
"""Nightly Hermes backup — tarball to /opt/data/backups/ and OneDrive."""
import glob, subprocess, tarfile, os, sys, time
from datetime import date

BACKUP_DIR = "/opt/data/backups"
REPO_DIR = "/opt/data/repo"
HOME_DIR = "/opt/data"
TODAY = date.today().isoformat()
ARCHIVE_NAME = f"hermes-backup-{TODAY}.tar.gz"
ARCHIVE_PATH = os.path.join(BACKUP_DIR, ARCHIVE_NAME)
ONEDRIVE_BACKUP = f"OneDrive/Hermy/_backups/{ARCHIVE_NAME}"

os.makedirs(BACKUP_DIR, exist_ok=True)

# Collect files to back up
paths = [
    os.path.join(HOME_DIR, ".hermes/config.yaml"),
    os.path.join(HOME_DIR, ".env"),
    os.path.join(HOME_DIR, "skills"),
    os.path.join(REPO_DIR, "docs"),
    os.path.join(REPO_DIR, "scripts"),
]

existing = [p for p in paths if os.path.exists(p)]

if not existing:
    print("Nothing to back up — no source paths found.")
    sys.exit(1)

with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
    for path in existing:
        tar.add(path, arcname=os.path.relpath(path, HOME_DIR))

print(f"Backup written: {ARCHIVE_PATH} ({os.path.getsize(ARCHIVE_PATH)} bytes)")

# OneDrive upload via Graph API (no rclone needed)
GRAPH_SCRIPT = os.path.expanduser("~/.config/hermy/onedrive_graph.py")
if os.path.exists(GRAPH_SCRIPT):
    try:
        result = subprocess.run(
            ["python3", GRAPH_SCRIPT, "upload", ARCHIVE_PATH, ONEDRIVE_BACKUP],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print(f"OneDrive uploaded: {ONEDRIVE_BACKUP}")
        else:
            print(f"OneDrive upload failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"OneDrive upload unavailable: {e}")
else:
    print("OneDrive upload unavailable: graph helper not found")

# Clean up stale temp files
for pattern in ["/opt/data/tmp*", "/opt/data/tmp_*"]:
    for f in glob.glob(pattern):
        if os.path.isfile(f) and f != ARCHIVE_PATH:
            os.remove(f)
            print(f"Removed stale temp: {f}")

# Clean up backups older than 7 days
for f in glob.glob(os.path.join(BACKUP_DIR, "hermes-backup-*.tar.gz")):
    if os.path.getmtime(f) < time.time() - 7 * 86400:
        os.remove(f)
        print(f"Removed old backup: {f}")

# Clean up state exports older than 7 days
export_dir = os.path.join(HOME_DIR, "exports")
for f in glob.glob(os.path.join(export_dir, "hermes-state-export-*.md")):
    if os.path.getmtime(f) < time.time() - 7 * 86400:
        os.remove(f)
        print(f"Removed old state export: {f}")

print("Backup complete.")
