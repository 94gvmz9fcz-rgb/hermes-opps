#!/usr/bin/env python3
"""Poll R2 bucket for new emails and report them."""
import urllib.request, json, pathlib, base64

CONF_PATH = pathlib.Path("/opt/data/tmp/.cf_config.json")
PROC_PATH = pathlib.Path(pathlib.Path.home() / ".r2-email-processed.json")

if not CONF_PATH.exists():
    print("No CF config found")
    exit(0)

conf = json.loads(CONF_PATH.read_text())
t = conf["token"]
a = conf["account_id"]
b = conf["bucket"]

# Load processed set
processed = set()
if PROC_PATH.exists():
    processed = set(json.loads(PROC_PATH.read_text()))

headers = {"Authorization": f"Bearer {t}"}
enc_bucket = b.replace("-", "%2D").replace("_", "%5F")
import urllib.parse
enc_bucket = urllib.parse.quote(b, safe='')

# List objects
req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/accounts/{a}/r2/buckets/{enc_bucket}/objects",
    headers=headers
)
resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
objs = resp.get("result", [])

if not isinstance(objs, list):
    exit(0)

# Filter new
new = [o for o in objs if o["key"] not in processed and o["key"].endswith(".json")]

if not new:
    exit(0)

# Mark as processed
for o in objs:
    processed.add(o["key"])
PROC_PATH.write_text(json.dumps(list(processed)))

# Report new emails
print(f"Found {len(new)} new email(s):")
for o in sorted(new, key=lambda x: x.get("uploaded", "")):
    # Fetch the metadata
    req2 = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{a}/r2/buckets/{enc_bucket}/objects/{urllib.parse.quote(o['key'], safe='')}",
        headers=headers
    )
    try:
        meta = json.loads(urllib.request.urlopen(req2, timeout=15).read())
        print(f"  From: {meta.get('From', '?')}")
        print(f"  Subject: {meta.get('Subject', '?')}")
        print(f"  Date: {meta.get('Date', '?')}")
    except:
        print(f"  {o['key']} ({o.get('size', 0)}B)")
