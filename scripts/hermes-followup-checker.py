#!/usr/bin/env python3
"""
Follow-up Checker — called by cron every 5 minutes.
Checks for due reminders, fires them, and outputs delivery messages.

Output is delivered to Josh via Telegram (deliver: origin).
Silent when nothing is due.
"""

import sys
import os
from pathlib import Path

# Add the hermes scripts dir to path and load the module (file has a dash, not underscore)
# NOTE: Path.home() differs under cron (HOME=/opt/data) vs interactive (HOME=/opt/data/home).
# Resolve robustly: the deployed checker and hermes-followup.py live side-by-side in the
# script's own directory (/opt/data/scripts on the droplet). Fall back to the legacy
# ~/.hermes/scripts layouts only if the sibling isn't there.
_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = Path(_HERE) if (Path(_HERE) / "hermes-followup.py").exists() else None
if SCRIPTS_DIR is None:
    for _cand in (Path(os.environ.get("HERMES_HOME", "/opt/data")) / ".hermes" / "scripts",
                  Path("/opt/data/home/.hermes/scripts")):
        if (_cand / "hermes-followup.py").exists():
            SCRIPTS_DIR = _cand
            break
if SCRIPTS_DIR is None:
    SCRIPTS_DIR = Path(_HERE)  # last resort: let the loader raise a clear error
sys.path.insert(0, str(SCRIPTS_DIR))
import importlib.util as _iu
_spec = _iu.spec_from_file_location("hermes_followup", str(SCRIPTS_DIR / "hermes-followup.py"))
_mod = _iu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
cmd_fire = _mod.cmd_fire
cmd_count = _mod.cmd_count

def main():
    count_before = cmd_count().get("count", 0)
    result = cmd_fire()
    
    if result["count"] == 0:
        # Silent — no output unless something fires
        return
    
    # Build a Telegram-friendly message
    fired = result["fired"]
    
    lines = [
        "⏰ **Follow-ups due:**",
        ""
    ]
    
    for r in fired:
        tag = f" [{r['tag']}]" if r.get('tag') else ""
        lines.append(f"• **#{r['id']}**: {r['title']}{tag}")
        if r.get("notes"):
            lines.append(f"  _{r['notes']}_")
    
    remaining = cmd_count().get("count", 0)
    lines.append("")
    if remaining > 0:
        lines.append(f"📋 {remaining} follow-up(s) still pending.")
    else:
        lines.append("✅ All caught up!")
    
    print("\n".join(lines))


if __name__ == "__main__":
    main()
