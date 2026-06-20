#!/usr/bin/env python3
"""Hermy model integration health checks.

Checks configured direct/cloud/local model routes without printing secrets.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ENV_FILES = [Path("/opt/data/.env"), Path.home() / ".hermes" / ".env"]


def load_env() -> list[str]:
    loaded: list[str] = []
    for path in ENV_FILES:
        if not path.exists():
            continue
        loaded.append(str(path))
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return loaded


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 60) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read(500).decode("utf-8", "ignore")
        return exc.code, body
    except Exception as exc:  # pragma: no cover - diagnostic script
        return 0, f"{type(exc).__name__}: {str(exc)[:300]}"


def check_openrouter() -> tuple[bool, str]:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return False, "missing OPENROUTER_API_KEY"
    status, data = post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "model": "qwen/qwen-2.5-7b-instruct",
            "messages": [{"role": "user", "content": "Reply with exactly: Hermy OpenRouter online"}],
            "max_tokens": 20,
            "temperature": 0,
        },
        headers={
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/94gvmz9fcz-rgb/hermes-opps",
            "X-Title": "Hermy Model Health",
        },
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"HTTP {status}: {data}"
    content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
    usage = data.get("usage") or {}
    return bool(content), f"reply={content!r}, tokens={usage.get('total_tokens')}, cost={usage.get('cost')}"


def check_deepseek() -> tuple[bool, str]:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        return False, "missing DEEPSEEK_API_KEY"
    status, data = post_json(
        "https://api.deepseek.com/chat/completions",
        {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Reply with exactly: Hermy DeepSeek online"}],
            "max_tokens": 20,
            "temperature": 0,
        },
        headers={"Authorization": f"Bearer {key}"},
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"HTTP {status}: {data}"
    content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
    usage = data.get("usage") or {}
    return bool(content), f"reply={content!r}, tokens={usage.get('total_tokens')}"


def check_gemini() -> tuple[bool, str]:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return False, "missing GEMINI_API_KEY / GOOGLE_API_KEY"
    status, data = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}",
        {
            "contents": [{"parts": [{"text": "Reply with exactly: Hermy Gemini online"}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 30},
        },
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"HTTP {status}: {str(data).replace(key, '[REDACTED]')}"
    content = "".join(
        part.get("text", "")
        for candidate in data.get("candidates", [])
        for part in candidate.get("content", {}).get("parts", [])
    ).strip()
    usage = data.get("usageMetadata") or {}
    return bool(content), f"reply={content!r}, tokens={usage.get('totalTokenCount')}"


def check_local_llama() -> tuple[bool, str]:
    status, data = post_json(
        "http://127.0.0.1:18080/v1/chat/completions",
        {
            "messages": [{"role": "user", "content": "Reply with exactly: Hermy local online"}],
            "max_tokens": 20,
            "temperature": 0,
        },
        timeout=90,
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"HTTP {status}: {data}"
    content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
    usage = data.get("usage") or {}
    return bool(content), f"reply={content!r}, tokens={usage.get('total_tokens')}"


def main() -> int:
    loaded = load_env()
    print("# Hermy Model Health")
    print(f"env_files_loaded: {', '.join(loaded) if loaded else 'none'}")
    print(f"hermes_cli: {shutil.which('hermes') or '/opt/hermes/.venv/bin/hermes if installed'}")
    checks = [
        ("openrouter_qwen", check_openrouter),
        ("deepseek_direct", check_deepseek),
        ("gemini_direct", check_gemini),
        ("local_llama_cpp", check_local_llama),
    ]
    all_ok = True
    for name, fn in checks:
        ok, detail = fn()
        all_ok = all_ok and ok
        print(f"{name}: {'ok' if ok else 'failed'} — {detail}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
