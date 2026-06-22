#!/usr/bin/env python3
"""
Email Scanner — IMAP-based inbox monitoring for Hermes.
Reads unseen emails from Outlook/Office 365, extracts content,
and routes actionable items to the OneDrive inbox pipeline.

Usage:
  python3 scripts/email-scanner.py [--once]

Configuration via environment variables or vault:
  EMAIL_IMAP_SERVER, EMAIL_IMAP_PORT, EMAIL_USER, EMAIL_PASS

Designed as a cron job (every 15 min).
"""

import json
import os
import sys
import re
import tempfile
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──

IMAP_SERVER = os.environ.get("EMAIL_IMAP_SERVER", "outlook.office365.com")
IMAP_PORT = int(os.environ.get("EMAIL_IMAP_PORT", "993"))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
INBOX_DIR = os.path.expanduser("~/OneDrive/Hermy/inbox")
PROCESSED_LOG = os.path.expanduser("~/.email-scanner-processed.json")

# ── Helpers ──

def decode_mime_header(header_value):
    """Decode MIME-encoded headers to plain text."""
    if not header_value:
        return ""
    parts = decode_header(header_value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)


def get_email_body(msg):
    """Extract plain text body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body += payload.decode(charset, errors="replace")
                except Exception:
                    pass
            elif content_type == "text/html" and not body:
                # Only use HTML if no plain text found
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        html = payload.decode(charset, errors="replace")
                        # Strip HTML tags for plain text
                        body += re.sub(r"<[^>]+>", " ", html)
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body += payload.decode(charset, errors="replace")
        except Exception:
            pass
    return body.strip()


def get_processed_ids():
    """Load set of previously processed message UIDs."""
    if os.path.exists(PROCESSED_LOG):
        try:
            with open(PROCESSED_LOG) as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_processed_ids(ids):
    """Save processed message UIDs."""
    existing = get_processed_ids()
    existing.update(ids)
    with open(PROCESSED_LOG, "w") as f:
        json.dump(list(existing), f)


def save_to_inbox(subject, sender, body, uid):
    """Save email content as a .txt file in the Hermes inbox."""
    os.makedirs(INBOX_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_subject = re.sub(r"[^\w\s-]", "", subject)[:60].strip()
    filename = f"email_{timestamp}_{uid}_{safe_subject}.txt"
    filepath = os.path.join(INBOX_DIR, filename)

    content = f"""From: {sender}
Subject: {subject}
Timestamp: {datetime.now().isoformat()}
Source: email

{body}
"""
    with open(filepath, "w") as f:
        f.write(content)

    return filepath


# ── Main ──

def scan_inbox(once=False):
    """Scan inbox for unseen emails and process them."""
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ EMAIL_USER and EMAIL_PASS must be set.", file=sys.stderr)
        return 1

    processed_ids = get_processed_ids()
    new_ids = []

    try:
        # Connect
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        # Search for unseen messages
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            print("📭 No new messages.")
            mail.logout()
            return 0

        uids = messages[0].split()
        print(f"📬 Found {len(uids)} unseen messages.")

        for uid in uids:
            uid_str = uid.decode()
            if uid_str in processed_ids:
                continue

            try:
                status, msg_data = mail.fetch(uid, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = decode_mime_header(msg.get("Subject", "(no subject)"))
                sender = decode_mime_header(msg.get("From", "(unknown)"))
                body = get_email_body(msg)

                # Save to inbox
                filepath = save_to_inbox(subject, sender, body, uid_str)
                print(f"  ✅ [{uid_str}] \"{subject[:50]}\" → {filepath}")
                new_ids.append(uid_str)

            except Exception as e:
                print(f"  ❌ [{uid_str}] Error: {e}", file=sys.stderr)

        # Save processed IDs
        if new_ids:
            save_processed_ids(new_ids)
            print(f"💾 Saved {len(new_ids)} new message IDs.")

        mail.logout()
        return 0

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    once = "--once" in sys.argv
    sys.exit(scan_inbox(once=once))
