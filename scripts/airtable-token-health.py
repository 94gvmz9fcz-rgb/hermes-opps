#!/usr/bin/env python3
"""
Airtable Token Health Check — tests the PAT in .env and reports if it's valid.
Quiet if healthy, loud if dead.

Part of the T001 rotation fix. Runs as part of the health monitor cron.
"""

import base64
import json
import os
import sys
import requests
from datetime import datetime, timezone

# ── Config ──
BASE_ID = "app6l2hwxinBLwHCa"        # Jermy CRM
B32_PATH = "/opt/data/tmp/airtable_b32.txt"
ENV_PATH = "/opt/data/.env"
STATE_PATH = os.path.expanduser("~/.airtable-token-health.json")


def decode_b32_token():
    """Read and decode the base32-encoded token."""
    if not os.path.exists(B32_PATH):
        return None, "base32 file not found"
    try:
        with open(B32_PATH) as f:
            encoded = f.read().strip()
        return base64.b32decode(encoded).decode(), None
    except Exception as e:
        return None, f"decode failed: {e}"


def test_token(token):
    """Test the token against the Airtable API."""
    try:
        r = requests.get(
            f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            tables = r.json().get("tables", [])
            table_names = [t["name"] for t in tables]
            return {"status": "ok", "tables": table_names, "count": len(tables)}
        elif r.status_code == 401:
            return {"status": "dead", "code": 401, "detail": "Unauthorized — token likely expired/revoked"}
        else:
            return {"status": "error", "code": r.status_code, "detail": r.text[:200]}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "code": 0, "detail": "Network error — cannot reach Airtable"}
    except Exception as e:
        return {"status": "error", "code": 0, "detail": str(e)}


def save_state(result):
    """Persist the last health check result for trend tracking."""
    state = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "status": result["status"],
        "result": result,
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    token, err = decode_b32_token()
    if err:
        result = {"status": "error", "detail": err}
        save_state(result)
        print(f"❌ Airtable token health: {err}", file=sys.stderr)
        return 1

    result = test_token(token)
    save_state(result)

    if result["status"] == "ok":
        # Quiet — token is fine
        return 0
    elif result["status"] == "dead":
        print(f"🔴 Airtable token EXPIRED! Tables unreachable. Need new PAT from Airtable account page.")
        print(f"   Update: store base32 of new token at {B32_PATH}")
        print(f"   Then run: python3 {__file__}")
        return 1
    else:
        print(f"⚠️ Airtable token check: {result.get('detail', 'unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
