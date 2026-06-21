#!/usr/bin/env python3
"""Test Airtable token: verify it works and can modify schema."""
import os, requests, json

# Read token from .env
with open("/opt/data/.env") as f:
    content = f.read()

TOKEN = ""
for line in content.split("\n"):
    if line.startswith("AIRTABLE_API_KEY="):
        TOKEN=line.split("=",1)[1].strip()
        break

print(f"Token loaded: {TOKEN[:20]}...{TOKEN[-10:]} (len={len(TOKEN)})")

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE_ID = "app6l2hwxinBLwHCa"

# Get tables
r = requests.get(f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables", headers=headers, timeout=10)
print(f"\nTables: {r.status_code}")
if r.status_code != 200:
    print(f"  Error: {r.text[:300]}")
    exit(1)

tables = r.json().get("tables", [])
for t in tables:
    print(f"  '{t['name']}' (id: {t['id']}) — {len(t.get('fields',[]))} fields")
    for f in t.get("fields", []):
        print(f"    {f['id']}: {f['name']} ({f['type']})")

# Try adding a field
table = tables[0]
table_name = table['name']
payload = {"fields": [{"name": "_test_field", "type": "singleLineText"}]}
r = requests.patch(
    f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_name}",
    headers=headers, json=payload, timeout=10
)
print(f"\nAdd field: {r.status_code}")
if r.status_code == 200:
    print("  ✅ Schema write WORKS!")
else:
    err = r.json()
    print(f"  ❌ {err.get('error',{}).get('message', r.text[:300])}")
