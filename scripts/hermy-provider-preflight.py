#!/usr/bin/env python3
"""Preflight Hermy's cost-routing provider setup without printing secrets.

This script is intentionally read-only. It reports which provider credentials
appear present in the current environment and whether key local commands are
available. It never prints token values.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


ENV_KEYS = [
    "OPENROUTER_API_KEY",
    "DEEPSEEK_API_KEY",
    "DASHSCOPE_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GROQ_API_KEY",
    "VOICE_TOOLS_OPENAI_KEY",
]

COMMANDS = ["hermes", "ollama", "uv", "python3", "git"]
DEFAULT_ENV_FILES = [Path("/opt/data/.env"), Path.home() / ".hermes" / ".env"]


def load_env_file(path: Path) -> bool:
    """Load KEY=VALUE lines from a local env file without printing values."""
    if not path.exists():
        return False
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
    return True


def command_version(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        return "missing"
    try:
        result = subprocess.run(
            [cmd, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5,
            check=False,
        )
        first = (result.stdout or "").splitlines()[0] if result.stdout else "version unavailable"
        return f"{path} — {first}"
    except Exception as exc:  # pragma: no cover - diagnostic script
        return f"{path} — version check failed: {exc}"


def openrouter_smoke_test() -> tuple[bool, str]:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return False, "missing OPENROUTER_API_KEY"
    payload = {
        "model": "qwen/qwen-2.5-7b-instruct",
        "messages": [{"role": "user", "content": "Reply with exactly: Hermy cheap route online"}],
        "max_tokens": 20,
        "temperature": 0,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/94gvmz9fcz-rgb/hermes-opps",
            "X-Title": "Hermy Cost Routing Preflight",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.load(response)
        choice = (data.get("choices") or [{}])[0]
        content = ((choice.get("message") or {}).get("content") or "").strip()
        usage = data.get("usage") or {}
        if content:
            cost = usage.get("cost")
            cost_text = f", cost={cost}" if cost is not None else ""
            return True, f"qwen smoke test ok: {content!r}, tokens={usage.get('total_tokens')}{cost_text}"
        return False, "OpenRouter returned no message content"
    except urllib.error.HTTPError as exc:
        body = exc.read(240).decode("utf-8", "ignore")
        return False, f"HTTP {exc.code}: {body}"
    except Exception as exc:  # pragma: no cover - diagnostic script
        return False, f"{type(exc).__name__}: {str(exc)[:240]}"


def main() -> int:
    print("# Hermy Provider / Local Inference Preflight")
    print()

    loaded = [str(path) for path in DEFAULT_ENV_FILES if load_env_file(path)]
    print("## Env files loaded")
    print("- " + (", ".join(loaded) if loaded else "none"))
    print()

    print("## Environment credentials")
    for key in ENV_KEYS:
        print(f"- {key}: {'present' if os.getenv(key) else 'missing'}")
    print()

    print("## Commands")
    for cmd in COMMANDS:
        print(f"- {cmd}: {command_version(cmd)}")
    print()

    print("## OpenRouter smoke test")
    ok, detail = openrouter_smoke_test()
    print(f"- {'ok' if ok else 'failed'}: {detail}")
    print()

    print("## Recommended next actions")
    if not os.getenv("OPENROUTER_API_KEY"):
        print("- Add OpenRouter through Hermes auth/config before cheap-model routing tests.")
    if not shutil.which("hermes"):
        print("- Run/restart from the real Hermes CLI environment; `hermes` is not on this PATH.")
    if not shutil.which("ollama"):
        print("- Treat Ollama/local inference as uninstalled here; evaluate iPad/local lane separately.")
    print("- Keep secrets out of repo docs and command output.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
