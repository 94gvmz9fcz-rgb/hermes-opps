#!/usr/bin/env python3
"""
→art — Generative Art Pipeline
Usage: python3 →art.py [piece_name]

Generates a fresh generative art piece, outputs the HTML file path.
JStew opens it on his iPad, presses S for PNG.

Available pieces:
  drift       — Bioluminescent Drift (particles, flow field, bloom)
  attractor   — Strange Attractor Gallery (math, 6 modes)
  breathing   — Breathing (kinetic typography + particles)
  all         — Show the gallery index
"""

import sys
import os
import random

BASE = os.path.dirname(os.path.abspath(__file__))
Pieces_dir = os.path.join(BASE, "output", "creative")

PIECES = {
    "drift": "bioluminescent-drift.html",
    "attractor": "strange-attractor.html",
    "breathing": "breathing.html",
}

def show_gallery():
    """List all available pieces with descriptions."""
    print("🎨 AStew Generative Studio")
    print("=" * 40)
    for name, filename in PIECES.items():
        path = os.path.join(Pieces_dir, filename)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  {name:12s} → {filename} ({size // 1024} KB)")
    print()
    print(f"  {'index':12s} → Gallery index: output/creative/index.html")
    print()
    print("Open on your iPad, press S to save PNG.")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        show_gallery()
        print(f"\nUsage: python3 →art.py [piece_name]")
        sys.exit(0)

    piece = sys.argv[1].lower()

    if piece == "all" or piece == "index":
        path = os.path.join(BASE, "output", "creative", "index.html")
        print(f"📋 Gallery Index: {path}")
        sys.exit(0)

    if piece not in PIECES:
        print(f"❌ Unknown piece: '{piece}'")
        print(f"Available: {', '.join(PIECES.keys())}")
        sys.exit(1)

    filename = PIECES[piece]
    path = os.path.join(Pieces_dir, filename)

    if not os.path.exists(path):
        print(f"❌ Piece file not found: {path}")
        sys.exit(1)

    print(f"🎨 → {piece}")
    print(f"📄 {path}")
    print(f"📏 {os.path.getsize(path) // 1024} KB")
    print()
    print("Open on your iPad → Press S to save PNG → Send back to me")
    print()

    # Show controls
    with open(path) as f:
        content = f.read()
        if "keyPressed" in content:
            print("⌨️ Controls:")
            if "S" in content:
                print("  S = Save PNG")
            if "G" in content:
                print("  G = Save GIF")
            if "R" in content:
                print("  R = Reseed")
            if "Space" in content:
                print("  Space = Pause")
            if "1" in content and "6" in content:
                print("  1-6 = Switch attractor type")


if __name__ == "__main__":
    main()
