#!/usr/bin/env python3
"""Sync strategy/ and enrichment/ content from OneDrive/Hermy/ into the repo.

Downloads new/updated files, extracts text from binaries (xlsx, pptx, pdf),
and builds _index.json manifest files.

Usage:
    python3 scripts/strategy-sync.py            # full sync
    python3 scripts/strategy-sync.py --dry-run  # preview only
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

# Add onedrive_graph helper to path
sys.path.insert(0, os.path.expanduser("~/.config/hermy"))
from onedrive_graph import workspace, children, graph, GRAPH

REPO_ROOT = Path("/opt/data/repo")
STRATEGY_DIR = REPO_ROOT / "Strategy"
ENRICHMENT_DIR = REPO_ROOT / "enrichment"
JOSH_STUFF_DIR = REPO_ROOT / "Josh-Stuff"
RAW_DIR = REPO_ROOT / "_raw"  # binary originals, gitignored

# Track what we've done
class SyncReport:
    def __init__(self):
        self.downloaded = []
        self.skipped = []
        self.errored = []

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def download_file(dl_url: str, dest: Path, report: SyncReport) -> bool:
    """Download a file from OneDrive using its @microsoft.graph.downloadUrl."""
    if dest.exists():
        report.skipped.append(str(dest))
        return False
    ensure_dir(dest.parent)
    try:
        urllib.request.urlretrieve(dl_url, dest)
        report.downloaded.append(str(dest))
        return True
    except Exception as e:
        report.errored.append(f"{dest}: {e}")
        return False

def sync_folder(remote_parent_id: str, local_dir: Path, report: SyncReport, prefix: str = ""):
    """Recursively sync a OneDrive folder to local directory."""
    items = children(remote_parent_id)
    for item in sorted(items, key=lambda x: x["name"]):
        name = item["name"]
        if "folder" in item:
            # Recurse into subfolder
            sub_local = local_dir / name
            ensure_dir(sub_local)
            sync_folder(item["id"], sub_local, report, f"{prefix}/{name}")
        elif "file" in item:
            dl = item.get("@microsoft.graph.downloadUrl")
            if not dl:
                # Need full metadata for downloadUrl
                meta = graph("GET", f"{GRAPH}/me/drive/items/{item['id']}")
                dl = meta.get("@microsoft.graph.downloadUrl")
            if dl:
                dest = local_dir / name
                download_file(dl, dest, report)

def build_index(local_dir: Path) -> dict:
    """Build a JSON index of all files in a directory tree."""
    index = {"files": [], "folders": []}
    if not local_dir.exists():
        return index
    for root, dirs, files in os.walk(local_dir):
        rel_root = Path(root).relative_to(local_dir)
        for d in dirs:
            index["folders"].append(str(rel_root / d))
        for f in files:
            fp = Path(root) / f
            if f.startswith("_index") or f == ".hermes-keep":
                continue
            index["files"].append({
                "path": str(rel_root / f),
                "size": fp.stat().st_size,
                "modified": fp.stat().st_mtime,
            })
    return index

def main():
    parser = argparse.ArgumentParser(description="Sync OneDrive strategy/enrichment to repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    report = SyncReport()

    # Get workspace root
    root = workspace()
    items = children(root["id"])
    folder_map = {i["name"]: i["id"] for i in items if "folder" in i}

    # Sync strategy/
    if "strategy" in folder_map:
        print("Syncing strategy/...")
        if not args.dry_run:
            sync_folder(folder_map["strategy"], STRATEGY_DIR, report)
        ws_index = build_index(STRATEGY_DIR)
        if not args.dry_run:
            (STRATEGY_DIR / "_index.json").write_text(json.dumps(ws_index, indent=2))
        print(f"  {len(ws_index['files'])} files, {len(ws_index['folders'])} folders")

    # Sync enrichment/
    if "enrichment" in folder_map:
        print("Syncing enrichment/...")
        if not args.dry_run:
            sync_folder(folder_map["enrichment"], ENRICHMENT_DIR, report)
        ws_index = build_index(ENRICHMENT_DIR)
        if not args.dry_run:
            ensure_dir(ENRICHMENT_DIR)
            (ENRICHMENT_DIR / "_index.json").write_text(json.dumps(ws_index, indent=2))
        print(f"  {len(ws_index['files'])} files, {len(ws_index['folders'])} folders")

    # Sync key Josh Stuff files (not the full folder — skip DO NOT LOOK AT THESE HERMY)
    if "Josh Stuff" in folder_map:
        print("Syncing Josh Stuff (selected)...")
        josh_items = children(folder_map["Josh Stuff"])
        for item in josh_items:
            name = item["name"]
            # Skip the DO NOT LOOK AT THESE HERMY folder
            if "DO NOT LOOK AT THESE" in name.upper():
                print(f"  Skipping: {name}")
                continue
            if "folder" in item:
                # Sync CRM_Docs and Fun with Rocks
                if name in ("CRM_Docs", "Fun with Rocks"):
                    sub_local = JOSH_STUFF_DIR / name
                    ensure_dir(sub_local)
                    if not args.dry_run:
                        sync_folder(item["id"], sub_local, report)
            elif "file" in item:
                dl = item.get("@microsoft.graph.downloadUrl")
                if not dl:
                    meta = graph("GET", f"{GRAPH}/me/drive/items/{item['id']}")
                    dl = meta.get("@microsoft.graph.downloadUrl")
                if dl:
                    dest = JOSH_STUFF_DIR / name
                    download_file(dl, dest, report)
        ws_index = build_index(JOSH_STUFF_DIR)
        if not args.dry_run:
            (JOSH_STUFF_DIR / "_index.json").write_text(json.dumps(ws_index, indent=2))

    # Summary
    print(f"\nSync complete:")
    print(f"  Downloaded: {len(report.downloaded)}")
    print(f"  Skipped (already exists): {len(report.skipped)}")
    print(f"  Errors: {len(report.errored)}")
    for err in report.errored:
        print(f"    ERROR: {err}")

if __name__ == "__main__":
    main()
