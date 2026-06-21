#!/usr/bin/env python3
"""
Daily Inbox Scanner — checks OneDrive/Hermy/Inbox/ for new files
and reports to Josh in the morning standup.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path.home() / ".config" / "hermy"))
from onedrive_graph import graph, GRAPH

GRAPH_BASE = GRAPH

def list_inbox():
    """List contents of OneDrive/Hermy/Inbox/"""
    try:
        # Get Inbox folder
        resp = graph("GET", f"{GRAPH_BASE}/me/drive/root:/Hermy/Inbox")
        inbox_id = resp.get("id")
        if not inbox_id:
            return {"error": "Inbox folder not found", "items": []}
        
        # List children
        children = graph("GET", f"{GRAPH_BASE}/me/drive/items/{inbox_id}/children")
        items = children.get("value", [])
        
        result = []
        for item in items:
            file_info = item.get("file", {})
            result.append({
                "name": item.get("name"),
                "size": item.get("size", 0),
                "modified": item.get("lastModifiedDateTime"),
                "id": item.get("id"),
                "is_file": bool(file_info),
                "is_folder": bool(item.get("folder"))
            })
        
        return {"error": None, "items": result, "count": len(result)}
    
    except Exception as e:
        return {"error": str(e), "items": [], "count": 0}


def format_standup_line(stats):
    """Format the Inbox section for the morning standup."""
    if stats["error"]:
        return f"📥 Inbox: ⚠️ Could not scan — {stats['error']}"
    
    count = stats["count"]
    if count == 0:
        return "📥 Inbox: Empty ✓"
    
    # Summarize by file type
    exts = {}
    for item in stats["items"]:
        if item["is_folder"]:
            exts["📁"] = exts.get("📁", 0) + 1
        else:
            ext = os.path.splitext(item["name"])[1].lower() or "❓"
            exts[ext] = exts.get(ext, 0) + 1
    
    type_summary = ", ".join(f"{v} {k}" for k, v in sorted(exts.items()))
    
    lines = [f"📥 Inbox: {count} file{'s' if count > 1 else ''} ({type_summary})"]
    
    # List recent files (newest first)
    sorted_items = sorted(stats["items"], 
                         key=lambda x: x.get("modified", ""), reverse=True)
    for item in sorted_items[:5]:
        name = item["name"]
        if item["is_folder"]:
            lines.append(f"  📁 {name}")
        else:
            size_kb = item["size"] / 1024
            size_str = f"{size_kb:.0f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"
            lines.append(f"  📄 {name} ({size_str})")
    
    if count > 5:
        lines.append(f"  ... and {count - 5} more")
    
    return "\n".join(lines)


def main():
    stats = list_inbox()
    output = format_standup_line(stats)
    print("=== INBOX SCAN ===")
    print(output)
    
    # Track whether there's work to do
    if stats["count"] > 0:
        print("\nSTATUS=FILES_PENDING")
    elif stats["error"]:
        print(f"\nSTATUS=ERROR:{stats['error']}")
    else:
        print("\nSTATUS=CLEAN")


if __name__ == "__main__":
    main()
