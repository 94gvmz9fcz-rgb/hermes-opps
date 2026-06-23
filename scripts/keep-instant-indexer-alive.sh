#!/usr/bin/env bash
# keep-instant-indexer-alive.sh
# Minimal watchdog — ensures the instant indexer daemon is running.
# Runs every 5 minutes via cron.

PID_FILE="/opt/data/logs/instant-indexer.pid"
SCRIPT="/opt/data/repo/scripts/instant-indexer.py"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        exit 0  # Running fine
    fi
fi

# Dead or missing — restart
if [ -f "$SCRIPT" ]; then
    nohup python3 "$SCRIPT" > /dev/null 2>&1 &
    echo $! > "$PID_FILE"
    echo "restarted indexer (pid $!)"
else
    echo "indexer script not found at $SCRIPT"
fi
