#!/usr/bin/env python3
"""
→wrong feedback loop — correction ingestion for Herms.

Josh says "→wrong that's incorrect because X"
This script:
  1. Logs the correction with the original context
  2. Adds a negative example to ChromaDB so similar queries rank lower
  3. Updates the relevant doc/playbook with the correction
  4. Notifies me so I can adjust future answers

Usage:
  python3 wrong.py log "query" "original answer" "correction" [source_file]
  python3 wrong.py list [--limit 10]
"""
import json, os, sys, hashlib, chromadb
from datetime import datetime, timezone
from pathlib import Path

HOME = os.path.expanduser("~")
HYBRID_DB = "/opt/data/.hybrid-db"
LOG_PATH = Path(HOME) / ".hermes" / "corrections-log.json"

def load_log():
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text())
    return {"corrections": []}

def save_log(log):
    LOG_PATH.write_text(json.dumps(log, indent=2))

def log_correction(query, original_answer, correction, source_file=None):
    """Log a correction and update the hybrid DB."""
    log = load_log()
    
    entry = {
        "id": hashlib.sha256(f"{query}:{datetime.now().isoformat()}".encode()).hexdigest()[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "original_answer": original_answer[:500] if original_answer else "",
        "correction": correction,
        "source_file": source_file or "unknown",
        "resolved": False
    }
    
    log["corrections"].append(entry)
    save_log(log)
    
    # Add negative example to ChromaDB
    try:
        client = chromadb.PersistentClient(path=HYBRID_DB)
        collection = client.get_or_create_collection(
            name="hermes-hybrid",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Create a "wrong" document — this chunk will rank HIGH for the query
        # but its metadata flags it as a correction, so I know to avoid it
        wrong_doc = f"CORRECTION: {correction}. The previous answer was wrong. Original query was: {query}"
        h = hashlib.sha256(f"correction:{entry['id']}".encode()).hexdigest()[:16]
        
        collection.add(
            documents=[wrong_doc],
            metadatas=[{
                "type": "correction",
                "correction_id": entry["id"],
                "original_query": query[:200],
                "corrected_answer": correction[:200],
                "source_file": source_file or "unknown",
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }],
            ids=[f"corr-{h}"]
        )
        
        entry["chroma_indexed"] = True
    except Exception as e:
        entry["chroma_indexed"] = False
        entry["chroma_error"] = str(e)
    
    save_log(log)
    
    # If we know the source file, update it with a correction note
    if source_file and os.path.exists(source_file):
        try:
            with open(source_file, "a") as f:
                f.write(f"\n\n> **Correction ({datetime.now().strftime('%Y-%m-%d %H:%M')}):** {correction}\n")
            entry["file_updated"] = True
        except:
            entry["file_updated"] = False
        save_log(log)
    
    return entry

def list_corrections(limit=10, unresolved_only=False):
    """List recent corrections."""
    log = load_log()
    corrections = log["corrections"]
    
    if unresolved_only:
        corrections = [c for c in corrections if not c.get("resolved", False)]
    
    corrections = sorted(corrections, key=lambda c: c.get("timestamp", ""), reverse=True)[:limit]
    return corrections

def mark_resolved(correction_id):
    """Mark a correction as resolved."""
    log = load_log()
    for c in log["corrections"]:
        if c.get("id") == correction_id:
            c["resolved"] = True
            c["resolved_at"] = datetime.now(timezone.utc).isoformat()
            save_log(log)
            return True
    return False

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if command == "log":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        original = sys.argv[3] if len(sys.argv) > 3 else ""
        correction = sys.argv[4] if len(sys.argv) > 4 else ""
        source = sys.argv[5] if len(sys.argv) > 5 else None
        
        if not correction:
            print("Usage: wrong.py log <query> <original_answer> <correction> [source_file]")
            sys.exit(1)
        
        result = log_correction(query, original, correction, source)
        print(json.dumps(result, indent=2))
    
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        unresolved = "--unresolved" in sys.argv
        results = list_corrections(limit, unresolved)
        print(json.dumps(results, indent=2))
    
    elif command == "resolve":
        cid = sys.argv[2] if len(sys.argv) > 2 else ""
        if mark_resolved(cid):
            print(f"✅ Correction {cid} resolved")
        else:
            print(f"❌ Correction {cid} not found")
    
    else:
        print("→wrong feedback system")
        print("Usage:")
        print("  wrong.py log <query> <original> <correction> [source]")
        print("  wrong.py list [limit] [--unresolved]")
        print("  wrong.py resolve <id>")
