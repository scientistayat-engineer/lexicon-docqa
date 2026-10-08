"""ChromaDB wrapper. Persistent on disk locally, in-memory on serverless."""
import re
from functools import lru_cache

from app.config import SERVERLESS, settings
from app.services import sqlite_fix  # noqa: F401
from app.services import embeddings
from app.services.chunking import chunk_text
from app.services.loaders import read_file

_seeded = False


@lru_cache(maxsize=1)
def _collection():
    import chromadb
    client = chromadb.EphemeralClient() if SERVERLESS else chromadb.PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection("documents", metadata={"hnsw:space": "cosine"})


def add_document(name: str, text: str) -> int:
    col = _collection()
    col.delete(where={"source": name})  # re-upload replaces the old version
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        return 0
    col.add(
        ids=[f"{name}-{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings.embed(chunks),
        metadatas=[{"source": name, "chunk": i} for i in range(len(chunks))],
    )
    return len(chunks)


def ensure_seeded() -> None:
    """Index the sample documents the first time the store is empty."""
    global _seeded
    if _seeded:
        return
    if _collection().count() == 0:
        for f in sorted(settings.sample_docs.glob("*")):
            if f.suffix in settings.allowed_ext:
                add_document(f.name, read_file(f.name, f.read_bytes()))
    _seeded = True


def list_documents() -> list[dict]:
    ensure_seeded()
    counts: dict[str, int] = {}
    for m in _collection().get(include=["metadatas"])["metadatas"]:
        counts[m["source"]] = counts.get(m["source"], 0) + 1
    return [{"name": k, "chunks": v} for k, v in sorted(counts.items())]


def semantic_search(question: str, k: int = 3) -> list[dict]:
    """Embed the question and return the k nearest chunks (cosine distance)."""
    ensure_seeded()
    col = _collection()
    if col.count() == 0:
        return []
    res = col.query(query_embeddings=embeddings.embed([question]), n_results=min(k, col.count()))
    return [
        {"text": t, "source": m["source"], "chunk": m["chunk"],
         "distance": round(d, 4), "similarity": round(1 - d, 4)}
        for t, m, d in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


def keyword_search(question: str, k: int = 3) -> list[dict]:
    """Baseline for comparison: counts exact word matches only."""
    ensure_seeded()
    words = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if len(w) > 2}
    data = _collection().get(include=["documents", "metadatas"])
    scored = []
    for t, m in zip(data["documents"], data["metadatas"]):
        hits = words & set(re.findall(r"[a-z0-9]+", t.lower()))
        if hits:
            scored.append({"text": t, "source": m["source"], "chunk": m["chunk"],
                           "matches": sorted(hits), "score": len(hits)})
    return sorted(scored, key=lambda x: -x["score"])[:k]
