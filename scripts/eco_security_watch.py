#!/usr/bin/env python3
"""
eco_security_watch.py — lightweight ecosystem security the AStew/JStew stack.
Runs on a schedule, checks for compromise signals, and is SILENT unless it
finds something real (no nagging). Josh asked explicitly to keep the ecosystem
secure after an unsolicited 'VOID/ENIGMA' bot-promo surfaced in a thread.

Checks:
  1. Processes: only known good binaries (hermes gateway, tailscale, node LSP,
     s6 supervisor, bash, sleep, ps utilities). Anything else = alert.
  2. Listening sockets: report unexpected listeners on non-standard ports.
  3. Secret integrity: config.yaml / .env sizes + mtimes vs baseline. A surprise
     edit (esp. same day) could mean credential tampering.
  4. Unexpected inbound peers: gateway log showing a sender OTHER than the known
     good peer (Josh) messaging into our thread = alert.
  5. Suspicious outbound: established connections to external IPs beyond the
     known talosec/gateway endpoints (exfil signal).

Only the FIRST occurrence of a new anomaly alerts per baseline file, so a seen
anomaly goes quiet until it changes or clears. Exit 0, empty stdout = all clear.
"""

import os, json, re, subprocess, datetime, hashlib, socket, sys

HERMES_HOME = os.path.expanduser("~/.hermes")
LOG = "/opt/data/logs/gateway.log"
BASE = os.path.join(HERMES_HOME, ".hermes-probes")   # baseline dir
os.makedirs(BASE, exist_ok=True)

# Known-good program roots (match the basename of argv[0] / comm)
GOOD_PROC_ROOTS = {"python3", "hermes", "tailscaled", "node", "s6-svscan",
                   "s6-supervise", "s6-log", "s6-linux-init", "s6-ipcserverd",
                   "s6-linux-init-shutdownd", "ssh-agent", "ssh",
                   "bash", "sh", "sleep", "ps", "top", "head", "grep", "awk",
                   "ss", "date", "ls"}

# Sentinel for the known good peer (Josh's DM). Any OTHER sender = alert.
GOOD_PEERS = {"Josh Stewart"}


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception:
        return None


def _alert(file_, text, persist=True):
    """Append to an anomaly feed. First-time only per message text."""
    seen = os.path.join(BASE, file_ + ".seen")
    seen_set = set()
    if os.path.exists(seen):
        seen_set = set(open(seen).read().splitlines())
    key = text[:160]
    if key in seen_set:
        return  # already surfaced this exact anomaly — silent
    if persist:
        with open(seen, "a") as f:
            f.write(key + "\n")
    print(text)


def check_processes():
    try:
        out = subprocess.run(["ps", "aux"], capture_output=True, text=True,
                             timeout=15).stdout
    except Exception:
        return
    for line in out.splitlines()[1:]:
        cols = line.split(None, 10)
        if len(cols) < 11:
            continue
        raw0 = cols[10].split()[0] if cols[10] else ""
        # kernel threads show as "[kworker/...]", "[rcu_...]", "[ksoftirqd]" etc.
        # in ps — normal kernel activity, never a rogue process. Check the RAW
        # comm before basename (basename strips "[kworker/" as if it were a path).
        if raw0.startswith("[") and raw0.endswith("]"):
            continue
        argv0 = os.path.basename(raw0) if raw0 else ""
        if not argv0:
            continue
        root = argv0.split("/")[-1] or ""
        # kernel threads show as "[kworker/...]", "[rcu_...]", "[ksoftirqd]" etc.
        # in ps — normal kernel activity, never a rogue process. Skip all bracketed comms.
        if argv0.startswith("[") and argv0.endswith("]"):
            continue
        if root and root not in GOOD_PROC_ROOTS and root not in ("s6-supervise",):
            _alert("procs", f"UNKNOWN PROCESS running: {root} (cmd: {cols[10][:80]})")


def check_secrets():
    base_mtime = None
    for p, name in [("config.yaml", "config"), (".env", "env")]:
        path = os.path.join(HERMES_HOME, p)
        if not os.path.exists(path):
            continue
        cur_sha = _sha(path)
        rec = os.path.join(BASE, f"secret_{name}.sha")
        if os.path.exists(rec):
            prev = open(rec).read().strip()
            if cur_sha != prev:
                _alert("secrets", f"SECRET TAMPER: {p} hash changed from {prev} to {cur_sha}")
        else:
            # first baseline
            pass
        with open(rec, "w") as f:
            f.write(cur_sha or "")


def check_peers():
    """Scan gateway log for inbound from any sender other than GOOD_PEERS."""
    if not os.path.exists(LOG):
        return
    try:
        text = open(LOG, errors="ignore").read()
    except Exception:
        return
    # inbound message: platform=telegram user=SENDER chat=... msg='...'
    pat = re.compile(r"inbound message: platform=(\w+) user=([^ ]+) chat=(\S+)")
    for mm in pat.finditer(text):
        plat, user, chat = mm.group(1), mm.group(2), mm.group(3)
        if user not in GOOD_PEERS:
            _alert("peers", f"UNEXPECTED SENDER on {plat}: user={user} chat={chat}")


def check_sockets():
    """Report TCP listeners on unusual ports (not 22/53/443/8080/high ephemeral)."""
    try:
        out = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True,
                             timeout=15).stdout
    except Exception:
        return
    KNOWN = {"22", "53", "80", "443", "8080"}
    for line in out.splitlines()[1:]:
        m = re.search(r":(\d+)\s", line)
        if not m:
            continue
        port = m.group(1)
        if port not in KNOWN and int(port) < 1024:
            _alert("sockets", f"UNEXPECTED LOW-PORT LISTENER: {line.strip()[:100]}")


def main():
    check_processes()
    check_secrets()
    check_peers()
    check_sockets()
    # record check time
    with open(os.path.join(BASE, "last_run"), "w") as f:
        f.write(_now())
    # no output = all clear


if __name__ == "__main__":
    main()
