"""
embeddings.py

Thin wrapper around the Gemini embeddings endpoint (google-genai SDK).
Two entry points:
  - embed_documents(texts): batch-embeds knowledge-base chunks (task type
    RETRIEVAL_DOCUMENT) — used once, when the FAISS index is built.
  - embed_query(text): embeds a single user question (task type
    RETRIEVAL_QUERY) — used on every chat message.

Gemini's embed_content call accepts a list of strings for `contents`,
so batching multiple chunks into one API call is both supported and
much cheaper than one call per chunk.
"""

import os
from typing import List

import numpy as np
from google import genai
from google.genai import types

EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

_client = None


def _get_client() -> genai.Client:
    """Lazily create the Gemini client so importing this module never
    fails just because GEMINI_API_KEY isn't set yet (e.g. during tests)."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy backend/.env.example to "
                "backend/.env and fill in your key."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def embed_documents(texts: List[str]) -> np.ndarray:
    """Embed a batch of knowledge-base chunks for storage in FAISS."""
    client = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    vectors = [np.array(e.values, dtype="float32") for e in response.embeddings]
    return np.vstack(vectors)


def embed_query(text: str) -> np.ndarray:
    """Embed a single user query for similarity search against FAISS."""
    client = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return np.array(response.embeddings[0].values, dtype="float32")
