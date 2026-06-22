#!/usr/bin/env python3
"""
Junk Drawer Image Pipeline — batch image processing from Telegram.

When Josh sends images (caption: "cards", "photos", "docs", or no caption),
this pipeline:
  1. Downloads from Telegram
  2. Runs local OCR (tesseract) for text extraction
  3. Saves to OneDrive/Hermy/Junk Drawer/ with metadata
  4. Logs extracted text for me to review

Usage:
  python3 pipeline.py poll          # Check for new images once
  python3 pipeline.py watch         # Continuous poll (for cron/daemon)
  python3 pipeline.py process <file_id>  # Process a specific file
"""

import json
import os
import sys
import time
import uuid
import requests as req
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO

# Env loading (same as gateway)
sys.path.insert(0, "/opt/hermes")
from hermes_cli.env_loader import load_hermes_dotenv
load_hermes_dotenv()

# OCR
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# OneDrive
sys.path.insert(0, str(Path.home() / ".config" / "hermy"))
try:
    from onedrive_graph import graph, GRAPH
    GRAPH_BASE = GRAPH
    ONEDRIVE_AVAILABLE = True
except ImportError:
    GRAPH_BASE = ""
    ONEDRIVE_AVAILABLE = False

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = "8327493830"
OFFSET_FILE = Path.home() / ".hermes" / ".pipeline-offset"
JUNK_DRAWER = "Junk Drawer"

# Where processed images + OCR results live
PROCESSED_DIR = Path.home() / ".hermes" / "pipeline-results"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif"}
# Telegram sends documents with these MIME types
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/gif", "image/tiff", "image/heic", "image/heif"}


def tg(method, **params):
    """Call Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        r = req.post(url, json=params, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def download_file(file_id):
    """Download a file from Telegram by file_id."""
    fdata = tg("getFile", file_id=file_id)
    fpath = fdata.get("result", {}).get("file_path")
    if not fpath:
        return None, None
    dl_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fpath}"
    r = req.get(dl_url, timeout=60)
    if r.status_code != 200:
        return None, None
    ext = os.path.splitext(fpath)[1].lower()
    return r.content, ext


def ocr_image(image_bytes):
    """Run Tesseract OCR on image bytes. Returns extracted text or None."""
    if not OCR_AVAILABLE:
        return None
    try:
        img = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        text = text.strip()
        return text if text else None
    except Exception as e:
        return f"[OCR Error: {e}]"


def save_onedrive(content, path_segments):
    """Save bytes to OneDrive/Hermy/{path_segments}."""
    if not ONEDRIVE_AVAILABLE:
        return False, "OneDrive not available"

    try:
        resp = graph("GET", f"{GRAPH_BASE}/me/drive/root:/Hermy")
        root_id = resp.get("id")
        if not root_id:
            return False, "Hermy root not found"

        parent_id = root_id
        for i, seg in enumerate(path_segments[:-1]):
            children = graph("GET", f"{GRAPH_BASE}/me/drive/items/{parent_id}/children")
            existing = [c for c in children.get("value", [])
                       if c.get("name") == seg and "folder" in c]
            if existing:
                parent_id = existing[0]["id"]
            else:
                create = graph("POST", f"{GRAPH_BASE}/me/drive/items/{parent_id}/children",
                              {"name": seg, "folder": {}})
                parent_id = create.get("id")
                if not parent_id:
                    return False, f"Could not create folder: {seg}"

        filename = path_segments[-1]
        token = _get_token()
        if not token:
            return False, "No OneDrive token"

        upload_url = f"{GRAPH_BASE}/me/drive/items/{parent_id}:/{filename}:/content"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}
        r = req.put(upload_url, headers=headers, data=content, timeout=120)
        return (True, None) if r.status_code in (200, 201) else (False, f"HTTP {r.status_code}")

    except Exception as e:
        return False, str(e)


def _get_token():
    """Get OneDrive access token from stored creds."""
    try:
        tok_path = Path.home() / ".config" / "hermy" / "onedrive-token.json"
        if tok_path.exists():
            data = json.loads(tok_path.read_text())
            return data.get("access_token", "")
    except Exception:
        pass
    return os.environ.get("ONEDRIVE_ACCESS_TOKEN", "")


def poll_once():
    """Check Telegram for new image messages."""
    offset = None
    if OFFSET_FILE.exists():
        offset = int(OFFSET_FILE.read_text().strip())

    result = tg("getUpdates", offset=offset, timeout=5)
    updates = result.get("result", [])
    events = []

    for update in updates:
        uid = update.get("update_id", 0)
        msg = update.get("message", {})
        caption = (msg.get("caption", "") or "").strip().lower()
        photos = msg.get("photo", [])        # inline photos
        document = msg.get("document", {})    # file attachments

        images_to_process = []

        # Handle inline photos
        if photos:
            # Telegram sends multiple sizes — pick the largest
            best = max(photos, key=lambda p: p.get("file_size", 0))
            images_to_process.append({
                "file_id": best["file_id"],
                "file_name": f"photo_{datetime.now().strftime('%H%M%S')}.jpg",
                "source": "inline_photo",
                "caption": caption,
            })

        # Handle document attachments that are images
        if document:
            mime = document.get("mime_type", "")
            fname = document.get("file_name", f"file-{uuid.uuid4().hex[:8]}")
            ext = os.path.splitext(fname)[1].lower()

            is_image = (mime in ALLOWED_MIMES or ext in ALLOWED_EXTENSIONS or mime.startswith("image/"))
            if is_image:
                images_to_process.append({
                    "file_id": document["file_id"],
                    "file_name": fname,
                    "source": "document",
                    "caption": caption,
                })

        for img_info in images_to_process:
            file_id = img_info["file_id"]
            file_name = img_info["file_name"]
            source = img_info["source"]
            caption = img_info["caption"]

            # Download
            content, ext = download_file(file_id)
            if not content:
                continue

            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            safe_name = f"{ts}_{file_name}"

            # OCR
            ocr_text = ocr_image(content)
            has_text = bool(ocr_text and ocr_text.strip() and "OCR Error" not in ocr_text)

            # Save to OneDrive
            od_success = False
            if ONEDRIVE_AVAILABLE:
                od_ok, od_err = save_onedrive(content, [JUNK_DRAWER, safe_name])
                od_success = od_ok

            # Save OCR result locally
            result_data = {
                "file": safe_name,
                "file_id": file_id,
                "source": source,
                "caption": caption,
                "has_text": has_text,
                "size": len(content),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "onedrive_saved": od_success,
            }
            if ocr_text:
                result_data["ocr_text"] = ocr_text[:2000]  # cap long text
                # Save full OCR text
                (PROCESSED_DIR / f"{safe_name}.ocr.txt").write_text(ocr_text)

            result_file = PROCESSED_DIR / f"{safe_name}.json"
            result_file.write_text(json.dumps(result_data, indent=2))
            events.append(result_data)

        offset = uid + 1

    if offset:
        OFFSET_FILE.write_text(str(offset))

    return events


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "poll"

    if action == "poll":
        events = poll_once()
        if events:
            for ev in events:
                ocr_note = f" — has text: {len(ev.get('ocr_text',''))} chars" if ev.get("has_text") else " — no text extracted"
                print(f"📸 {ev['file']}{ocr_note}")
        else:
            print("No new images")
        print(f"\nSTATUS={'NEW_FILES' if events else 'CLEAN'}")
        # Print OCR text for assistant to see
        for ev in events:
            if ev.get("ocr_text"):
                print(f"\n--- OCR: {ev['file']} ---")
                print(ev["ocr_text"][:1500])
                print("---")

    elif action == "watch":
        print("🔄 Image pipeline watching (poll every 30s)")
        while True:
            try:
                events = poll_once()
                if events:
                    print(f"  {len(events)} new image(s)")
                    for ev in events:
                        if ev.get("ocr_text"):
                            print(f"    {ev['file']}: {ev['ocr_text'][:100]}...")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(30)

    elif action == "reset":
        if OFFSET_FILE.exists():
            OFFSET_FILE.unlink()
        print("Offset reset")


if __name__ == "__main__":
    main()
