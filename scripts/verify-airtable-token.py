#!/usr/bin/env python3
"""Verify the Airtable token works."""
import base64
from pathlib import Path
import requests

env_path = Path.home() / '.hermes' / '.env'
with open(env_path) as f:
    for raw in f:
        if 'AIRTABLE_TOKEN' in raw:
            val = raw.strip().split('=', 1)[1]
            break
    else:
        print("ERROR: AIRTABLE_TOKEN not found")
        raise SystemExit(1)

# Try base64 decode
try:
    token = base64.b64decode(val).decode()
except Exception:
    token = val

print(f"Token found: {token[:20]}... ({len(token)} chars)")

# Test meta/bases
resp = requests.get(
    "https://api.airtable.com/v0/meta/bases",
    headers={"Authorization": f"Bearer {token}"},
)
if resp.status_code == 200:
    bases = resp.json().get("bases", [])
    print(f"\n✅ Airtable API OK — {len(bases)} bases accessible")
    for b in bases:
        print(f"  {b['id']}  {b.get('name', 'unnamed')}")
else:
    print(f"❌ API error {resp.status_code}")
    raise SystemExit(1)

# Check our target base
target_id = "app6l2hwxinBLwHCa"
target = next((b for b in bases if b['id'] == target_id), None)
if target:
    print(f"\n✅ Target base '{target.get('name')}' accessible")
else:
    all_ids = [b['id'] for b in bases]
    print(f"\n⚠️ Target {target_id} not accessible. Available: {all_ids}")
