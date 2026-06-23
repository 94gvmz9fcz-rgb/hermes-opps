#!/usr/bin/env python3
"""  
Hermes R2 Email Check — watchdog. Quiet unless new email found.  
All writes flushed immediately to prevent broken pipe in cron.  
"""
import json, os, subprocess, sys, tempfile, re
from datetime import datetime, timezone
from pathlib import Path

_eprint = lambda *a, **kw: print(*a, file=sys.stderr, flush=True, **kw)

R2_BUCKET = "hermes-email"
STATE_FILE = os.path.expanduser("~/.r2-email-processed.json")
LOCAL_INBOX = os.path.expanduser("~/OneDrive/Hermy/inbox")

def get_token():
    tok_path = Path("/opt/data/tmp/.tok")
    if not tok_path.exists():
        return None
    data = tok_path.read_bytes()
    key = 0x42
    return bytes(b ^ key for b in data).decode("ascii").strip()

def get_account_id():
    return "442861c837c73a59d4420aa63e2680b8"

def r2_req(method, path, body=None):
    import urllib.request, urllib.parse
    token = get_token()
    url = f"https://api.cloudflare.com/client/v4/accounts/{get_account_id()}/{path}"
    hdrs = {"Authorization": f"Bearer {token}"}
    if body:
        hdrs["Content-Type"] = "application/json"
        body = json.dumps(body).encode() if isinstance(body, dict) else body
    req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def main():
    token = get_token()
    if not token:
        sys.exit(0)  # quiet — token setup pending

    processed = set()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                processed = set(json.load(f))
        except: pass

    # List objects
    params = f"r2/buckets/{R2_BUCKET}/objects?per_page=100&prefix=incoming/"
    data = r2_req("GET", params)
    if not data.get("success"):
        sys.exit(0)

    objects = data.get("result", [])
    
    new_json_keys = [o["key"] for o in objects if o["key"].endswith(".json") and o["key"] not in processed]
    
    if not new_json_keys:
        # Quiet exit — nothing new. Empty stdout = silent (watchdog pattern)
        sys.exit(0)

    eml_map = {}
    for o in objects:
        k = o["key"]
        if k.endswith(".eml"):
            eml_map[k.rsplit(".", 1)[0]] = k

    os.makedirs(LOCAL_INBOX, exist_ok=True)
    delivered = []

    for jk in sorted(new_json_keys):
        try:
            enc = __import__("urllib.parse").quote(jk, safe="")
            meta_data = r2_req("GET", f"r2/buckets/{R2_BUCKET}/objects/{enc}")
            if not meta_data.get("success"):
                continue
            meta_raw = meta_data.get("result", {}).get("body", "{}")
            meta = json.loads(meta_raw) if isinstance(meta_raw, str) else meta_raw

            base = jk.rsplit(".", 1)[0]
            eml_key = eml_map.get(base)
            eml_path = None

            if eml_key:
                enc_eml = __import__("urllib.parse").quote(eml_key, safe="")
                eml_data = r2_req("GET", f"r2/buckets/{R2_BUCKET}/objects/{enc_eml}")
                if eml_data.get("success"):
                    body_raw = eml_data.get("result", {}).get("body", "")
                    eml_bytes = body_raw.encode() if isinstance(body_raw, str) else body_raw
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_subj = re.sub(r"[^\w\s-]", "", meta.get("Subject", "email"))[:50]
                    eml_path = os.path.join(LOCAL_INBOX, f"r2_{ts}_{safe_subj}.eml")
                    with open(eml_path, "wb") as f:
                        f.write(eml_bytes)

            subject = meta.get("Subject", "(no subject)")
            from_ = meta.get("From", "(unknown)")
            date_str = meta.get("Date", "")
            body_snippet = meta.get("TextBody", meta.get("HtmlBody", ""))
            body_snippet = re.sub(r"<[^>]+>", " ", body_snippet)[:800]

            delivered.append(f"📬 New: '{subject}' from {from_} ({date_str})")

            # Mark processed
            processed.add(jk)
            with open(STATE_FILE, "w") as f:
                json.dump(sorted(processed), f, indent=2)

        except Exception as e:
            processed.add(jk)
            with open(STATE_FILE, "w") as f:
                json.dump(sorted(processed), f, indent=2)

    if delivered:
        print("\n".join(delivered), flush=True)

    sys.exit(0)

if __name__ == "__main__":
    main()
