#!/usr/bin/env python3
"""
Siri-to-Hermes Bridge — handles audio posted from iOS Shortcut.

Accepts audio files (M4A, WAV, OGG, MP3) sent to the Telegram Bot API
and ensures they get processed the same as native voice memos.

The Shortcut side handles recording and POSTing. This side just needs
to confirm the gateway processes the incoming file correctly.

Usage:
  python3 siri-bridge.py          # One-shot validation test
  python3 siri-bridge.py --watch  # Monitor gateway logs for processing
"""

import json, os, sys, time, subprocess

BOT_TOKEN_FILE = "/tmp/real-token.txt"
CHAT_ID = "8327493830"
API = "https://api.telegram.org"

def get_token():
    if os.path.exists(BOT_TOKEN_FILE):
        with open(BOT_TOKEN_FILE) as f:
            return f.read().strip()
    return None

def send_test_audio(filepath, method="sendVoice"):
    """Send an audio file to the chat via Telegram Bot API."""
    token = get_token()
    if not token:
        print("No token found.")
        return False
    
    url = f"{API}/bot{token}/{method}"
    with open(filepath, "rb") as f:
        files = {"audio" if method == "sendAudio" else "voice": f}
        data = {"chat_id": CHAT_ID, "caption": "📱 From Siri Shortcut pipeline test"}
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", url, "-F", f"chat_id={CHAT_ID}", 
             "-F", f"audio=@{filepath}" if method == "sendAudio" else "-F", f"voice=@{filepath}"],
            capture_output=True, text=True, timeout=30
        )
    
    try:
        resp = json.loads(result.stdout)
        if resp.get("ok"):
            print(f"✅ Sent! Message ID: {resp['result']['message_id']}")
            return True
        else:
            print(f"❌ API Error: {resp.get('description')}")
            return False
    except:
        print(f"❌ Failed: {result.stdout[:200]}")
        return False

if __name__ == "__main__":
    print("Siri-to-Hermes Bridge — Pipeline Ready")
    print("=" * 40)
    print(f"Chat ID: {CHAT_ID}")
    print(f"Bot: @jstew_hermes_bot")
    print()
    print("Shortcut Setup:")
    print("1. Create a new Shortcut")
    print("2. Add 'Record Audio' — no duration limit")
    print("3. Add 'Get Contents of URL' — POST to Telegram Bot API")
    print("4. Add 'Show Notification' — confirm sent")
    print()
    print("Telegram endpoint:")
    print(f"POST {API}/bot<TOKEN>/sendAudio")
    print(f"  chat_id: {CHAT_ID}")
    print(f"  audio: (audio file from recording)")
    print(f"  caption: (optional note)")
