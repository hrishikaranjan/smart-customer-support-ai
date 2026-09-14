"""
rag.py

Retrieval-Augmented Generation helper. Given a user question, retrieves
the most relevant knowledge-base chunks from FAISS and formats them into
a context block that gets injected into the Gemini prompt (see agent.py).
"""

from typing import List
import vector_store


def retrieve_context(query: str, top_k: int = 3, min_score: float = 0.55) -> str:
    """Return a formatted context string of relevant KB chunks, or an
    empty string if nothing sufficiently relevant was found.

    min_score filters out weak matches (e.g. small talk like "hello")
    so we don't stuff irrelevant policy text into every prompt.
    """
    results = vector_store.search(query, top_k=top_k)
    relevant = [r for r in results if r["score"] >= min_score]

    if not relevant:
        return ""

    blocks = []
    for r in relevant:
        blocks.append(f"[Source: {r['source']}]\n{r['text']}")
    return "\n\n".join(blocks)
