#!/usr/bin/env python3
"""Preflight Hermy's cost-routing provider setup without printing secrets.

This script is intentionally read-only. It reports which provider credentials
appear present in the current environment and whether key local commands are
available. It never prints token values.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass


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


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


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


def main() -> int:
    print("# Hermy Provider / Local Inference Preflight")
    print()

    print("## Environment credentials")
    for key in ENV_KEYS:
        print(f"- {key}: {'present' if os.getenv(key) else 'missing'}")
    print()

    print("## Commands")
    for cmd in COMMANDS:
        print(f"- {cmd}: {command_version(cmd)}")
    print()

    print("## Recommended next actions")
    if not os.getenv("OPENROUTER_API_KEY"):
        print("- Add OpenRouter through Hermes auth/config before cheap-model routing tests.")
    if not shutil.which("hermes"):
        print("- Run config changes from the real Hermes CLI environment; `hermes` is not on this PATH.")
    if not shutil.which("ollama"):
        print("- Treat Ollama/local inference as uninstalled here; evaluate iPad/local lane separately.")
    print("- Keep secrets out of repo docs and command output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
