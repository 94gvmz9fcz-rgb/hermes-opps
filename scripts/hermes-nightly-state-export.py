#!/usr/bin/env python3
"""Nightly state export — sync docs/state/* to OneDrive."""
import subprocess, os, sys, shutil
from datetime import date
import tempfile

REPO_DIR = "/opt/data/repo"
STATE_DIR = os.path.join(REPO_DIR, "docs", "state")
HOME_DIR = "/opt/data"
TODAY = date.today().isoformat()
EXPORT_NAME = f"hermes-state-export-{TODAY}.md"
LOCAL_EXPORT = os.path.join(HOME_DIR, "exports", EXPORT_NAME)

os.makedirs(os.path.join(HOME_DIR, "exports"), exist_ok=True)

if not os.path.isdir(STATE_DIR):
    print("State directory not found — nothing to export.")
    sys.exit(1)

# Collect and concatenate all state docs
state_files = sorted(f for f in os.listdir(STATE_DIR) if f.endswith(".md"))
if not state_files:
    print("No state files found.")
    sys.exit(0)

with open(LOCAL_EXPORT, "w") as out:
    out.write(f"# Hermes State Export — {TODAY}\n\n")
    for fname in state_files:
        fpath = os.path.join(STATE_DIR, fname)
        with open(fpath) as f:
            out.write(f"---\n## {fname}\n\n")
            out.write(f.read())
            out.write("\n\n")

print(f"State export written: {LOCAL_EXPORT} ({os.path.getsize(LOCAL_EXPORT)} bytes)")

# OneDrive upload
onedrive_path = f"OneDrive/Hermy/_system/state-exports/{TODAY}/"
onedrive_cmd = ["rclone", "copy", LOCAL_EXPORT, f"hermes_onedrive:{onedrive_path}", "--verbose"]
try:
    result = subprocess.run(onedrive_cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        print(f"OneDrive uploaded: {onedrive_path}{EXPORT_NAME}")
    else:
        print(f"OneDrive upload skipped or failed: {result.stderr.strip()}")
except (FileNotFoundError, subprocess.TimeoutExpired) as e:
    print(f"OneDrive upload unavailable: {e}")

print("State export complete.")
