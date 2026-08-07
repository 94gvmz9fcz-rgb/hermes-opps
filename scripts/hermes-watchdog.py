#!/usr/bin/env python3
"""
Hermes Watchdog v2 — process health monitor.

Silent when healthy. Alerts only when Hermes gateway process dies.
No heartbeat file needed. Just checks: is the process running?

v2 changes: absolute paths, no heartbeat, 3 failures = alert, 15min cooldown.
"""

import os, time, subprocess, sys, json

# ── Config ──
# State file lives under HERMES_HOME (canonical /opt/data), NOT /opt/data/home
# (which did not migrate to the droplet). Matches the process argv on both
# launch styles: `hermes gateway run` (source box) and
# `python -m hermes_cli.main gateway run` (droplet venv).
STATE_FILE = os.path.join(os.environ.get("HERMES_HOME", "/opt/data"),
                          ".hermes", ".watchdog_state.json")
PROCESS_MATCH = r"hermes_cli\.main gateway run|hermes gateway run"
MAX_CONSECUTIVE_FAILURES = 3
# ────────────


def check_process():
    try:
        r = subprocess.run(["pgrep", "-f", PROCESS_MATCH], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"consecutive_failures": 0, "last_alert": 0}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"consecutive_failures": 0, "last_alert": 0}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def main():
    state = load_state()
    now = time.time()

    if check_process():
        state["consecutive_failures"] = 0
        save_state(state)
        sys.exit(0)

    # Process not found
    state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
    save_state(state)

    if state["consecutive_failures"] < MAX_CONSECUTIVE_FAILURES:
        sys.exit(0)

    if now - state.get("last_alert", 0) < 900:
        sys.exit(0)

    state["last_alert"] = now
    save_state(state)

    print("\n".join([
        "⚠️  *Hermes Watchdog Alert*",
        "",
        "🔴 *Process*: Hermes gateway is NOT running.",
        "   → Consecutive failures: {}".format(state["consecutive_failures"]),
        "   → The systemd unit `hermes-gateway.service` should auto-restart it; if not, on the droplet run: `systemctl --user restart hermes-gateway`.",
    ]))


if __name__ == "__main__":
    main()
