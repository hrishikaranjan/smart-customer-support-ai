"""
vector_store.py

Builds and queries a FAISS vector index over the knowledge_base/*.txt
files. The index (plus the raw text chunks) is cached to disk under
index_store/ so we only call the Gemini embeddings API once per
document, not once per chat message.

Pipeline implemented here:
    .txt files -> chunks -> Gemini embeddings -> FAISS index -> disk cache
"""

import os
import json
import glob
from typing import List, Tuple

import numpy as np
import faiss

from embeddings import embed_documents, embed_query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
INDEX_DIR = os.path.join(BASE_DIR, "index_store")
INDEX_PATH = os.path.join(INDEX_DIR, "kb.index")
CHUNKS_PATH = os.path.join(INDEX_DIR, "chunks.json")

CHUNK_SIZE = 700       # characters per chunk
CHUNK_OVERLAP = 100    # characters of overlap between consecutive chunks


def _chunk_text(text: str, source: str) -> List[dict]:
    """Split a document into overlapping character chunks.

    A simple sliding window is enough for short policy documents like
    these; it keeps the implementation easy to explain in an interview
    while still avoiding cutting sentences in half too often.
    """
    text = " ".join(text.split())  # normalize whitespace
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "source": source})
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _load_all_chunks() -> List[dict]:
    """Read every .txt file in knowledge_base/ and split it into chunks."""
    all_chunks = []
    for path in sorted(glob.glob(os.path.join(KB_DIR, "*.txt"))):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        source = os.path.basename(path)
        all_chunks.extend(_chunk_text(content, source))
    return all_chunks


def build_index(force: bool = False) -> None:
    """Build the FAISS index from knowledge_base/ and cache it to disk.

    If a cached index already exists and `force` is False, this is a
    no-op — we never want to re-embed the whole knowledge base just
    because the server restarted.
    """
    os.makedirs(INDEX_DIR, exist_ok=True)

    if not force and os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
        return

    chunks = _load_all_chunks()
    if not chunks:
        raise RuntimeError(f"No knowledge base documents found in {KB_DIR}")

    texts = [c["text"] for c in chunks]
    vectors = embed_documents(texts)  # shape: (n_chunks, dim)

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized inner product
    faiss.normalize_L2(vectors)
    index.add(vectors)

    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def _load_index() -> Tuple[faiss.Index, List[dict]]:
    if not (os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH)):
        build_index(force=True)
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


def search(query: str, top_k: int = 3) -> List[dict]:
    """Return the top_k most relevant knowledge-base chunks for a query."""
    index, chunks = _load_index()

    query_vector = embed_query(query).reshape(1, -1)
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx]
        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "score": float(score),
        })
    return results
