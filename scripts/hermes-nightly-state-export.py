#!/usr/bin/env python3
"""Nightly state export — sync docs/state/* to OneDrive."""
import glob, subprocess, os, sys, shutil, time
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

# OneDrive upload via Graph API (no rclone needed)
GRAPH_SCRIPT = os.path.expanduser("~/.config/hermy/onedrive_graph.py")
onedrive_path = f"Hermy/_system/state-exports/{TODAY}/{EXPORT_NAME}"
if os.path.exists(GRAPH_SCRIPT):
    try:
        result = subprocess.run(
            ["python3", GRAPH_SCRIPT, "upload", LOCAL_EXPORT, onedrive_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print(f"OneDrive uploaded: {onedrive_path}")
        else:
            print(f"OneDrive upload failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"OneDrive upload unavailable: {e}")
else:
    print("OneDrive upload unavailable: graph helper not found")

print("State export complete.")

# --- EOL and Temp Pruning ---

# Clean up stale temp files
for pattern in ["/opt/data/tmp*", "/opt/data/tmp_*"]:
    for f in glob.glob(pattern):
        if os.path.isfile(f):
            os.remove(f)
            print(f"Removed stale temp: {f}")

# Clean up local exports older than 7 days
export_dir = os.path.dirname(LOCAL_EXPORT)
for f in glob.glob(os.path.join(export_dir, "hermes-state-export-*.md")):
    if os.path.getmtime(f) < time.time() - 7 * 86400:
        os.remove(f)
        print(f"Removed old export: {f}")
