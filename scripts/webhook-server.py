#!/usr/bin/env python3
"""
Webhook Receiver — lightweight HTTP server for external webhooks.
Listens on a configurable port, accepts POST payloads, and
routes them to the OneDrive inbox as files.

This is a simple implementation suited for testing.
Production: deploy as a serverless function on Cloudflare Workers
or Vercel for always-on availability.

Usage:
  python3 scripts/webhook-server.py [--port 8080]
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

INBOX_DIR = os.path.expanduser("~/OneDrive/Hermy/inbox")
DEFAULT_PORT = 8080


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle POST requests from webhooks."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Determine source from path or headers
        source = self.path.strip("/").replace("/", "-") or "webhook"
        content_type = self.headers.get("Content-Type", "application/octet-stream")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webhook_{timestamp}_{source}.json"

        os.makedirs(INBOX_DIR, exist_ok=True)
        filepath = os.path.join(INBOX_DIR, filename)

        # Try to parse as JSON for pretty storage
        try:
            payload = json.loads(body)
            content = json.dumps({
                "source": source,
                "received_at": datetime.now().isoformat(),
                "headers": dict(self.headers),
                "payload": payload,
            }, indent=2)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Store raw
            content = json.dumps({
                "source": source,
                "received_at": datetime.now().isoformat(),
                "headers": dict(self.headers),
                "content_type": content_type,
                "payload_raw": body.decode("utf-8", errors="replace"),
            }, indent=2)

        with open(filepath, "w") as f:
            f.write(content)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "file": filename}).encode())

    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "service": "hermes-webhook",
            "inbox": INBOX_DIR,
        }).encode())

    def log_message(self, format, *args):
        """Quiet logging."""
        sys.stderr.write(f"[webhook] {args[0]} {args[1]} {args[2]}\n")


def main():
    port = DEFAULT_PORT
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"🌐 Webhook server listening on port {port}")
    print(f"📥 POST → http://localhost:{port}/<source-name>")
    print(f"❤️  GET  → http://localhost:{port}/ (health check)")
    print(f"📂 Inbox: {INBOX_DIR}")
    print()
    print("⚠️  For external access, use ngrok or a serverless function.")
    print("   Example: ngrok http 8080")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
