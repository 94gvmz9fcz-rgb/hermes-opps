#!/usr/bin/env python3
"""Seed the hybrid DB with our core docs. Inline version - no imports from other scripts."""
import sys, os, hashlib, json, re, chromadb

DB_PATH = "/opt/data/.hybrid-db"

def chunk_text(text, max_chars=1000):
    if len(text) <= max_chars:
        return [text]
    chunks = []
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

client = chromadb.PersistentClient(path=DB_PATH)
for name in client.list_collections():
    try:
        client.delete_collection(name.name)
    except:
        pass

collection = client.create_collection(
    name="hermes-hybrid",
    metadata={"hnsw:space": "cosine"}
)

docs_to_index = [
    ("Hermy/docs/DASHBOARD.md", "/opt/data/repo/docs/herms/DASHBOARD.md", "doc"),
    ("Hermy/docs/work-profile.md", "/opt/data/repo/docs/josh/work-profile.md", "josh-work"),
    ("Hermy/docs/industry-landscape.md", "/opt/data/repo/docs/josh/industry-landscape.md", "josh-work"),
    ("Hermy/docs/work-playbook.md", "/opt/data/repo/docs/josh/work-playbook.md", "josh-work"),
    ("Hermy/docs/decisions-log.md", "/opt/data/repo/docs/state/02-decisions-log.md", "decision"),
    ("Hermy/docs/study-plan.md", "/opt/data/repo/docs/josh/study-plan.md", "josh-work"),
]

for remote_path, local_path, doc_type in docs_to_index:
    text = open(local_path).read()
    chunks = chunk_text(text)
    ids = []
    documents = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        h = hashlib.sha256(f"{remote_path}:{i}".encode()).hexdigest()[:16]
        ids.append(f"idx-{h}")
        documents.append(chunk)
        metadatas.append({
            "source": "hermes-repo",
            "type": doc_type,
            "filename": remote_path.split("/")[-1],
            "filepath": remote_path,
            "ext": ".md",
            "chunk": i,
            "indexed_at": "2026-06-22"
        })
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ {remote_path}: {len(chunks)} chunks")

print(f"\n📊 Total chunks in DB: {collection.count()}")

# Save manifest
manifest = {}
for remote_path, local_path, doc_type in docs_to_index:
    manifest[remote_path] = {
        "hash": hashlib.sha256(open(local_path, "rb").read()).hexdigest()[:16],
        "chunks": len(chunk_text(open(local_path).read())),
        "indexed_at": "2026-06-22"
    }
with open(os.path.expanduser("~/.hybrid-manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# Test queries
tests = [
    "DoD IT channel contacts Air Force",
    "memory compression navigation pointers",
    "Josh work profile account manager",
]
for query in tests:
    results = collection.query(query_texts=[query], n_results=2)
    print(f"\n🔍 '{query}':")
    for i, (doc, dist, meta) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0])):
        fn = meta.get('filename', '?')
        print(f"  [{i+1}] dist={dist:.3f} | {fn} | {doc[:80]}...")

print("\n🔥 Hybrid DB seeded and verified.")
