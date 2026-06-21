#!/usr/bin/env python3
"""Nightly Hermes backup — tarball to /opt/data/backups/ and OneDrive."""
import subprocess, tarfile, os, sys
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

# OneDrive upload via rclone or gws
onedrive_cmd = ["rclone", "copy", ARCHIVE_PATH, f"hermes_onedrive:{ONEDRIVE_BACKUP}", "--verbose"]
try:
    result = subprocess.run(onedrive_cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        print(f"OneDrive uploaded: {ONEDRIVE_BACKUP}")
    else:
        print(f"OneDrive upload skipped or failed: {result.stderr.strip()}")
except (FileNotFoundError, subprocess.TimeoutExpired) as e:
    print(f"OneDrive upload unavailable: {e}")

# Clean up backups older than 7 days
import glob, time
for f in glob.glob(os.path.join(BACKUP_DIR, "hermes-backup-*.tar.gz")):
    if os.path.getmtime(f) < time.time() - 7 * 86400:
        os.remove(f)
        print(f"Removed old backup: {f}")

print("Backup complete.")
