#!/usr/bin/env python3
"""
Hybrid Indexer — watches OneDrive/Hermy/ for new files and indexes them into ChromaDB.
Runs on-demand or via cron.

Usage:
  python3 hybrid-indexer.py scan       # Index all new files in OneDrive/Hermy/docs
  python3 hybrid-indexer.py index <path>  # Index a specific file
  python3 hybrid-indexer.py status     # Show index stats
"""
import json, os, sys, hashlib, re
from pathlib import Path
from datetime import datetime, timezone

# Hybrid env
sys.path.insert(0, str(Path.home() / ".config" / "hermy"))
from onedrive_graph import graph, GRAPH

GRAPH_BASE = GRAPH
MANIFEST_PATH = Path.home() / ".hybrid-manifest.json"
DB_PATH = "/opt/data/.hybrid-db"

# File types we can index
TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".xml", ".log", ".html"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".rb", ".go", ".rs", ".java"}

def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}

def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

def file_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def extract_text(filepath, content_bytes):
    """Extract readable text from a file."""
    ext = Path(filepath).suffix.lower()
    if ext in TEXT_EXTENSIONS or ext in CODE_EXTENSIONS:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content_bytes.decode("latin-1")
            except:
                return ""
    return ""

def chunk_text(text, max_chars=1000):
    """Split long texts into chunks for better retrieval."""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    # Try paragraph breaks first
    paragraphs = text.split("\n\n")
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < max_chars:
            current += p + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    
    # If still too big, split by sentences
    final_chunks = []
    for c in chunks:
        if len(c) > max_chars:
            sentences = c.replace(". ", ".||").split("||")
            cur = ""
            for s in sentences:
                if len(cur) + len(s) < max_chars:
                    cur += s + " "
                else:
                    if cur.strip():
                        final_chunks.append(cur.strip())
                    cur = s + " "
            if cur.strip():
                final_chunks.append(cur.strip())
        else:
            final_chunks.append(c)
    
    return final_chunks

def index_file_in_chromadb(chunks, filepath, metadata):
    """Add chunks to ChromaDB."""
    import chromadb
    
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name="hermes-hybrid",
        metadata={"hnsw:space": "cosine"}
    )
    
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        h = hashlib.sha256(f"{filepath}:{i}".encode()).hexdigest()[:16]
        ids.append(f"idx-{h}")
        documents.append(chunk)
        metadatas.append({
            **metadata,
            "chunk": i,
            "filepath": filepath,
            "indexed_at": datetime.now(timezone.utc).isoformat()
        })
    
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return len(chunks)

def index_file(filepath, content_bytes):
    """Index a single file into ChromaDB and manifest."""
    manifest = load_manifest()
    
    # Check if already indexed and unchanged
    fhash = hashlib.sha256(content_bytes).hexdigest()[:16]
    if filepath in manifest and manifest[filepath]["hash"] == fhash:
        return {"status": "skipped", "reason": "unchanged"}
    
    text = extract_text(filepath, content_bytes)
    if not text.strip():
        return {"status": "skipped", "reason": "no extractable text"}
    
    chunks = chunk_text(text)
    metadata = {
        "source": "onedrive",
        "type": "doc",
        "filename": Path(filepath).name,
        "ext": Path(filepath).suffix.lower()
    }
    
    try:
        num_chunks = index_file_in_chromadb(chunks, filepath, metadata)
        manifest[filepath] = {
            "hash": fhash,
            "chunks": num_chunks,
            "indexed_at": datetime.now(timezone.utc).isoformat()
        }
        save_manifest(manifest)
        return {"status": "indexed", "chunks": num_chunks}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_docs_folder():
    """List files in OneDrive/Hermy/docs/ via Graph API."""
    try:
        # Get docs folder
        resp = graph("GET", f"{GRAPH_BASE}/me/drive/root:/Hermy/docs")
        folder_id = resp.get("id")
        if not folder_id:
            # Create it
            root = graph("GET", f"{GRAPH_BASE}/me/drive/root:/Hermy")
            root_id = root.get("id")
            resp = graph("POST", f"{GRAPH_BASE}/me/drive/items/{root_id}/children",
                        {"name": "docs", "folder": {}})
            folder_id = resp.get("id")
            
        children = graph("GET", f"{GRAPH_BASE}/me/drive/items/{folder_id}/children")
        return children.get("value", [])
    except Exception as e:
        print(f"Error listing docs folder: {e}")
        return []

def scan_and_index():
    """Scan OneDrive/Hermy/docs/ and index new/changed files."""
    manifest = load_manifest()
    files = list_docs_folder()
    
    results = {"indexed": 0, "skipped": 0, "errors": 0, "total": len(files)}
    
    for f in files:
        name = f.get("name", "")
        if not any(name.endswith(ext) for ext in TEXT_EXTENSIONS | CODE_EXTENSIONS):
            continue
        
        # Download file content
        download_url = f.get("@microsoft.graph.downloadUrl")
        if not download_url:
            continue
        
        import requests
        r = requests.get(download_url, timeout=30)
        if r.status_code != 200:
            results["errors"] += 1
            continue
        
        filepath = f"Hermy/docs/{name}"
        result = index_file(filepath, r.content)
        
        if result["status"] == "indexed":
            results["indexed"] += 1
        elif result["status"] == "error":
            results["errors"] += 1
        else:
            results["skipped"] += 1
    
    return results

def print_status():
    """Show index stats."""
    import chromadb
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="hermes-hybrid")
    count = collection.count()
    manifest = load_manifest()
    files_count = len(manifest)
    
    print(f"📊 Hybrid Index Status")
    print(f"  Files indexed: {files_count}")
    print(f"  Chunks in DB:  {count}")
    print(f"  DB location:   {DB_PATH}")
    print(f"  Last indexed:  {max((v['indexed_at'] for v in manifest.values()), default='never')[:19]}")
    print(f"\nIndexed files:")
    for path, info in sorted(manifest.items()):
        print(f"  {path} ({info['chunks']} chunks)")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if command == "scan":
        results = scan_and_index()
        print(json.dumps(results, indent=2))
    elif command == "status":
        print_status()
    else:
        print(f"Usage: {sys.argv[0]} [scan|status]")
