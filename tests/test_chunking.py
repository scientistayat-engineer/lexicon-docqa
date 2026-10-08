from app.services.chunking import chunk_text


def test_chunks_respect_size():
    text = ("Embeddings map text to vectors. " * 60).strip()
    chunks = chunk_text(text, size=200, overlap=30)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_empty_text():
    assert chunk_text("   ") == []
