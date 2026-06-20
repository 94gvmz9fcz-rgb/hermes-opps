#!/usr/bin/env bash
set -euo pipefail

MODEL="/opt/data/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf"
LLAMA_SERVER="/opt/data/bin/llama-server"
HOST="127.0.0.1"
PORT="18080"
LOG_DIR="/opt/data/logs"
LOG_FILE="$LOG_DIR/llama-server-qwen2.5-0.5b.log"
PID_FILE="/opt/data/local/llama.cpp/llama-server-qwen2.5-0.5b.pid"

mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")"

if [[ ! -x "$LLAMA_SERVER" ]]; then
  echo "missing llama-server at $LLAMA_SERVER" >&2
  exit 1
fi

if [[ ! -s "$MODEL" ]]; then
  echo "missing model at $MODEL" >&2
  exit 1
fi

if [[ -s "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE")"
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "llama-server already running pid=$old_pid"
    exit 0
  fi
fi

nohup "$LLAMA_SERVER" \
  -m "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  -c 2048 \
  -t 2 \
  >"$LOG_FILE" 2>&1 &

pid="$!"
echo "$pid" > "$PID_FILE"
echo "started llama-server pid=$pid url=http://$HOST:$PORT log=$LOG_FILE"
