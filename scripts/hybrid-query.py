#!/usr/bin/env python3
"""
Hybrid Query Bridge — routes searches to local ChromaDB.
Called by Herms when I need to search indexed documents.

Usage:
  python3 hybrid-query.py search "query text" [n_results=5]
  python3 hybrid-query.py search "query text" --filter source=hermes-repo
  python3 hybrid-query.py status
"""
import sys, json, os, chromadb

DB_PATH = "/opt/data/.hybrid-db"

def search(query, n_results=5, filter_dict=None):
    """Search the hybrid DB and return results."""
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name="hermes-hybrid",
        metadata={"hnsw:space": "cosine"}
    )
    
    where = None
    if filter_dict:
        where = {}
        for k, v in filter_dict.items():
            where[k] = v
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where
    )
    
    output = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            output.append({
                "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                "filename": results['metadatas'][0][i].get('filename', 'unknown'),
                "filepath": results['metadatas'][0][i].get('filepath', 'unknown'),
                "type": results['metadatas'][0][i].get('type', 'unknown'),
                "chunk": results['metadatas'][0][i].get('chunk', 0),
                "content": results['documents'][0][i][:500]  # Truncate for display
            })
    
    return {
        "query": query,
        "results": output,
        "total_results": len(output)
    }

def status():
    """Show DB status."""
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        collection = client.get_collection("hermes-hybrid")
        count = collection.count()
    except:
        count = 0
    
    manifest_path = os.path.expanduser("~/.hybrid-manifest.json")
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path))
        files = len(manifest)
    else:
        files = 0
    
    return {
        "status": "running",
        "chunks": count,
        "files_indexed": files,
        "db_path": DB_PATH
    }

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        n = 5
        filter_dict = None
        
        for arg in sys.argv[3:]:
            if arg.isdigit():
                n = int(arg)
            elif arg.startswith("--filter"):
                parts = arg.split("=", 1)
                if len(parts) == 2:
                    kv = parts[1].split("=") if "=" in parts[1] else [parts[1]]
                    if len(kv) >= 2:
                        filter_dict = {kv[0]: kv[1]}
        
        if not query:
            print(json.dumps({"error": "No query provided"}))
            sys.exit(1)
        
        result = search(query, n, filter_dict)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        print(json.dumps(status(), indent=2))
    
    else:
        print(f"Usage: {sys.argv[0]} [search|status]")
