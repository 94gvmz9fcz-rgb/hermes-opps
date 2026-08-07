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
POD_DIR = os.path.join(HOME_DIR, "kalshi-pod")
paths = [
    os.path.join(HOME_DIR, "config.yaml"),          # the real Hermes config (NOT .hermes/config.yaml — that path does not exist on the droplet)
    os.path.join(HOME_DIR, ".env"),
    os.path.join(HOME_DIR, "skills"),
    os.path.join(REPO_DIR, "docs"),
    os.path.join(REPO_DIR, "scripts"),
    os.path.join(HOME_DIR, "exports"),          # state exports + hybrid-db.sql dump
    os.path.join(HOME_DIR, "cron"),             # jobs.json registry — restores the whole fleet on DR
    os.path.join(HOME_DIR, ".hermes"),              # memory.md, watchdog state, cron scratch — the durable agent state
    # ---- ENGINE DURABILITY (the whole prediction engine) ----
    POD_DIR,   # all python + cases/ ledgers (track_record, pmus_paperlog, KXCPI, gate state) + RESTORE.md
    # NOTE: the API signing credential (/opt/data/.polymarket-us-key) is
    # intentionally NOT tarballed — live secret, KYC-recoverable via the
    # polymarket.us portal (see RESTORE.md). Excluded in _filter below.
]

# Exclude the raw credential + pyc from the pod tarball
def _filter(tarinfo):
    name = tarinfo.name
    if name.endswith(".pyc") or "/__pycache__/" in name:
        return None
    if ".polymarket-us-key" in name:
        return None  # never ship the signing secret in a cleartext tarball
    return tarinfo

existing = [p for p in paths if os.path.exists(p)]

# Postgres dump (hybrid DB) — DR completeness: the DB is small today; dump it
# into exports/ so the tarball carries it (exports is in `paths` below).
try:
    os.makedirs(os.path.join(HOME_DIR, "exports"), exist_ok=True)
    dump_path = os.path.join(HOME_DIR, "exports", "hybrid-db.sql")
    with open(dump_path, "w") as f:
        subprocess.run(["su", "postgres", "-c", "pg_dump hybrid"], stdout=f,
                       timeout=120, check=False)
    print(f"PG dump written: {dump_path}")
except Exception as e:
    print(f"PG dump skipped: {e}")

if not existing:
    print("Nothing to back up — no source paths found.")
    sys.exit(1)

with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
    for path in existing:
        tar.add(path, arcname=os.path.relpath(path, HOME_DIR), filter=_filter)

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

# R2 offsite backup (Cloudflare) — primary off-box durability (no deps)
R2KEYS = "/opt/data/tmp/.r2keys.env"
if os.path.exists(R2KEYS):
    try:
        env = dict(os.environ)
        for line in open(R2KEYS):
            line = line.strip()
            if line.startswith("export "):
                k, _, v = line[7:].partition("=")
                env[k.strip()] = v.strip()
        up = subprocess.run(["python3", "/opt/data/scripts/r2_upload.py", ARCHIVE_PATH],
                            capture_output=True, text=True, timeout=300, env=env)
        if up.returncode == 0:
            print(f"R2 uploaded: {up.stdout.strip()}")
        else:
            print(f"R2 upload failed: {up.stderr.strip()[:200]}")
        pr = subprocess.run(["python3", "/opt/data/scripts/r2_upload.py", "--prune"],
                            capture_output=True, text=True, timeout=120, env=env)
        if pr.returncode == 0:
            print(f"R2 prune: {pr.stdout.strip()}")
    except Exception as e:
        print(f"R2 upload unavailable: {e}")
else:
    print("R2 upload unavailable: keys file not found")

print("Backup complete.")
