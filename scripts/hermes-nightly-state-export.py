#!/usr/bin/env python3
"""Nightly state export — writes state docs and metadata to OneDrive."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/opt/data/repo/docs/state")
GRAPH_HELPER = Path("/opt/data/home/.config/hermy/onedrive_graph.py")
ONE_DRIVE_TARGET = "/Hermy/_system/state-exports"


def collect_state() -> dict[str, str]:
    """Read current state docs and metadata into a dict."""
    items: dict[str, str] = {}
    
    if REPO.exists():
        for md in sorted(REPO.glob("*.md")):
            items[md.name] = md.read_text()
    
    # Add memory contents if accessible
    mem_path = Path("/opt/data/memories")
    if mem_path.exists():
        for mem_file in mem_path.glob("*.md"):
            items[mem_file.name] = mem_file.read_text()
    
    # Add skill inventory
    skills_path = Path("/opt/data/skills")
    inventory: list[dict] = []
    if skills_path.exists():
        for skill_md in skills_path.rglob("SKILL.md"):
            name = skill_md.parent.name
            cat = skill_md.parent.parent.name
            inventory.append({"name": name, "category": cat})
    items["skill-inventory.json"] = json.dumps(inventory, indent=2)
    
    return items


def upload_to_onedrive(state: dict[str, str]) -> bool:
    """Upload state files to a dated folder in OneDrive."""
    if not GRAPH_HELPER.exists():
        return False
    
    try:
        ns: dict = {}
        exec(GRAPH_HELPER.read_text().replace('if __name__ == "__main__":', "if False:"), ns)
        
        root = ns["workspace"]()
        system = ns["ensure_folder"](root["id"], "_system")
        exports = ns["ensure_folder"](system["id"], "state-exports")
        
        today = dt.date.today().isoformat()
        dated = ns["ensure_folder"](exports["id"], today)
        
        for filename, content in state.items():
            ns["put_text"](dated["id"], filename, content)
        
        return True
    except Exception:
        return False


def main() -> int:
    print("Starting nightly state export...")
    
    state = collect_state()
    print(f"Collected {len(state)} state files")
    
    if upload_to_onedrive(state):
        print("Uploaded to OneDrive/Hermy/_system/state-exports/")
    else:
        print("ERROR: OneDrive upload failed")
        return 1
    
    print("State export complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
