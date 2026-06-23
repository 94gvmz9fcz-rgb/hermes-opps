#!/usr/bin/env python3
"""
Hermes R2 Email Check — polls the hermes-email R2 bucket for new emails
and surfaces them for discussion in Telegram.

Quiet unless there's actually new email — no "nothing found" output.

For each new .eml file found, reads the matching .json metadata,
saves it to the local inbox, then outputs a structured summary
for Hermes to act on.

State tracked via ~/.r2-email-processed.json (set of object keys).
"""

import json
import os
import subprocess
import sys
import tempfile
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──
R2_BUCKET = "hermes-email"
STATE_FILE = os.path.expanduser("~/.r2-email-processed.json")
LOCAL_INBOX = os.path.expanduser("~/OneDrive/Hermy/inbox")

# R2 API via wrangler or curl (prefer wrangler if available)
# We'll use curl with the Cloudflare API since we have the token

def get_token():
    """Read and decode the XOR-encoded token."""
    tok_path = Path("/opt/data/tmp/.tok")
    if not tok_path.exists():
        return None
    data = tok_path.read_bytes()
    key = 0x42
    decoded = bytes(b ^ key for b in data).decode("ascii").strip()
    return decoded

def get_account_id():
    return "442861c837c73a59d4420aa63e2680b8"

def r2_list(token, bucket, prefix=""):
    """List objects in R2 bucket using urllib."""
    import urllib.request
    import urllib.parse

    account_id = get_account_id()
    params = urllib.parse.urlencode({"per_page": 100, "prefix": prefix})
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/objects?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    if data.get("success"):
        return data["result"]
    else:
        errors = data.get("errors", [])
        raise Exception(f"R2 list failed: {errors}")


def r2_get(token, bucket, key):
    """Download an object from R2 bucket using urllib."""
    import urllib.request
    import urllib.parse

    account_id = get_account_id()
    encoded_key = urllib.parse.quote(key, safe="")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/objects/{encoded_key}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            err_data = json.loads(body)
            errors = err_data.get("errors", [])
        except json.JSONDecodeError:
            errors = [body.decode("utf-8", errors="replace")]
        raise Exception(f"R2 get failed for {key}: {errors}")

def load_processed():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_processed(keys):
    existing = load_processed()
    existing.update(keys)
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(existing), f, indent=2)


def format_email_for_delivery(title, from_, subject, date_str, body_snippet, body_path):
    """Build a clean delivery message for Telegram."""
    lines = [
        f"📬 **New email from Hermy's inbox**",
        f"**Subject:** {subject}",
        f"**From:** {from_}",
        f"**Date:** {date_str}",
        f"**Key context:** {body_snippet[:500]}" if body_snippet else "",
        f"",
        f"📍 Saved to: `{body_path}`",
    ]
    return "\n".join(l for l in lines if l)


def main():
    try:
        token = get_token()
        if not token:
            print("❌ Token not found at /opt/data/tmp/.tok", file=sys.stderr)
            return 1

        processed = load_processed()

        # List all .json metadata files in the incoming/ prefix
        objects = r2_list(token, R2_BUCKET, prefix="incoming/")

        # Find new .json files (metadata)
        new_json_keys = []
        for obj in objects:
            key = obj["key"]
            if not key.endswith(".json"):
                continue
            if key not in processed:
                new_json_keys.append(key)

        if not new_json_keys:
            # Quiet exit — nothing new
            return 0

        # Find matching .eml files for the new metadata
        eml_keys = {}
        for obj in objects:
            key = obj["key"]
            if key.endswith(".eml"):
                # Map the base name (without extension)
                base = key.rsplit(".", 1)[0]
                eml_keys[base] = key

        os.makedirs(LOCAL_INBOX, exist_ok=True)

        delivered = []
        for json_key in sorted(new_json_keys):
            try:
                # Download metadata
                meta_raw = r2_get(token, R2_BUCKET, json_key)
                meta = json.loads(meta_raw)

                base_key = json_key.rsplit(".", 1)[0]
                eml_key = eml_keys.get(base_key)
                eml_path = None

                # Download .eml if available
                if eml_key:
                    eml_data = r2_get(token, R2_BUCKET, eml_key)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_subj = re.sub(r"[^\w\s-]", "", meta.get("Subject", "email"))[:50]
                    eml_path = os.path.join(LOCAL_INBOX, f"r2_{ts}_{safe_subj}.eml")
                    with open(eml_path, "wb") as f:
                        f.write(eml_data)

                subject = meta.get("Subject", "(no subject)")
                from_ = meta.get("From", "(unknown)")
                date_str = meta.get("Date", "")

                # Build body snippet from the .eml or metadata
                body_snippet = ""
                if "TextBody" in meta:
                    body_snippet = meta["TextBody"]
                elif "HtmlBody" in meta:
                    body_snippet = meta["HtmlBody"]
                    # Strip HTML for snippet
                    body_snippet = re.sub(r"<[^>]+>", " ", body_snippet)

                # Truncate snippet for delivery
                if len(body_snippet) > 800:
                    body_snippet = body_snippet[:800] + "..."

                delivered.append({
                    "subject": subject,
                    "from_": from_,
                    "date_str": date_str,
                    "body_snippet": body_snippet,
                    "body_path": eml_path,
                    "json_key": json_key,
                    "eml_key": eml_key,
                })

                # Mark as processed
                save_processed([json_key])

            except Exception as e:
                print(f"❌ Failed to process {json_key}: {e}", file=sys.stderr)
                # Still mark as processed so we don't retry endlessly
                save_processed([json_key])

        if delivered:
            # Output as JSON so Hermes can parse it
            output = {
                "new_emails": len(delivered),
                "emails": [{
                    "subject": d["subject"],
                    "from": d["from_"],
                    "date": d["date_str"],
                    "snippet": d["body_snippet"][:300],
                    "file": d["body_path"],
                } for d in delivered]
            }
            print(json.dumps(output, indent=2))

        return 0

    except Exception as e:
        print(f"❌ R2 email check failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
