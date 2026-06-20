#!/usr/bin/env python3
"""Nightly Hermes system backup — writes tarball to /opt/data/backups/ and OneDrive."""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

EXPORT_DIR = Path("/opt/data/exports")
BACKUP_DIR = Path("/opt/data/backups")
HERMES_HOME = Path("/opt/data")
REPO = Path("/opt/data/repo")
SKILLS = Path("/opt/data/skills")
CONFIG = Path("/opt/data/config.yaml")
ENV = Path("/opt/data/.env")
GRAPH_HELPER = Path("/opt/data/home/.config/hermy/onedrive_graph.py")
ONE_DRIVE_BACKUP_PATH = "/Hermy/_backups"


def export_sessions() -> str | None:
    """Dump recent sessions to a dated export file."""
    hermes_cli = "/opt/hermes/.venv/bin/hermes"
    if not os.path.isfile(hermes_cli):
        return None
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / f"sessions-{dt.date.today().isoformat()}.jsonl"
    subprocess.run(
        [hermes_cli, "sessions", "export", str(path)],
        capture_output=True, timeout=120, env={**os.environ, "HOME": "/opt/data/home"},
    )
    return str(path) if path.exists() and path.stat().st_size > 0 else None


def create_tarball() -> str | None:
    """Create compressed backup tarball."""
    today = dt.date.today().isoformat()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKUP_DIR / f"hermes-backup-{today}.tar.gz"
    
    sources: list[str] = []
    includes: list[str] = []
    
    if CONFIG.exists():
        sources.append(str(CONFIG))
        includes.append(str(CONFIG))
    if ENV.exists():
        sources.append(str(ENV))
    
    sources.append(str(SKILLS))
    includes.append(str(SKILLS))
    
    if REPO.exists():
        includes.append(str(REPO / ".git"))
        includes.append(str(REPO / "docs"))
        includes.append(str(REPO / "scripts"))
    
    for export in EXPORT_DIR.glob("*.jsonl"):
        sources.append(str(export))
        includes.append(str(export))
    
    cmd = ["tar", "-czf", str(path), "--exclude=*.pyc", "--exclude=__pycache__", "--exclude=*.pid", "--exclude=*.log"] + includes
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    return str(path) if result.returncode == 0 else None


def upload_to_onedrive(local_path: str) -> bool:
    """Upload backup file to OneDrive/_backups/."""
    if not os.path.isfile(GRAPH_HELPER) or not os.path.isfile(local_path):
        return False
    
    try:
        import sys as _sys
        _sys.path.insert(0, str(GRAPH_HELPER.parent))
        ns: dict = {}
        exec(GRAPH_HELPER.read_text().replace('if __name__ == "__main__":', "if False:"), ns)
        
        root = ns["workspace"]()
        backups = ns["ensure_folder"](root["id"], "_backups")
        
        from pathlib import Path as _Path
        content = _Path(local_path).read_bytes()
        filename = _Path(local_path).name
        
        ns["put_text"](backups["id"], filename, content.decode("latin-1"))
        return True
    except Exception:
        return False


def prune_old_backups() -> None:
    """Remove backups older than 7 days locally."""
    now = dt.datetime.now(dt.UTC).timestamp()
    for path in sorted(BACKUP_DIR.glob("hermes-backup-*.tar.gz"), reverse=True)[7:]:
        if path.stat().st_mtime < now - 7 * 86400:
            path.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    
    print("Starting nightly backup...")
    
    export_path = export_sessions()
    if export_path:
        print(f"Sessions exported: {export_path}")
    
    tarball = create_tarball()
    if tarball:
        print(f"Tarball created: {tarball}")
    else:
        errors.append("Tarball creation failed")
    
    if tarball:
        if upload_to_onedrive(tarball):
            print("Uploaded to OneDrive")
        else:
            errors.append("OneDrive upload failed")
        prune_old_backups()
        print("Old backups pruned")
    
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    
    print("Backup complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
